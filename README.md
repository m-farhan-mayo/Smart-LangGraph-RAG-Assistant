# 🧠 Smart Data Assistant

> A **Retrieval-Augmented Generation (RAG)** system built for Data Engineers — ask questions about your pipeline logs, database schemas, and documentation in plain English, and get accurate LLM-generated answers.

---

## 📌 The Problem We Solved

Data engineers deal with two recurring pain points daily:

1. **Pipeline debugging is slow** — when an Airflow DAG fails, you have to manually grep through logs, cross-reference error codes, and correlate with schema documentation spread across multiple files.
2. **Knowledge is scattered** — database schemas live in `.txt` files, error logs in `.log` files, and tribal knowledge in people's heads. There's no unified interface to query all of it.

**Smart Data Assistant** solves this by building a local AI assistant that:
- Ingests your logs and documentation into a semantic vector store
- Routes each question intelligently (schema question? → look in docs. Error? → look in logs)
- Retrieves the most relevant context and feeds it to a local LLM (Mistral via Ollama)
- Returns a plain-English answer through a chat UI

**Real example from this project:** The log `dag1.log` contained the error `ERROR: Task failed due to missing table users`. A user asking *"What columns are in the users table?"* gets a direct answer from the schema stored in `data/docs/schema.txt` — without opening a single file.

---

## 🏗️ Architecture

```
User (Browser Chat UI)
        │
        ▼
  FastAPI Server (main.py)
        │  POST /ask
        ▼
  LangGraph StateGraph (src/langgraph_flow/graph.py)
        │
        ├─── Node 1: classify()
        │       └── detect_query_type() → "logs" | "docs" | "all"
        │
        └─── Node 2: answer_node()
                │
                ▼
        RAG Pipeline (src/rag/pipeline.py)
                │
                ├── get_retriever() → filters FAISS by source type
                │
                ├── FAISS Vector Store (in-memory)
                │       └── all-MiniLM-L6-v2 embeddings
                │
                └── Ollama (Mistral 7B, running locally)
                        └── LCEL Chain: retriever | prompt | llm | parser
```
LangGraph
<img width="1227" height="1620" alt="LANGGRAPH" src="https://github.com/user-attachments/assets/8551c46c-fdf1-4b27-8bbb-b510db9a82db" />

RAG Pipeline
<img width="3203" height="129" alt="RAG PIPELINE" src="https://github.com/user-attachments/assets/5c6b27ec-9825-45e7-bee2-9ed6e64ce284" />

DATA FLOW
<img width="706" height="1113" alt="DATA FLOW" src="https://github.com/user-attachments/assets/017ae153-e81c-47bb-ba7d-22a13402acf3" />

Complete Project
<img width="1272" height="1587" alt="COMPLETE SYSTEM" src="https://github.com/user-attachments/assets/8924201d-2dde-4adf-a45e-52514f77660b" />

---

## 📁 Project Structure

```
smart-data-assistant/
│
├── data/
│   ├── logs/                   # Airflow DAG logs (e.g., dag1.log)
│   └── docs/                   # DB schemas, documentation (e.g., schema.txt)
│
├── src/
│   ├── ingestion/
│   │   ├── loader.py           # Reads all files from data/logs and data/docs
│   │   ├── splitter.py         # Splits text into overlapping chunks (300 chars, 50 overlap)
│   │   └── embedder.py         # Embeds chunks with HuggingFace + stores in FAISS
│   │
│   ├── retrieval/
│   │   ├── filters.py          # Detects query intent (logs / docs / all)
│   │   └── retriever.py        # Returns a source-filtered FAISS retriever
│   │
│   ├── rag/
│   │   └── pipeline.py         # LCEL chain: retriever → prompt → Mistral → output
│   │
│   └── langgraph_flow/
│       └── graph.py            # LangGraph StateGraph: classify → route → answer
│
├── static/
│   └── index.html              # Chat UI (dark-themed, served by FastAPI)
│
├── airflow/
│   └── dag.py                  # Airflow DAG definition (runs on Linux/WSL/Docker)
│
├── docker/
│   ├── Dockerfile              # Builds the Python app image
│   └── docker-compose.yml      # Orchestrates app + Airflow webserver + scheduler
│
├── main.py                     # FastAPI app entry point (serves UI + /ask API)
├── requirements.txt            # Python dependencies
└── pyproject.toml              # Project metadata
```

---

## ⚙️ How Each Module Works

### `src/ingestion/loader.py`
Reads every file from `data/logs/` and `data/docs/` and returns a list of documents, each tagged with its `source` folder (`logs` or `docs`) and `file_name`. This metadata is later used to filter retrieval.

### `src/ingestion/splitter.py`
Implements a custom sliding-window text splitter:
- **Chunk size:** 300 characters
- **Overlap:** 50 characters (so context isn't lost at chunk boundaries)

Each chunk retains the `source` and `file_name` metadata from its parent document.

### `src/ingestion/embedder.py`
Converts all chunks into vector embeddings using `sentence-transformers/all-MiniLM-L6-v2` (a lightweight, fast 384-dim model). Stores everything in a **FAISS** in-memory vector index for fast similarity search.

### `src/retrieval/filters.py`
Simple keyword-based intent classifier:
| Query contains | Routed to |
|---|---|
| `error`, `fail` | `logs` only |
| `table`, `column`, `schema` | `docs` only |
| anything else | `all` sources |

### `src/retrieval/retriever.py`
Returns a FAISS retriever with a **metadata filter** applied based on the detected query type. Fetches top-3 most relevant chunks.

### `src/rag/pipeline.py`
Builds a **LangChain Expression Language (LCEL)** chain:
```python
{"context": retriever | format_docs, "question": RunnablePassthrough()}
| PromptTemplate
| OllamaLLM (mistral)
| StrOutputParser
```
The prompt instructs the model to answer only from the provided context.

### `src/langgraph_flow/graph.py`
A **LangGraph** `StateGraph` that manages the workflow as discrete nodes:
1. **`classify`** — determines query type
2. **`answer`** — invokes the RAG pipeline

Conditional edges route the flow based on the classification result.

### `main.py`
FastAPI application that:
- Loads and embeds all data at startup (once, in-memory)
- Serves the chat frontend at `GET /`
- Accepts queries at `POST /ask` → invokes the LangGraph → returns the answer

### `static/index.html`
A fully self-contained dark-themed chat interface. Sends queries to `/ask` via `fetch()`, displays streaming-style typing indicators, and renders responses in a chat bubble layout.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Mistral 7B via [Ollama](https://ollama.ai) (runs 100% locally) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace |
| **Vector Store** | FAISS (in-memory, CPU) |
| **RAG Framework** | LangChain Core (LCEL) + `langchain-community` |
| **Orchestration** | LangGraph `StateGraph` |
| **API Server** | FastAPI + Uvicorn |
| **Frontend** | Vanilla HTML/CSS/JS (dark UI, no frameworks) |
| **Workflow Scheduler** | Apache Airflow (Linux/WSL/Docker only) |
| **Containerization** | Docker + Docker Compose |
| **Package Manager** | `uv` (fast Python package installer) |

---

## 🚧 Problems Encountered & How We Fixed Them

### 1. `ModuleNotFoundError: No module named 'langchain.chains'`
**Cause:** Installed LangChain v1.x, which removed `RetrievalQA` from `langchain.chains`. The class was deprecated and the entire `langchain.chains` submodule was restructured.  
**Fix:** Replaced `RetrievalQA` with a modern **LCEL chain** using `langchain_core` primitives (`RunnablePassthrough`, `PromptTemplate`, `StrOutputParser`). This is LangChain's recommended approach from v0.2+.

### 2. `ModuleNotFoundError: No module named 'langchain_community'`
**Cause:** Installed via `pip` into the system Python, not the active `.venv`.  
**Fix:** Used `uv pip install` to install into the virtual environment.

### 3. `ModuleNotFoundError: No module named 'fcntl'` (Airflow on Windows)
**Cause:** `fcntl` is a POSIX-only Unix system call module. It doesn't exist on Windows. Apache Airflow depends on it for file locking and process management.  
**Fix:** Airflow must run on Linux. Options: **WSL2**, **Docker (Linux container)**, or a remote Linux server.

### 4. `unable to get image '...': unexpected end of JSON input` (Docker)
**Cause:** Docker Desktop was not running. The Docker CLI pipe `//./pipe/docker_engine` didn't exist, so the CLI got an empty/malformed JSON response.  
**Fix:** Launch Docker Desktop and wait for it to fully start before running `docker-compose`.

### 5. `pip not found` in fresh WSL2 Ubuntu
**Cause:** Fresh Ubuntu installations don't include Python or pip.  
**Fix:**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
```

### 6. Wrong volume paths in `docker-compose.yml`
**Cause:** The compose file lives in `docker/` but referenced `./airflow` — which would be `docker/airflow/`, not the actual `airflow/` at the project root.  
**Fix:** Changed to `../airflow` (relative to the compose file location).

### 7. No UI at `http://127.0.0.1:8000`
**Cause:** FastAPI is a pure API framework — it serves JSON, not HTML. There was no root route and no static files configured.  
**Fix:** Added `StaticFiles` mount + a `GET /` route returning `index.html`, and created a full chat frontend in `static/index.html`.

### 8. `LangChainDeprecationWarning: class Ollama was deprecated`
**Cause:** `langchain_community.llms.Ollama` was deprecated in favour of `langchain-ollama` package.  
**Fix:** Install `langchain-ollama` and use `from langchain_ollama import OllamaLLM`.

---

## ▶️ How to Run

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) installed and running locally
- Mistral model pulled: `ollama pull mistral`

### 1. Clone & set up environment
```bash
git clone <repo-url>
cd smart-data-assistant

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install uv
uv pip install -r requirements.txt
```

### 3. Add your data
- Drop `.log` files into `data/logs/`
- Drop `.txt` / `.md` schema/documentation files into `data/docs/`

### 4. Start the server
```bash
uvicorn main:app --reload
```

### 5. Open the chat UI
Navigate to **http://127.0.0.1:8000** in your browser.

### 6. Use the API directly
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What columns are in the users table?"}'
```

### 7. Interactive API docs
Visit **http://127.0.0.1:8000/docs** for the Swagger UI.

---

## 🐳 Docker (for Airflow)

> Apache Airflow requires Linux. Use Docker on Windows.

```bash
# Make sure Docker Desktop is running first
cd docker
docker-compose up --build
```

- App: `http://localhost:8000`
- Airflow UI: `http://localhost:8080`

---

## 🔮 What's Next

- [ ] Persist the FAISS index to disk (avoid re-embedding on every restart)
- [ ] Support PDF and Markdown ingestion
- [ ] Add streaming responses to the chat UI
- [ ] Switch to `OllamaLLM` from `langchain-ollama` (remove deprecated import)
- [ ] Add Airflow DAG to auto-ingest new log files on a schedule
- [ ] Add Docker support for the full stack on Windows via WSL2

---

## 👤 Author

**Farhan MaYo** — Data Engineer  
Built as a learning project exploring RAG pipelines, LangGraph orchestration, and local LLM inference.
