from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import Ollama
from src.retrieval.retriever import get_retriever
from langchain_ollama import OllamaLLM


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def generate_answer(query, vectorstore):
    retriever = get_retriever(vectorstore, query)

    llm = Ollama(model="mistral")

    prompt = PromptTemplate.from_template(
        "Use the following context to answer the question.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    qa_chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return qa_chain.invoke(query)