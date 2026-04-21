smart-data-assistant/
│
├── data/
│   ├── logs/
│   ├── docs/
│
├── src/
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── splitter.py
│   │   ├── embedder.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── filters.py
│   │
│   ├── rag/
│   │   ├── pipeline.py
│   │
│   ├── langgraph_flow/
│   │   ├── graph.py
│   │
│   ├── utils/
│   │   ├── config.py
│
├── airflow/
│   ├── dag.py
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│
├── main.py
├── requirements.txt
├── README.md