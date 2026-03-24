from langgraph.graph import StateGraph, END
from typing import TypedDict
from app.services.rag_service import query_rag
from app.services.agent_service import summarize_tool, calculator_tool

# -----------------------
# STATE
# -----------------------
class AgentState(TypedDict):
    query: str
    history: list
    doc_id: str   # 🔥 ADD THIS
    response: str


# -----------------------
# NODE 1: DECIDE
# -----------------------
def decide_tool(state: AgentState):
    query = state["query"].lower()

    if "summary" in query:
        return "summarize"
    elif any(op in query for op in ["+", "-", "*", "/"]):
        return "calculator"
    else:
        return "rag"


# -----------------------
# NODE 2: RAG
# -----------------------
def rag_node(state: AgentState):
    answer = query_rag(
        state["query"],
        history=state["history"],
        doc_id=state["doc_id"]
    )

    return {"response": answer}


# -----------------------
# NODE 3: SUMMARIZE
# -----------------------
def summarize_node(state: AgentState):
    answer = summarize_tool()
    return {"response": answer}


# -----------------------
# NODE 4: CALCULATOR
# -----------------------
def calculator_node(state: AgentState):
    answer = calculator_tool(state["query"])
    return {"response": answer}


# -----------------------
# GRAPH BUILD
# -----------------------
builder = StateGraph(AgentState)

builder.add_node("rag", rag_node)
builder.add_node("summarize", summarize_node)
builder.add_node("calculator", calculator_node)

# Decision routing
def router(state: AgentState):
    return decide_tool(state)

builder.add_conditional_edges(
    "rag",  # entry placeholder
    router,
    {
        "rag": "rag",
        "summarize": "summarize",
        "calculator": "calculator",
    }
)

builder.set_entry_point("rag")

builder.add_edge("rag", END)
builder.add_edge("summarize", END)
builder.add_edge("calculator", END)

graph = builder.compile()