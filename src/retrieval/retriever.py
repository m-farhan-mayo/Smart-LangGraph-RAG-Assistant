from src.retrieval.filters import detect_query_type


def get_retriever(vectorstore, query):
    query_type = detect_query_type(query)

    if query_type == "all":
        return vectorstore.as_retriever(search_kwargs={"k": 3})
    else:
        return vectorstore.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": {"source": query_type}
            }
        )