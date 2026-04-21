from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from src.ingestion.loader import load_all_data
from src.ingestion.splitter import split_documents
from src.ingestion.embedder import create_vector_store
from src.langgraph_flow.graph import build_graph

app = FastAPI(title="Smart Data Assistant")

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join("static", "index.html"))

print("Loading data...")
documents = load_all_data()

print("Splitting documents...")
chunks = split_documents(documents)

print("Creating vector store...")
vectorstore = create_vector_store(chunks)

graph = build_graph()


class QueryRequest(BaseModel):
    query: str


@app.post("/ask")
def ask_question(request: QueryRequest):
    result = graph.invoke({
        "query": request.query,
        "vectorstore": vectorstore
    })

    return {"answer": result["answer"]}