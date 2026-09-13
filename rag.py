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
            "knowledge_base folder nahi mila. "
            "Make sure the folder exists in the "
            "same directory as app.py."
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
# SPLIT TEXT INTO CHUNKS
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
        # Try to end chunk at a natural boundary
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


        next_start = end - overlap


        if next_start <= start:

            next_start = end


        start = next_start


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

        document_chunks = (
            split_text_into_chunks(
                document["text"],
                chunk_size=chunk_size,
                overlap=overlap
            )
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
# CREATE COLLECTION
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
    # Load current knowledge base
    # --------------------------------------------------------

    documents = load_documents()


    # --------------------------------------------------------
    # Current KB version
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
    # Check existing collection
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
    # If collection exists, check version
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
                        sample_metadatas[0]
                        .get(
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
                "Knowledge base se koi text "
                "chunk create nahi hua."
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

                embeddings=(
                    embeddings[start:end]
                ),

                documents=(
                    texts[start:end]
                ),

                metadatas=(
                    metadatas[start:end]
                )
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
    # Question embedding
    # --------------------------------------------------------

    question_embedding = create_embeddings(
        [question]
    )[0]


    # --------------------------------------------------------
    # Number of documents
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
    # Retrieve more candidates
    # --------------------------------------------------------

    search_count = min(
        max(
            top_k * 5,
            10
        ),
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
    # FILTER RESULTS
    # ========================================================

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


        # ----------------------------------------------------
        # Relevance threshold
        # ----------------------------------------------------

        if distance > 0.90:

            continue


        # ----------------------------------------------------
        # Maximum 2 chunks per source
        # ----------------------------------------------------

        current_count = (
            source_counts.get(
                source,
                0
            )
        )


        if current_count >= 2:

            continue


        source_counts[source] = (
            current_count + 1
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


    # ========================================================
    # FALLBACK
    # ========================================================

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


    # ========================================================
    # RETURN
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
