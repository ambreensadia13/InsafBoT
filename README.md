<h1 align="center">INSAFBOT</h1>

<p align="center">
<b>AI-Powered Legal Information Assistant for Pakistan</b>
</p>

<p align="center">
Retrieval-Augmented Generation (RAG) application for providing
grounded legal information from a local Pakistani legal knowledge base.
</p>

<p align="center">
<img src="https://img.shields.io/badge/Framework-Streamlit-red">
<img src="https://img.shields.io/badge/AI-Grok-blue">
<img src="https://img.shields.io/badge/RAG-ChromaDB-green">
<img src="https://img.shields.io/badge/Language-English%20%7C%20Urdu%20%7C%20Roman%20Urdu-orange">
</p>

---

## About

INSAFBOT is an AI-powered legal information assistant that helps users understand Pakistani legal topics in simple language.

The application uses **RAG, ChromaDB, Sentence Transformers, and Grok by xAI** to retrieve relevant legal information before generating a response.

Users can ask questions in **English, Urdu, or Roman Urdu**.

## Features

* AI-powered legal question answering
* Retrieval-Augmented Generation (RAG)
* Semantic search using ChromaDB
* Multilingual queries
* English, Urdu, and Roman Urdu support
* Beginner, Intermediate, and Expert explanation levels
* Source-based responses
* 25 legal topic documents
* Streamlit web interface
* Grok AI integration
* Secure API key configuration using Streamlit Secrets

## Architecture

```text
User Question
      |
      v
Sentence Transformer
      |
      v
ChromaDB Semantic Search
      |
      v
Relevant Legal Documents
      |
      v
Grok AI
      |
      v
Grounded Legal Answer
```

## Tech Stack

* Python
* Streamlit
* Grok AI / xAI API
* ChromaDB
* Sentence Transformers
* GitHub
* Streamlit Community Cloud

## Project Structure

```text
INSAFBOT/
├── app.py
├── rag.py
├── requirements.txt
├── .gitignore
└── knowledge_base/
    ├── FIR_PPC.txt
    ├── Tenant_Landlord.txt
    ├── Cybercrime.txt
    ├── Divorce_Khula.txt
    ├── Bail.txt
    ├── Wills_Inheritance.txt
    └── ...25 legal documents
```

## API Configuration

INSAFBOT uses the **Grok API** for AI-generated legal explanations.

For local development, configure your Grok API key using environment variables.

For Streamlit Community Cloud, add the API key to:

## RAG Pipeline

The application follows these steps:

```text
1. User enters a legal question
              |
              v
2. Question is converted into an embedding
              |
              v
3. ChromaDB searches the legal knowledge base
              |
              v
4. Relevant legal documents are retrieved
              |
              v
5. Retrieved context is provided to Grok
              |
              v
6. Grok generates a grounded explanation
              |
              v
7. Sources are displayed to the user
```

## Supported Languages

Users can ask questions in:

* English
* Urdu
* Roman Urdu

Examples:

```text
What is the procedure for Khula in Pakistan?

Khula lene ka procedure kya hai?

پاکستان میں خلع لینے کا طریقہ کیا ہے؟
```

## Legal Knowledge Base

INSAFBOT contains a local legal knowledge base covering multiple Pakistani legal topics, including:

* FIR and PPC
* Bail
* Divorce and Khula
* Nikah
* Women's Marriage Rights
* Tenant and Landlord Law
* Cybercrime
* Wills and Inheritance
* Family Law
* Property-related matters
* Domestic Violence
* And other Pakistani legal topics

## Disclaimer

INSAFBOT provides **general legal information** based on its available knowledge base. It is not a lawyer and does not replace professional legal advice.

The information provided by the application may not reflect the latest amendments, judicial decisions, or individual circumstances.

For important or urgent legal matters, consult a qualified legal professional.

---

<p align="center">
<b>INSAFBOT</b> — AI-Powered Legal Information Assistant for Pakistan
</p>

<p align="center">
Grounded Legal Explanation
</p>
