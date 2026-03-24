from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import query_rag

router = APIRouter(prefix="/chat", tags=["Chat"])

chat_memory = {}

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"
    doc_id: str | None = None


@router.post("/")
def chat(req: ChatRequest):
    if req.session_id not in chat_memory:
        chat_memory[req.session_id] = []

    history = chat_memory[req.session_id]

    response = query_rag(req.query, history, req.doc_id)

    history.append({"user": req.query, "bot": response})

    return {"response": response}