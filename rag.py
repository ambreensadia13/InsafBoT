import hashlib
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_BASE_FOLDER = (
    BASE_DIR / "knowledge_base"
)

DB_FOLDER = (
    BASE_DIR / "chroma_db"
)


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
# LOAD EMBEDDING MODEL
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

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()


# ============================================================
# LOAD TXT DOCUMENTS
# ============================================================

def load_documents():

    if not KNOWLEDGE_BASE_FOLDER.exists():

        raise FileNotFoundError(
            "knowledge_base folder nahi mila."
        )

    txt_files = sorted(
        KNOWLEDGE_BASE_FOLDER.glob("*.txt")
    )

    if not txt_files:

        raise FileNotFoundError(
            "knowledge_base folder ke andar "
            "koi TXT file nahi mili."
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
            "Knowledge base mein readable "
            "text nahi mila."
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

    version_data = []

    for filepath in txt_files:

        content = filepath.read_bytes()

        file_hash = hashlib.md5(
            content
        ).hexdigest()

        version_data.append(
            f"{filepath.name}:{file_hash}"
        )

    combined = "|".join(
        version_data
    )

    return hashlib.md5(
        combined.encode("utf-8")
    ).hexdigest()


# ============================================================
# CHUNK DOCUMENTS
# ============================================================

def split_text_into_chunks(
    text,
    chunk_size=1000,
    overlap=200
):

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

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

            sentence_break = text.rfind(
                ". ",
                start,
                end
            )

            newline_break = text.rfind(
                "\n",
                start,
                end
            )

            best_break = max(
                sentence_break,
                newline_break
            )

            if best_break > start + 400:

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

        start = max(
            end - overlap,
            start + 1
        )

    return chunks


# ============================================================
# CHUNK DOCUMENTS
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
            chunk_size,
            overlap
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
# GET CHROMA CLIENT
# ============================================================

def get_chroma_client():

    return chromadb.PersistentClient(
        path=str(DB_FOLDER)
    )


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database():

    documents = load_documents()

    current_version = (
        get_knowledge_base_version()
    )

    chroma_client = get_chroma_client()

    rebuild_database = False

    try:

        collection = (
            chroma_client.get_collection(
                name=COLLECTION_NAME
            )
        )

        if collection.count() == 0:

            rebuild_database = True

        else:

            sample = collection.get(
                limit=1,
                include=["metadatas"]
            )

            existing_version = ""

            if (
                sample.get("metadatas")
                and len(sample["metadatas"]) > 0
            ):

                existing_version = (
                    sample["metadatas"][0].get(
                        "kb_version",
                        ""
                    )
                )

            if existing_version != current_version:

                rebuild_database = True

    except Exception:

        rebuild_database = True

        collection = None


    # --------------------------------------------------------
    # REBUILD DATABASE
    # --------------------------------------------------------

    if rebuild_database:

        try:

            chroma_client.delete_collection(
                name=COLLECTION_NAME
            )

        except Exception:

            pass

        collection = (
            chroma_client.create_collection(
                name=COLLECTION_NAME,
                metadata={
                    "hnsw:space": "cosine"
                }
            )
        )

        chunks = chunk_documents(
            documents
        )

        if not chunks:

            raise ValueError(
                "Knowledge base se koi "
                "text chunk create nahi hua."
            )

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = create_embeddings(
            texts
        )

        ids = []

        metadatas = []

        for index, chunk in enumerate(
            chunks
        ):

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
                    "chunk_number": (
                        chunk["chunk_number"]
                    ),
                    "kb_version": (
                        current_version
                    )
                }
            )

        # Add in batches
        batch_size = 100

        for start in range(
            0,
            len(texts),
            batch_size
        ):

            end = start + batch_size

            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=texts[start:end],
                metadatas=metadatas[start:end]
            )

    return collection


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
    # CREATE QUESTION EMBEDDING
    # --------------------------------------------------------

    question_embedding = create_embeddings(
        [question]
    )[0]


    # --------------------------------------------------------
    # SEARCH MORE RESULTS FIRST
    # --------------------------------------------------------

    total_documents = collection.count()

    search_count = min(
        max(top_k * 4, 10),
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


    # --------------------------------------------------------
    # FILTER AND REMOVE DUPLICATE SOURCES
    # --------------------------------------------------------

    filtered_documents = []

    filtered_metadatas = []

    filtered_distances = []

    source_counts = {}

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        source = metadata.get(
            "source",
            "Unknown"
        )

        # Cosine distance:
        # lower score = more relevant

        if distance > 0.90:

            continue

        # Maximum 2 chunks from one document

        if source_counts.get(
            source,
            0
        ) >= 2:

            continue

        source_counts[source] = (
            source_counts.get(
                source,
                0
            ) + 1
        )

        filtered_documents.append(
            document
        )

        filtered_metadatas.append(
            metadata
        )

        filtered_distances.append(
            distance
        )

        if len(
            filtered_documents
        ) >= top_k:

            break


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    # If threshold filtered everything,
    # return the best result only.

    if (
        not filtered_documents
        and documents
    ):

        filtered_documents.append(
            documents[0]
        )

        filtered_metadatas.append(
            metadatas[0]
        )

        filtered_distances.append(
            distances[0]
        )


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
