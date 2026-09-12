import os
import hashlib

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ============================================================
# SETTINGS
# ============================================================

LAWS_FOLDER = "laws"
DB_FOLDER = "chroma_db"
COLLECTION_NAME = "pakistan_laws"

# Multilingual local embedding model.
# It works much better for English + Urdu/Roman Urdu
# than an English-only embedding model.
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# ============================================================
# LOCAL EMBEDDING MODEL
# ============================================================

_embedding_model = None


def get_embedding_model():

    global _embedding_model

    if _embedding_model is None:

        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _embedding_model


def create_embeddings(texts):

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()


# ============================================================
# LOAD PDF DOCUMENTS
# ============================================================

def load_documents():

    documents = []

    if not os.path.isdir(LAWS_FOLDER):

        raise FileNotFoundError(
            "The 'laws' folder was not found. "
            "Make sure your 7 PDF files are inside the laws/ folder."
        )

    pdf_files = sorted(
        filename
        for filename in os.listdir(LAWS_FOLDER)
        if filename.lower().endswith(".pdf")
    )

    if not pdf_files:

        raise FileNotFoundError(
            "No PDF files were found inside the laws/ folder."
        )

    for filename in pdf_files:

        filepath = os.path.join(
            LAWS_FOLDER,
            filename
        )

        reader = PdfReader(filepath)

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if not text:
                continue

            text = text.strip()

            if not text:
                continue

            documents.append(
                {
                    "text": text,
                    "source": filename,
                    "page": page_number
                }
            )

    if not documents:

        raise ValueError(
            "The PDF files were found, but no readable text "
            "could be extracted from them."
        )

    return documents


# ============================================================
# CHUNK LEGAL DOCUMENTS
# ============================================================

def chunk_documents(
    documents,
    chunk_size=1500,
    overlap=250
):

    chunks = []

    for document in documents:

        text = document["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

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
# CHROMADB
# ============================================================

def get_collection():

    chroma_client = chromadb.PersistentClient(
        path=DB_FOLDER
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database():

    collection = get_collection()

    # If database already contains documents,
    # don't rebuild it.
    if collection.count() > 0:

        return collection

    documents = load_documents()

    chunks = chunk_documents(documents)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # IMPORTANT:
    # Embeddings are created locally.
    # No Gemini embedding API is used here.
    embeddings = create_embeddings(texts)

    ids = []

    metadatas = []

    for index, chunk in enumerate(chunks):

        chunk_id = hashlib.md5(
            f"{chunk['source']}_{chunk['page']}_{index}".encode(
                "utf-8"
            )
        ).hexdigest()

        ids.append(chunk_id)

        metadatas.append(
            {
                "source": chunk["source"],
                "page": chunk["page"]
            }
        )

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

    question_embedding = create_embeddings(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results
