<h1> INSAFBOT</h1>

<h3 align="center">AI-Powered Legal Information Assistant for Pakistan</h3>

<p align="center">
  A Retrieval-Augmented Generation (RAG) based legal information assistant
  that helps users understand Pakistani laws using trusted legal documents.
</p>

<p align="center">
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit" alt="Streamlit">
  </a>
  <a href="https://ai.google.dev/">
    <img src="https://img.shields.io/badge/AI-Google%20Gemini-blue?logo=google" alt="Google Gemini">
  </a>
  <img src="https://img.shields.io/badge/RAG-Enabled-green" alt="RAG">
  <img src="https://img.shields.io/badge/Language-English%20%7C%20Urdu%20%7C%20Roman%20Urdu-orange" alt="Languages">
</p>

---

## 📌 About INSAFBOT

**INSAFBOT** is an AI-powered legal information assistant designed to help people understand Pakistani laws in simple language.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from a collection of Pakistani legal documents before generating an answer using **Google Gemini**.

Users can ask questions in:

- 🇬🇧 English
- 🇵🇰 Urdu
- 🔤 Roman Urdu

INSAFBOT provides answers based on the legal documents available in its knowledge base and displays the relevant legal sources used to generate the response.

> ⚠️ INSAFBOT provides general legal information and is not a replacement for a qualified lawyer or professional legal advice.

---

# ✨ Features

## 🤖 AI Legal Question Answering

Users can ask questions related to Pakistani laws and receive AI-generated explanations based on retrieved legal documents.

Example:

> "Mere husband mujhe maintenance nahi de rahe, main kya kar sakti hoon?"

---

## 🔎 Retrieval-Augmented Generation (RAG)

INSAFBOT does not rely only on the AI model's general knowledge.

Instead, it follows this process:

```text
User Question
      ↓
Question Embedding
      ↓
Semantic Search
      ↓
Relevant Legal Documents
      ↓
Relevant Legal Sections / Text
      ↓
Google Gemini
      ↓
Grounded Legal Explanation
