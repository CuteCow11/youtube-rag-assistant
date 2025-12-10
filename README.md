# 🎥 YouTube RAG Assistant

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/🦜_LangChain-RAG-green?style=for-the-badge)
![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-purple?style=for-the-badge)
![Chrome](https://img.shields.io/badge/Chrome_Extension-Manifest_V3-yellow?style=for-the-badge&logo=google-chrome)

**Stop watching, start asking.**

A powerful Chrome Extension that gives YouTube videos a "brain." It extracts transcripts, processes them with AI, and lets you chat with any video in real-time using a local Python server.

## 📸 Demo
![App Screenshot](./demo1.png)
![App Screenshot](./demo2.png)
![App Screenshot](./demo3.png)


## 🏗️ Architecture

```mermaid
graph LR
    A["Chrome Extension\n(Side Panel)"] -- "POST /chat" --> B("FastAPI Server")
    B --> C{"LangChain Logic"}
    C -- "1. Retrieve Context" --> D[("FAISS Vector DB")]
    C -- "2. Query + Context" --> E["OpenRouter / Gemma LLM"]
    E -- "3. Answer" --> B
    B -- "JSON Response" --> A





