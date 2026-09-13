import hashlib
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_BASE_FOLDER = BASE_DIR / "knowledge_base"

DB_FOLDER = BASE_DIR / "chroma_db"


# ============================================================
# CHROMA SETTINGS
# ============================================================

COLLECTION_NAME = "insafbot_legal"


# ============================================================
# EMBEDDING MODEL
# ============================================================

EMBEDDING_MODEL = (
    "paraphrase-multilingual-MiniLM-L12-v2"
)

_embedding_model = None


# ============================================================
# EMBEDDING MODEL LOADER
# ============================================================

def get_embedding_model():

    global _embedding_model

    if _embedding_model is None:

        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _embedding_model


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(texts):

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()


# ============================================================
# LOAD KNOWLEDGE BASE DOCUMENTS
# ============================================================

def load_documents():

    if not KNOWLEDGE_BASE_FOLDER.exists():

        raise FileNotFoundError(
            "knowledge_base folder nahi mila. "
            "Make sure the knowledge_base folder "
            "app.py aur rag.py ke same project folder mein hai."
        )

    txt_files = sorted(
        KNOWLEDGE_BASE_FOLDER.glob("*.txt")
    )

    if not txt_files:

        raise FileNotFoundError(
            "knowledge_base folder ke andar "
            "koi .txt file nahi mili."
        )

    documents = []

    for filepath in txt_files:

        try:

            text = filepath.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            text = filepath.read_text(
                encoding="utf-8-sig"
            )

        text = text.strip()

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": filepath.name,
                "page": "N/A"
            }
        )

    if not documents:

        raise ValueError(
            "TXT files mili hain lekin un mein "
            "readable text nahi hai."
        )

    return documents


# ============================================================
# KNOWLEDGE BASE VERSION
# ============================================================

def get_knowledge_base_version():

    if not KNOWLEDGE_BASE_FOLDER.exists():
        return ""

    txt_files = sorted(
        KNOWLEDGE_BASE_FOLDER.glob("*.txt")
    )

    version_parts = []

    for filepath in txt_files:

        try:

            content = filepath.read_bytes()

        except Exception:

            content = b""

        file_hash = hashlib.md5(
            content
        ).hexdigest()

        version_parts.append(
            f"{filepath.name}:{file_hash}"
        )

    combined = "|".join(
        version_parts
    )

    return hashlib.md5(
        combined.encode("utf-8")
    ).hexdigest()


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# SPLIT DOCUMENT INTO CHUNKS
# ============================================================

def split_text_into_chunks(
    text,
    chunk_size=1000,
    overlap=200
):

    text = normalize_text(
        text
    )

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text)
        )

        # ----------------------------------------------------
        # Try to stop at a natural sentence boundary
        # ----------------------------------------------------

        if end < len(text):

            sentence_break = max(
                text.rfind(
                    ". ",
                    start,
                    end
                ),

                text.rfind(
                    "۔ ",
                    start,
                    end
                ),

                text.rfind(
                    "? ",
                    start,
                    end
                ),

                text.rfind(
                    "! ",
                    start,
                    end
                )
            )

            paragraph_break = text.rfind(
                "\n\n",
                start,
                end
            )

            best_break = max(
                sentence_break,
                paragraph_break
            )

            if best_break > start + 350:

                end = best_break + 1

        chunk = text[
            start:end
        ].strip()

        if chunk:

            chunks.append(
                chunk
            )

        if end >= len(text):
            break

        next_start = end - overlap

        if next_start <= start:

            next_start = end

        start = next_start

    return chunks


# ============================================================
# CHUNK ALL DOCUMENTS
# ============================================================

def chunk_documents(
    documents,
    chunk_size=1000,
    overlap=200
):

    chunks = []

    for document in documents:

        document_chunks = split_text_into_chunks(
            document["text"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        for chunk_number, chunk_text in enumerate(
            document_chunks
        ):

            chunks.append(
                {
                    "text": chunk_text,
                    "source": document["source"],
                    "page": document["page"],
                    "chunk_number": chunk_number
                }
            )

    return chunks


# ============================================================
# CHROMA CLIENT
# ============================================================

def get_chroma_client():

    DB_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    return chromadb.PersistentClient(
        path=str(DB_FOLDER)
    )


# ============================================================
# DELETE OLD COLLECTION
# ============================================================

def delete_old_collection(
    chroma_client
):

    try:

        chroma_client.delete_collection(
            name=COLLECTION_NAME
        )

    except Exception:

        pass


# ============================================================
# CREATE NEW COLLECTION
# ============================================================

def create_collection(
    chroma_client
):

    return chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database():

    # --------------------------------------------------------
    # Load documents
    # --------------------------------------------------------

    documents = load_documents()

    # --------------------------------------------------------
    # Calculate current KB version
    # --------------------------------------------------------

    current_version = (
        get_knowledge_base_version()
    )

    # --------------------------------------------------------
    # Chroma client
    # --------------------------------------------------------

    chroma_client = get_chroma_client()

    collection = None

    rebuild_database = False

    # --------------------------------------------------------
    # Try to load existing collection
    # --------------------------------------------------------

    try:

        collection = (
            chroma_client.get_collection(
                name=COLLECTION_NAME
            )
        )

    except Exception:

        rebuild_database = True

    # --------------------------------------------------------
    # Check existing database
    # --------------------------------------------------------

    if collection is not None:

        try:

            collection_count = (
                collection.count()
            )

        except Exception:

            collection_count = 0

        if collection_count == 0:

            rebuild_database = True

        else:

            try:

                sample = collection.get(
                    limit=1,
                    include=[
                        "metadatas"
                    ]
                )

                existing_version = ""

                sample_metadatas = (
                    sample.get(
                        "metadatas",
                        []
                    )
                )

                if sample_metadatas:

                    existing_version = (
                        sample_metadatas[0].get(
                            "kb_version",
                            ""
                        )
                    )

                if (
                    existing_version
                    != current_version
                ):

                    rebuild_database = True

            except Exception:

                rebuild_database = True

    # ========================================================
    # REBUILD DATABASE
    # ========================================================

    if rebuild_database:

        delete_old_collection(
            chroma_client
        )

        collection = create_collection(
            chroma_client
        )

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        chunks = chunk_documents(
            documents,
            chunk_size=1000,
            overlap=200
        )

        if not chunks:

            raise ValueError(
                "Knowledge base se koi text chunk "
                "create nahi hua."
            )

        # ----------------------------------------------------
        # Texts
        # ----------------------------------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        # ----------------------------------------------------
        # Embeddings
        # ----------------------------------------------------

        embeddings = create_embeddings(
            texts
        )

        # ----------------------------------------------------
        # IDs and metadata
        # ----------------------------------------------------

        ids = []

        metadatas = []

        for chunk in chunks:

            unique_text = (
                f"{chunk['source']}_"
                f"{chunk['chunk_number']}_"
                f"{chunk['text']}"
            )

            chunk_id = hashlib.md5(
                unique_text.encode(
                    "utf-8"
                )
            ).hexdigest()

            ids.append(
                chunk_id
            )

            metadatas.append(
                {
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk_number": chunk[
                        "chunk_number"
                    ],
                    "kb_version": current_version
                }
            )

        # ----------------------------------------------------
        # Add data in batches
        # ----------------------------------------------------

        batch_size = 100

        for start in range(
            0,
            len(texts),
            batch_size
        ):

            end = min(
                start + batch_size,
                len(texts)
            )

            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[
                    start:end
                ],
                documents=texts[
                    start:end
                ],
                metadatas=metadatas[
                    start:end
                ]
            )

    return collection


# ============================================================
# QUESTION TOPIC DETECTION
# ============================================================

def detect_question_topics(question):

    question_lower = question.lower()

    topics = []

    topic_keywords = {

        "fir": [
            "fir",
            "first information report",
            "police report",
            "police station",
            "register fir",
            "darj fir",
            "f.i.r"
        ],

        "tenant": [
            "tenant",
            "rent",
            "rented",
            "landlord",
            "kiraya",
            "makan malik",
            "kirayedar"
        ],

        "labour": [
            "salary",
            "wage",
            "labour",
            "worker",
            "employee",
            "employer",
            "mazdoori",
            "tankhwa"
        ],

        "cheque": [
            "cheque",
            "check bounce",
            "cheque bounce",
            "dishonour",
            "bank cheque"
        ],

        "inheritance": [
            "inheritance",
            "will",
            "wills",
            "property inheritance",
            "warasat",
            "wasiyat"
        ],

        "domestic_violence": [
            "domestic violence",
            "violence against women",
            "wife abuse",
            "husband abuse",
            "ghar mein tashaddud"
        ],

        "khula": [
            "khula",
            "khula procedure",
            "divorce",
            "talaq",
            "dissolution of marriage",
            "nikah"
        ],

        "cybercrime": [
            "cybercrime",
            "cyber crime",
            "online threat",
            "online harassment",
            "hacking",
            "facebook threat",
            "social media threat"
        ],

        "nadra": [
            "nadra",
            "cnic",
            "identity card",
            "b-form",
            "name correction",
            "date of birth correction"
        ],

        "property": [
            "property fraud",
            "land fraud",
            "property dispute",
            "land dispute",
            "zameen",
            "property"
        ],

        "traffic": [
            "traffic challan",
            "challan",
            "traffic fine",
            "driving license",
            "traffic violation"
        ]
    }

    for topic, keywords in topic_keywords.items():

        for keyword in keywords:

            if keyword in question_lower:

                topics.append(topic)

                break

    return topics


# ============================================================
# SOURCE TOPIC MATCHING
# ============================================================

def source_matches_topic(
    source,
    topics
):

    if not topics:
        return False

    source_lower = source.lower()

    topic_source_keywords = {

        "fir": [
            "fir",
            "ppc",
            "police"
        ],

        "tenant": [
            "tenant",
            "landlord",
            "rent"
        ],

        "labour": [
            "labour",
            "salary",
            "wage",
            "worker"
        ],

        "cheque": [
            "cheque",
            "check"
        ],

        "inheritance": [
            "inheritance",
            "will"
        ],

        "domestic_violence": [
            "domestic",
            "violence"
        ],

        "khula": [
            "khula",
            "divorce",
            "marriage",
            "nikah"
        ],

        "cybercrime": [
            "cyber",
            "crime"
        ],

        "nadra": [
            "nadra",
            "cnic"
        ],

        "property": [
            "property",
            "land"
        ],

        "traffic": [
            "traffic",
            "challan"
        ]
    }

    for topic in topics:

        keywords = topic_source_keywords.get(
            topic,
            []
        )

        for keyword in keywords:

            if keyword in source_lower:

                return True

    return False


# ============================================================
# SEARCH LEGAL DOCUMENTS
# ============================================================

def search_laws(
    collection,
    question,
    top_k=5
):

    question = question.strip()

    if not question:

        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    # --------------------------------------------------------
    # Create question embedding
    # --------------------------------------------------------

    question_embedding = create_embeddings(
        [question]
    )[0]

    # --------------------------------------------------------
    # Check database
    # --------------------------------------------------------

    try:

        total_documents = (
            collection.count()
        )

    except Exception:

        total_documents = 0

    if total_documents == 0:

        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    # --------------------------------------------------------
    # Detect topic
    # --------------------------------------------------------

    topics = detect_question_topics(
        question
    )

    # --------------------------------------------------------
    # Retrieve larger candidate pool
    # --------------------------------------------------------

    search_count = min(
        max(top_k * 10, 30),
        total_documents
    )

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=search_count,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    # ========================================================
    # PREPARE CANDIDATES
    # ========================================================

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if not document:
            continue

        if not metadata:
            metadata = {}

        if distance is None:
            continue

        source = metadata.get(
            "source",
            "Unknown"
        )

        # ----------------------------------------------------
        # Strict semantic threshold
        # ----------------------------------------------------

        if distance > 0.78:
            continue

        # ----------------------------------------------------
        # Topic/source matching
        # ----------------------------------------------------

        topic_match = source_matches_topic(
            source,
            topics
        )

        # ----------------------------------------------------
        # Score
        #
        # Lower distance = better.
        # Topic match receives strong preference.
        # ----------------------------------------------------

        score = float(distance)

        if topics and topic_match:

            score -= 0.12

        candidates.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": float(distance),
                "score": score,
                "topic_match": topic_match
            }
        )

    # ========================================================
    # SORT CANDIDATES
    # ========================================================

    candidates.sort(
        key=lambda item: item["score"]
    )

    # ========================================================
    # SELECT RESULTS
    # ========================================================

    filtered_documents = []

    filtered_metadatas = []

    filtered_distances = []

    source_counts = {}

    # --------------------------------------------------------
    # First prefer topic-matching sources
    # --------------------------------------------------------

    if topics:

        topic_candidates = [
            candidate
            for candidate in candidates
            if candidate["topic_match"]
        ]

        other_candidates = [
            candidate
            for candidate in candidates
            if not candidate["topic_match"]
        ]

        ordered_candidates = (
            topic_candidates
            + other_candidates
        )

    else:

        ordered_candidates = candidates

    # ========================================================
    # ADD RELEVANT RESULTS
    # ========================================================

    for candidate in ordered_candidates:

        source = candidate[
            "metadata"
        ].get(
            "source",
            "Unknown"
        )

        # ----------------------------------------------------
        # If a topic was detected, don't allow weak
        # unrelated documents to enter just to fill top_k.
        # ----------------------------------------------------

        if topics:

            if (
                not candidate["topic_match"]
                and candidate["distance"] > 0.68
            ):
                continue

        # ----------------------------------------------------
        # Maximum 2 chunks per source
        # ----------------------------------------------------

        current_count = source_counts.get(
            source,
            0
        )

        if current_count >= 2:
            continue

        source_counts[source] = (
            current_count + 1
        )

        filtered_documents.append(
            candidate["document"]
        )

        filtered_metadatas.append(
            candidate["metadata"]
        )

        filtered_distances.append(
            candidate["distance"]
        )

        if len(
            filtered_documents
        ) >= top_k:

            break

    # ========================================================
    # NO FALLBACK
    # ========================================================
    #
    # Important:
    # We intentionally do NOT return a random
    # document when nothing relevant is found.
    #
    # ========================================================

    return {
        "documents": [
            filtered_documents
        ],

        "metadatas": [
            filtered_metadatas
        ],

        "distances": [
            filtered_distances
        ]
    }
