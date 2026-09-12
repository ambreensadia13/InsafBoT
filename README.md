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
<img src="https://img.shields.io/badge/AI-Google%20Gemini-blue">
<img src="https://img.shields.io/badge/RAG-ChromaDB-green">
<img src="https://img.shields.io/badge/Language-English%20%7C%20Urdu%20%7C%20Roman%20Urdu-orange">
</p>

---

## About

INSAFBOT is an AI-powered legal information assistant that helps users understand Pakistani legal topics in simple language.

The application uses **RAG, ChromaDB, Sentence Transformers, and Google Gemini** to retrieve relevant legal information before generating a response.

Users can ask questions in **English, Urdu, or Roman Urdu**.

## Features

* AI-powered legal question answering
* Retrieval-Augmented Generation (RAG)
* Semantic search using ChromaDB
* Multilingual queries
* Beginner, Intermediate, and Expert explanation levels
* Source-based responses
* 25 legal topic documents
* Streamlit web interface
* Google Gemini integration

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
Google Gemini
      |
      v
Grounded Legal Answer
```

## Tech Stack

* Python
* Streamlit
* Google Gemini
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

## Installation

```bash
git clone https://github.com/YOUR-USERNAME/INSAFBOT.git
cd INSAFBOT
pip install -r requirements.txt
streamlit run app.py
```

Add your Gemini API key to:

```text
.streamlit/secrets.toml
```

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Never upload your API key to GitHub.

## Example Questions

```text
Police meri FIR darj nahi kar rahi, main kya kar sakta hoon?

Mera CNIC gum ho gaya hai, duplicate CNIC kaise banwa sakta hoon?

Khula lene ke liye aurat ko kya legal process follow karna hota hai?

Office mein harassment ho rahi hai, complaint kahan file karni chahiye?

Contract ki shart poori na ho to main kya legal action le sakta hoon?
```

## Disclaimer

INSAFBOT provides **general legal information** based on its available knowledge base. It is not a lawyer and does not replace professional legal advice.

For important or urgent legal matters, consult a qualified legal professional.

---

<p align="center">
<b>INSAFBOT</b> — AI-Powered Legal Information Assistant for Pakistan
</p>

Grounded Legal Explanation
