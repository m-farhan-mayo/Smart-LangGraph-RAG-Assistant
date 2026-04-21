def detect_query_type(query):
    query = query.lower()

    if "error" in query or "fail" in query:
        return "logs"
    elif "table" in query or "column" in query or "schema" in query:
        return "docs"
    else:
        return "all"