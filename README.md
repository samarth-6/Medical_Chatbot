# Medical Chatbot

A medical AI assistant that combines **trusted medical web search** with **document-based Retrieval-Augmented Generation (RAG)** to provide accurate, source-backed answers.

## Features

### Trusted Medical Web Search

The assistant searches trusted medical sources and generates responses grounded in reliable information.

Supported sources include:

* PubMed
* MedlinePlus
* Mayo Clinic
* WebMD
* Healthline
* NIH
* WHO
* CDC
* Cleveland Clinic
* Johns Hopkins Medicine

Responses include source citations whenever relevant information is found.

---

### Document Question Answering (RAG)

Upload your own medical documents and ask questions about their contents.

Supported document types:

* PDF
* DOCX
* TXT

The system:

1. Extracts text from uploaded documents.
2. Splits content into chunks.
3. Generates embeddings using Gemini Embeddings.
4. Stores vectors in Neon PostgreSQL with pgvector.
5. Retrieves relevant chunks for user queries.
6. Uses Gemini to generate answers based on retrieved context.

---

### Intelligent Query Routing

A planner agent determines whether a query should be handled by:

* Web Search Agent
* RAG Agent

This allows users to seamlessly switch between general medical questions and document-specific questions.

---

## How to Use

### Web Search Mode

Use this mode for general medical questions.

Examples:

* What are the symptoms of diabetes?
* What causes high blood pressure?
* What are the side effects of ibuprofen?

The system searches trusted medical websites and generates a summarized response with sources.

---

### Document Mode (RAG)

Use this mode when you want answers from your uploaded documents.

#### Step 1: Upload Documents

Upload one or more supported files.

The application creates a unique document session and indexes the contents.

#### Step 2: Ask Questions

After uploading, ask questions such as:

* Summarize this report.
* What medications are mentioned?
* What diagnosis is discussed in the document?
* What treatment recommendations are provided?

The answer is generated only from the uploaded documents.

---

## Architecture

### Planner Agent

Determines:

* Whether the query is medical.
* Whether to use web search or document retrieval.

### Web Search Agent

* Searches trusted medical sources.
* Collects relevant information.
* Returns source-backed context.

### RAG Agent

* Retrieves relevant document chunks from the vector database.
* Provides document-specific context.

### Synthesis Agent

* Generates final answers.
* Combines retrieved context with the user's question.
* Produces concise and medically relevant responses.

---

## Tech Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Python

### LLM

* Gemini 2.5 Flash

### Embeddings

* Gemini Embedding Model (`gemini-embedding-001`)

### Vector Database

* Neon PostgreSQL
* pgvector

### Document Processing

* PyPDF
* python-docx

---

## Important Disclaimer

This application is intended for informational and educational purposes only.

It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals regarding medical concerns.

---
