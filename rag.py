import os
import hashlib
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_BASE_FOLDER = BASE_DIR / "knowledge_base"
DB_FOLDER = BASE_DIR / "chroma_db"

COLLECTION_NAME = "insafbot_legal"

# Multilingual model:
# English + Urdu + Roman Urdu ke liye suitable
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# ============================================================
# EMBEDDING MODEL
# ============================================================

_embedding_model = None


def get_embedding_model():
    """
    Load the Sentence Transformer model only once.
    """

    global _embedding_model

    if _embedding_model is None:

        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _embedding_model


def create_embeddings(texts):
    """
    Create local embeddings for given texts.
    """

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()


# ============================================================
# LOAD TXT LEGAL DOCUMENTS
# ============================================================

def load_documents():
    """
    Read all TXT files from knowledge_base folder.
    """

    if not KNOWLEDGE_BASE_FOLDER.exists():

        raise FileNotFoundError(
            "knowledge_base folder nahi mila. "
            "Make sure all 25 TXT files knowledge_base folder "
            "ke andar hain."
        )

    txt_files = sorted(
        KNOWLEDGE_BASE_FOLDER.glob("*.txt")
    )

    if not txt_files:

        raise FileNotFoundError(
            "knowledge_base folder ke andar koi TXT file nahi mili."
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
            "TXT files mili hain lekin un mein readable text nahi hai."
        )

    return documents


# ============================================================
# CHUNK DOCUMENTS
# ============================================================

def chunk_documents(
    documents,
    chunk_size=1200,
    overlap=200
):
    """
    Break large legal documents into smaller chunks.
    """

    chunks = []

    for document in documents:

        text = document["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[
                start:end
            ].strip()

            if chunk_text:

                chunks.append(
                    {
                        "text": chunk_text,
                        "source": document["source"],
                        "page": document["page"]
                    }
                )

            start += chunk_size - overlap

    return chunks


# ============================================================
# CHROMADB COLLECTION
# ============================================================

def get_collection():

    chroma_client = chromadb.PersistentClient(
        path=str(DB_FOLDER)
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database():
    """
    Build the ChromaDB knowledge base from TXT files.

    If database already contains documents,
    existing collection is reused.
    """

    collection = get_collection()

    # Existing database
    if collection.count() > 0:

        return collection

    # Load TXT files
    documents = load_documents()

    # Create chunks
    chunks = chunk_documents(
        documents
    )

    if not chunks:

        raise ValueError(
            "Knowledge base se koi text chunk create nahi hua."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # Create embeddings locally
    embeddings = create_embeddings(
        texts
    )

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        unique_text = (
            f"{chunk['source']}_"
            f"{index}_"
            f"{chunk['text']}"
        )

        chunk_id = hashlib.md5(
            unique_text.encode("utf-8")
        ).hexdigest()

        ids.append(
            chunk_id
        )

        metadatas.append(
            {
                "source": chunk["source"],
                "page": chunk["page"]
            }
        )

    # Add to ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
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
    """
    Search the legal knowledge base
    using semantic similarity.
    """

    question = question.strip()

    if not question:

        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    question_embedding = create_embeddings(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=top_k
    )

    return results
