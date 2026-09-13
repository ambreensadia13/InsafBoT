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

COLLECTION_NAME = "insafbot_legal"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

_embedding_model = None


# ============================================================
# EMBEDDING MODEL
# ============================================================

def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    return _embedding_model


def create_embeddings(texts):
    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_documents():
    if not KNOWLEDGE_BASE_FOLDER.exists():
        raise FileNotFoundError(
            "The knowledge_base folder was not found."
        )

    txt_files = sorted(
        KNOWLEDGE_BASE_FOLDER.glob("*.txt")
    )

    if not txt_files:
        raise FileNotFoundError(
            "No .txt files were found inside the knowledge_base folder."
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

        text = normalize_text(text)

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": filepath.name,
            }
        )

    if not documents:
        raise ValueError(
            "All knowledge base files are empty."
        )

    return documents


# ============================================================
# KNOWLEDGE BASE VERSION
# ============================================================

def get_knowledge_base_version():
    if not KNOWLEDGE_BASE_FOLDER.exists():
        return ""

    files = sorted(
        KNOWLEDGE_BASE_FOLDER.glob("*.txt")
    )

    version_data = []

    for filepath in files:
        try:
            content = filepath.read_bytes()
        except Exception:
            content = b""

        file_hash = hashlib.md5(
            content
        ).hexdigest()

        version_data.append(
            f"{filepath.name}:{file_hash}"
        )

    combined = "|".join(version_data)

    return hashlib.md5(
        combined.encode("utf-8")
    ).hexdigest()


# ============================================================
# TEXT NORMALIZATION
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
# TEXT CHUNKING
# ============================================================

def split_text_into_chunks(
    text,
    chunk_size=1000,
    overlap=200,
):
    text = normalize_text(text)

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

        if end < len(text):
            sentence_breaks = [
                text.rfind(
                    ". ",
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
                ),
                text.rfind(
                    "۔ ",
                    start,
                    end
                ),
            ]

            paragraph_break = text.rfind(
                "\n\n",
                start,
                end
            )

            best_break = max(
                sentence_breaks + [paragraph_break]
            )

            if best_break > start + 350:
                end = best_break + 1

        chunk = text[
            start:end
        ].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def chunk_documents(
    documents,
    chunk_size=1000,
    overlap=200,
):
    chunks = []

    for document in documents:
        document_chunks = split_text_into_chunks(
            document["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for number, chunk_text in enumerate(
            document_chunks
        ):
            chunks.append(
                {
                    "text": chunk_text,
                    "source": document["source"],
                    "chunk_number": number,
                }
            )

    return chunks


# ============================================================
# CHROMA
# ============================================================

def get_chroma_client():
    DB_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    return chromadb.PersistentClient(
        path=str(DB_FOLDER)
    )


def delete_collection(client):
    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
    except Exception:
        pass


def create_collection(client):
    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database():
    documents = load_documents()

    current_version = (
        get_knowledge_base_version()
    )

    client = get_chroma_client()

    collection = None
    rebuild = False

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME
        )
    except Exception:
        rebuild = True

    # --------------------------------------------------------
    # CHECK EXISTING DATABASE
    # --------------------------------------------------------

    if collection is not None:
        try:
            count = collection.count()
        except Exception:
            count = 0

        if count == 0:
            rebuild = True
        else:
            try:
                sample = collection.get(
                    limit=1,
                    include=["metadatas"]
                )

                metadatas = sample.get(
                    "metadatas",
                    []
                )

                existing_version = ""

                if metadatas:
                    first_metadata = metadatas[0]

                    if isinstance(
                        first_metadata,
                        dict
                    ):
                        existing_version = (
                            first_metadata.get(
                                "kb_version",
                                ""
                            )
                        )

                if existing_version != current_version:
                    rebuild = True

            except Exception:
                rebuild = True

    # --------------------------------------------------------
    # REBUILD DATABASE
    # --------------------------------------------------------

    if rebuild:
        delete_collection(client)

        collection = create_collection(
            client
        )

        chunks = chunk_documents(
            documents,
            chunk_size=1000,
            overlap=200,
        )

        if not chunks:
            raise ValueError(
                "No chunks could be created from the knowledge base."
            )

        texts = [
            item["text"]
            for item in chunks
        ]

        embeddings = create_embeddings(
            texts
        )

        ids = []
        metadatas = []

        for item in chunks:
            unique_text = (
                f"{item['source']}_"
                f"{item['chunk_number']}_"
                f"{item['text']}"
            )

            chunk_id = hashlib.md5(
                unique_text.encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)

            metadatas.append(
                {
                    "source": item["source"],
                    "chunk_number": item[
                        "chunk_number"
                    ],
                    "kb_version": current_version,
                }
            )

        # ----------------------------------------------------
        # ADD IN BATCHES
        # ----------------------------------------------------

        batch_size = 100

        for start in range(
            0,
            len(texts),
            batch_size,
        ):
            end = min(
                start + batch_size,
                len(texts),
            )

            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=texts[start:end],
                metadatas=metadatas[start:end],
            )

    return collection


# ============================================================
# TOPIC DETECTION
# ============================================================

def detect_question_topics(question):
    q = question.lower()

    topics = []

    keywords = {
        "fir": [
            "fir",
            "f.i.r",
            "first information report",
            "register fir",
            "police report",
            "police station",
            "darj fir",
        ],

        "tenant": [
            "tenant",
            "landlord",
            "rent",
            "rented",
            "kiraya",
            "kirayedar",
            "makan malik",
        ],

        "labour": [
            "salary",
            "wage",
            "labour",
            "worker",
            "employee",
            "employer",
            "mazdoori",
            "tankhwa",
        ],

        "cheque": [
            "cheque",
            "check bounce",
            "cheque bounce",
            "dishonour",
            "bank cheque",
        ],

        "inheritance": [
            "inheritance",
            "will",
            "wills",
            "warasat",
            "wasiyat",
            "property inheritance",
        ],

        "domestic_violence": [
            "domestic violence",
            "violence against women",
            "wife abuse",
            "husband abuse",
            "ghar mein tashaddud",
        ],

        "khula": [
            "khula",
            "divorce",
            "talaq",
            "dissolution of marriage",
            "nikah",
        ],

        "cybercrime": [
            "cybercrime",
            "cyber crime",
            "online threat",
            "online harassment",
            "hacking",
            "facebook threat",
            "social media threat",
        ],

        "nadra": [
            "nadra",
            "cnic",
            "identity card",
            "b-form",
            "name correction",
            "date of birth correction",
        ],

        "property": [
            "property fraud",
            "land fraud",
            "property dispute",
            "land dispute",
            "zameen",
            "property",
        ],

        "traffic": [
            "traffic challan",
            "challan",
            "traffic fine",
            "driving license",
            "traffic violation",
        ],
    }

    for topic, words in keywords.items():
        for word in words:
            if word in q:
                topics.append(topic)
                break

    return topics


# ============================================================
# SOURCE TOPIC MATCHING
# ============================================================

def source_matches_topic(
    source,
    topics,
):
    if not topics:
        return False

    source_lower = source.lower()

    source_keywords = {
        "fir": [
            "fir",
            "police",
            "ppc",
        ],

        "tenant": [
            "tenant",
            "landlord",
            "rent",
        ],

        "labour": [
            "labour",
            "salary",
            "wage",
            "worker",
            "employment",
        ],

        "cheque": [
            "cheque",
            "check",
        ],

        "inheritance": [
            "inheritance",
            "will",
        ],

        "domestic_violence": [
            "domestic",
            "violence",
        ],

        "khula": [
            "khula",
            "divorce",
            "marriage",
            "nikah",
        ],

        "cybercrime": [
            "cyber",
            "crime",
        ],

        "nadra": [
            "nadra",
            "cnic",
        ],

        "property": [
            "property",
            "land",
        ],

        "traffic": [
            "traffic",
            "challan",
        ],
    }

    for topic in topics:
        words = source_keywords.get(
            topic,
            []
        )

        for word in words:
            if word in source_lower:
                return True

    return False


# ============================================================
# SEARCH
# ============================================================

def search_laws(
    collection,
    question,
    top_k=5,
):
    question = question.strip()

    if not question:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    embeddings = create_embeddings(
        [question]
    )

    if not embeddings:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    embedding = embeddings[0]

    try:
        total = collection.count()
    except Exception:
        total = 0

    if total == 0:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    topics = detect_question_topics(
        question
    )

    search_count = min(
        max(top_k * 10, 30),
        total,
    )

    results = collection.query(
        query_embeddings=[embedding],
        n_results=search_count,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get(
        "documents",
        [[]],
    )

    metadatas = results.get(
        "metadatas",
        [[]],
    )

    distances = results.get(
        "distances",
        [[]],
    )

    documents = (
        documents[0]
        if documents
        else []
    )

    metadatas = (
        metadatas[0]
        if metadatas
        else []
    )

    distances = (
        distances[0]
        if distances
        else []
    )

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if not document:
            continue

        if not isinstance(
            metadata,
            dict
        ):
            metadata = {}

        if distance is None:
            continue

        distance = float(distance)

        # ----------------------------------------------------
        # SEMANTIC RELEVANCE FILTER
        # ----------------------------------------------------

        if distance > 0.78:
            continue

        source = str(
            metadata.get(
                "source",
                "Unknown",
            )
        )

        topic_match = source_matches_topic(
            source,
            topics,
        )

        score = distance

        if topics and topic_match:
            score -= 0.12

        candidates.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "score": score,
                "topic_match": topic_match,
            }
        )

    candidates.sort(
        key=lambda item: item["score"]
    )

    # ========================================================
    # ORDER RESULTS
    # ========================================================

    if topics:
        topic_candidates = [
            item
            for item in candidates
            if item["topic_match"]
        ]

        other_candidates = [
            item
            for item in candidates
            if not item["topic_match"]
        ]

        ordered = (
            topic_candidates
            + other_candidates
        )
    else:
        ordered = candidates

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    final_documents = []
    final_metadatas = []
    final_distances = []

    source_counts = {}

    for candidate in ordered:
        metadata = candidate["metadata"]

        source = str(
            metadata.get(
                "source",
                "Unknown",
            )
        )

        if topics:
            if (
                not candidate["topic_match"]
                and candidate["distance"] > 0.68
            ):
                continue

        count = source_counts.get(
            source,
            0
        )

        # Maximum two chunks per source.
        if count >= 2:
            continue

        source_counts[source] = count + 1

        final_documents.append(
            candidate["document"]
        )

        final_metadatas.append(
            metadata
        )

        final_distances.append(
            candidate["distance"]
        )

        if len(final_documents) >= top_k:
            break

    return {
        "documents": [
            final_documents
        ],
        "metadatas": [
            final_metadatas
        ],
        "distances": [
            final_distances
        ],
    }
