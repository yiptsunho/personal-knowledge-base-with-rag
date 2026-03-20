from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.rag import get_query_engine
from time import perf_counter
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    question: str

class SourceItem(BaseModel):
    filename: str | None = None
    snippet: str
    score: float | None = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    latency_ms: float
    status: str = "success"

@router.post("/", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start_time = perf_counter()

    try:
        query_engine = get_query_engine()
        logger.info(f"Query received: {request.question}")
        response = query_engine.query(request.question)

        sources = []
        for node in response.source_nodes:
            meta = node.node.metadata
            sources.append(SourceItem(
                filename=meta.get("filename"),
                snippet=node.node.get_text()[:350] + ("..." if len(node.node.get_text()) > 350 else ""),
                score=float(node.score) if node.score else None
            ))

        latency_ms = (perf_counter() - start_time) * 1000

        logger.info(f"Retrieved {len(response.source_nodes)} nodes, generated answer in {latency_ms:.1f} ms")

        return QueryResponse(
            answer=str(response.response).strip(),
            sources=sources,
            latency_ms=round(latency_ms, 1)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")