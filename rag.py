import os
import hashlib

import chromadb
from pypdf import PdfReader
from google import genai


LAWS_FOLDER = "laws"
DB_FOLDER = "chroma_db"
COLLECTION_NAME = "pakistan_laws"


def get_client(api_key):
    return genai.Client(api_key=api_key)


def load_documents():
    documents = []

    for filename in sorted(os.listdir(LAWS_FOLDER)):

        if not filename.lower().endswith(".pdf"):
            continue

        filepath = os.path.join(LAWS_FOLDER, filename)

        reader = PdfReader(filepath)

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text()

            if not text:
                continue

            text = text.strip()

            if not text:
                continue

            documents.append({
                "text": text,
                "source": filename,
                "page": page_number
            })

    return documents


def chunk_documents(documents, chunk_size=1200, overlap=200):

    chunks = []

    for document in documents:

        text = document["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "text": chunk_text,
                    "source": document["source"],
                    "page": document["page"]
                })

            start += chunk_size - overlap

    return chunks


def create_embedding(client, text):

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return result.embeddings[0].values


def get_collection():

    chroma_client = chromadb.PersistentClient(
        path=DB_FOLDER
    )

    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )


def build_database(client):

    documents = load_documents()

    chunks = chunk_documents(documents)

    collection = get_collection()

    existing = collection.count()

    if existing > 0:
        return collection

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(
            client,
            chunk["text"]
        )

        chunk_id = hashlib.md5(
            f"{chunk['source']}_{chunk['page']}_{index}".encode()
        ).hexdigest()

        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[{
                "source": chunk["source"],
                "page": chunk["page"]
            }]
        )

    return collection


def search_laws(client, collection, question, top_k=5):

    question_embedding = create_embedding(
        client,
        question
    )

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results
