
from typing import Any

from fastapi import APIRouter, HTTPException

from scholaris.chatbot import ScholarisChatbot
from scholaris.config import load_config
from scholaris.types import QueryRequest, QueryResponse

router = APIRouter(prefix="/api/v1", tags=["scholaris"])

config = load_config()
chatbot = ScholarisChatbot(config)


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "scholaris"}


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        response = chatbot.ask(
            query=request.query,
            session_id=request.session_id,
            max_hops=request.max_hops,
            include_reasoning=request.include_reasoning,
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_document(file_path: str) -> dict[str, Any]:
    try:
        result = chatbot.ingest_document(file_path)
        return {
            "status": "success",
            "document_id": result.get("document_id"),
            "chunks": result.get("chunks", 0),
            "entities": result.get("entities", 0),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str) -> dict[str, str]:
    chatbot.clear_session(session_id)
    return {"status": "success", "message": f"Session {session_id} cleared"}


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    return {
        "status": "operational",
        "provider": config.llm.provider,
        "model": config.llm.model,
    }
