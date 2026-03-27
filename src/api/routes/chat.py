from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.api.deps import get_rag_pipeline

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query가 비어 있습니다.")
    pipeline = get_rag_pipeline()
    answer = pipeline.answer(req.query)
    return {"answer": answer}
