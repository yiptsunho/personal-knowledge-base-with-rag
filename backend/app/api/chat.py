from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.rag import get_query_engine

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/")
async def query_rag(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        query_engine = get_query_engine()
        response = query_engine.query(request.question)

        print("\nResponse:")
        print(response.response)
        
        sources = [
            {
                "text": node.node.get_text()[:300] + "..." if len(node.node.get_text()) > 300 else node.node.get_text(),
                "score": float(node.score) if node.score else None
            }
            for node in response.source_nodes
        ]
        
        return {
            "answer": str(response.response),
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")