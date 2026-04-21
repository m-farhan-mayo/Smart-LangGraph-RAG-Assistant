def split_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += (chunk_size - overlap)

    return chunks


def split_documents(documents):
    all_chunks = []

    for doc in documents:
        chunks = split_text(doc["text"])

        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "file_name": doc["file_name"]
            })

    return all_chunks