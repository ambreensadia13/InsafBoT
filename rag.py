import os
import re
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_BASE_DIR = "knowledge_base"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "insafbot_legal"

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

# Minimum semantic similarity
SIMILARITY_THRESHOLD = 0.45


# ============================================================
# EMBEDDING MODEL
# ============================================================

_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    return _embedding_model


# ============================================================
# CHROMA CLIENT
# ============================================================

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


# ============================================================
# FILE HASH
# ============================================================

def get_knowledge_base_hash():
    """
    Creates a hash from all TXT files.

    If any TXT file changes, the database is rebuilt.
    """

    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        return ""

    files = []

    for root, _, filenames in os.walk(KNOWLEDGE_BASE_DIR):
        for filename in filenames:
            if filename.lower().endswith(".txt"):
                files.append(os.path.join(root, filename))

    files.sort()

    hasher = hashlib.sha256()

    for filepath in files:

        hasher.update(filepath.encode("utf-8"))

        try:
            with open(filepath, "rb") as f:
                hasher.update(f.read())
        except Exception:
            continue

    return hasher.hexdigest()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# LAW REFERENCE EXTRACTION
# ============================================================

def extract_law_reference(text):
    """
    Attempts to extract an actual law/section/article/rule
    reference from the source text.

    It does NOT invent a law if one is not present.
    """

    if not text:
        return "Not specified in source document"

    text = normalize_text(text)

    # --------------------------------------------------------
    # Section references
    # --------------------------------------------------------

    patterns = [
        r"\bSections?\s+\d+[A-Za-z]?(?:\s*(?:to|-)\s*\d+[A-Za-z]?)?",
        r"\bsection\s+\d+[A-Za-z]?(?:\s*(?:to|-)\s*\d+[A-Za-z]?)?",
        r"\bS\.\s*\d+[A-Za-z]?",
        r"\bSs\.\s*\d+[A-Za-z]?(?:\s*(?:to|-)\s*\d+[A-Za-z]?)?",
        r"\bu/s\s+\d+[A-Za-z]?",
        r"\bunder\s+section\s+\d+[A-Za-z]?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            reference = match.group(0).strip()

            # Find nearby law name
            start = max(0, match.start() - 250)
            nearby = text[start:match.end() + 150]

            law_patterns = [
                r"(Pakistan Penal Code(?:,\s*\d{4})?)",
                r"(Code of Criminal Procedure(?:,\s*\d{4})?)",
                r"(Code of Civil Procedure(?:,\s*\d{4})?)",
                r"(Qanun-e-Shahadat Order(?:,\s*\d{4})?)",
                r"(Family Courts Act(?:,\s*\d{4})?)",
                r"(Muslim Family Laws Ordinance(?:,\s*\d{4})?)",
                r"(Protection of Women Against Harassment at the Workplace Act(?:,\s*\d{4})?)",
                r"(Prevention of Electronic Crimes Act(?:,\s*\d{4})?)",
                r"(Cyber Crime.*?Act(?:,\s*\d{4})?)",
                r"(Child Marriage Restraint Act(?:,\s*\d{4})?)",
                r"(Guardians and Wards Act(?:,\s*\d{4})?)",
                r"(Dissolution of Muslim Marriages Act(?:,\s*\d{4})?)",
                r"(Constitution of the Islamic Republic of Pakistan)",
            ]

            for law_pattern in law_patterns:
                law_match = re.search(
                    law_pattern,
                    nearby,
                    re.IGNORECASE
                )

                if law_match:
                    return f"{law_match.group(1)}, {reference}"

            return reference

    # --------------------------------------------------------
    # Article references
    # --------------------------------------------------------

    article_match = re.search(
        r"\bArticles?\s+\d+[A-Za-z]?(?:\s*(?:to|-)\s*\d+[A-Za-z]?)?",
        text,
        re.IGNORECASE
    )

    if article_match:
        reference = article_match.group(0).strip()

        nearby = text[
            max(0, article_match.start() - 250):
            article_match.end() + 150
        ]

        if re.search(
            r"Constitution of the Islamic Republic of Pakistan",
            nearby,
            re.IGNORECASE
        ):
            return (
                "Constitution of the Islamic Republic of Pakistan, "
                + reference
            )

        return reference

    # --------------------------------------------------------
    # Rule references
    # --------------------------------------------------------

    rule_match = re.search(
        r"\bRules?\s+\d+[A-Za-z]?(?:\s*(?:to|-)\s*\d+[A-Za-z]?)?",
        text,
        re.IGNORECASE
    )

    if rule_match:
        return rule_match.group(0).strip()

    # --------------------------------------------------------
    # Named Acts / Ordinances
    # --------------------------------------------------------

    named_law_patterns = [
        r"\b[A-Z][A-Za-z\s-]{3,80}\sAct(?:,\s*\d{4})?",
        r"\b[A-Z][A-Za-z\s-]{3,80}\sOrdinance(?:,\s*\d{4})?",
        r"\b[A-Z][A-Za-z\s-]{3,80}\sCode(?:,\s*\d{4})?",
        r"\bPakistan Penal Code(?:,\s*\d{4})?",
        r"\bCode of Criminal Procedure(?:,\s*\d{4})?",
        r"\bCode of Civil Procedure(?:,\s*\d{4})?",
    ]

    for pattern in named_law_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            candidate = match.group(0).strip()

            # Avoid returning excessively long accidental matches
            if len(candidate) <= 120:
                return candidate

    return "Not specified in source document"


# ============================================================
# CHUNKING
# ============================================================

def create_chunks(text):
    """
    Creates overlapping chunks while attempting to preserve
    paragraph boundaries.
    """

    text = normalize_text(text)

    if not text:
        return []

    paragraphs = text.split("\n\n")

    chunks = []
    current = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current) + len(paragraph) + 2 <= CHUNK_SIZE:

            if current:
                current += "\n\n" + paragraph
            else:
                current = paragraph

        else:

            if current:
                chunks.append(current)

            overlap = current[-CHUNK_OVERLAP:] if current else ""

            current = overlap + "\n\n" + paragraph

    if current:
        chunks.append(current)

    return chunks


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database(force_rebuild=False):

    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        raise FileNotFoundError(
            f"Knowledge base folder '{KNOWLEDGE_BASE_DIR}' was not found."
        )

    client = get_chroma_client()

    # --------------------------------------------------------
    # Current KB hash
    # --------------------------------------------------------

    current_hash = get_knowledge_base_hash()

    # --------------------------------------------------------
    # Existing collection
    # --------------------------------------------------------

    try:
        collection = client.get_collection(COLLECTION_NAME)

        existing_metadata = collection.get(
            limit=1,
            include=["metadatas"]
        )

        metadata = existing_metadata.get("metadatas", [])

        stored_hash = None

        if metadata:
            stored_hash = metadata[0].get("kb_hash")

        # Check if database is valid
        if (
            not force_rebuild
            and stored_hash == current_hash
            and metadata
            and "law_reference" in metadata[0]
        ):
            return collection

        # Old/outdated database
        client.delete_collection(COLLECTION_NAME)

    except Exception:
        pass

    # --------------------------------------------------------
    # Create new collection
    # --------------------------------------------------------

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "INSAFBOT Pakistani legal knowledge base",
            "kb_hash": current_hash
        }
    )

    documents = []
    metadatas = []
    ids = []

    # --------------------------------------------------------
    # Read TXT files
    # --------------------------------------------------------

    txt_files = []

    for root, _, filenames in os.walk(KNOWLEDGE_BASE_DIR):

        for filename in filenames:

            if filename.lower().endswith(".txt"):

                txt_files.append(
                    os.path.join(root, filename)
                )

    txt_files.sort()

    if not txt_files:
        raise ValueError(
            "No .txt files were found inside knowledge_base."
        )

    # --------------------------------------------------------
    # Process files
    # --------------------------------------------------------

    counter = 0

    for filepath in txt_files:

        filename = os.path.basename(filepath)

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                text = f.read()

        except Exception:
            continue

        text = normalize_text(text)

        if not text:
            continue

        chunks = create_chunks(text)

        for chunk_index, chunk in enumerate(chunks):

            law_reference = extract_law_reference(chunk)

            doc_id = (
                f"{filename}_{chunk_index}_{counter}"
            )

            documents.append(chunk)

            metadatas.append({
                "source": filename,
                "law_reference": law_reference,
                "chunk_index": chunk_index,
                "kb_hash": current_hash
            })

            ids.append(doc_id)

            counter += 1

    if not documents:
        raise ValueError(
            "The knowledge base contains no readable text."
        )

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    model = get_embedding_model()

    embeddings = model.encode(
        documents,
        show_progress_bar=False,
        normalize_embeddings=True
    )

    embeddings = embeddings.tolist()

    # --------------------------------------------------------
    # Store in Chroma
    # --------------------------------------------------------

    batch_size = 100

    for start in range(0, len(documents), batch_size):

        end = start + batch_size

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end]
        )

    return collection


# ============================================================
# SEARCH
# ============================================================

def search_laws(
    collection,
    query,
    top_k=5
):

    if not query or not query.strip():
        return []

    model = get_embedding_model()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=max(top_k * 3, 10),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output = []

    seen = set()
    source_count = {}

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Chroma cosine distance -> approximate similarity
        similarity = 1 - float(distance)

        if similarity < SIMILARITY_THRESHOLD:
            continue

        metadata = metadata or {}

        source = metadata.get(
            "source",
            "Unknown source"
        )

        # Prevent too many chunks from same document
        source_count[source] = source_count.get(source, 0)

        if source_count[source] >= 2:
            continue

        # Avoid duplicate chunks
        key = (
            source,
            document[:200]
        )

        if key in seen:
            continue

        seen.add(key)

        # Use stored law reference.
        # If old metadata somehow lacks it, extract it now.
        law_reference = metadata.get(
            "law_reference"
        )

        if not law_reference:
            law_reference = extract_law_reference(
                document
            )

        output.append({
            "text": document,
            "source": source,
            "law_reference": law_reference,
            "similarity": similarity
        })

        source_count[source] += 1

        if len(output) >= top_k:
            break

    return output
