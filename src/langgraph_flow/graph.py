from langgraph.graph import StateGraph
from typing import TypedDict

from src.rag.pipeline import generate_answer
from src.retrieval.filters import detect_query_type


# Define state
class GraphState(TypedDict):
    query: str
    vectorstore: object
    query_type: str
    answer: str


# Step 1: classify query
def classify(state: GraphState):
    query_type = detect_query_type(state["query"])
    return {"query_type": query_type}


# Step 2: route decision
def route(state: GraphState):
    return state["query_type"]


# Step 3: generate answer
def answer_node(state: GraphState):
    answer = generate_answer(state["query"], state["vectorstore"])
    return {"answer": answer}


# Build graph
def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify", classify)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route,
        {
            "logs": "answer",
            "docs": "answer",
            "all": "answer"
        }
    )

    graph.set_finish_point("answer")

    return graph.compile()