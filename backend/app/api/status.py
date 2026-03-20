# backend/app/api/status.py
from fastapi import APIRouter
from datetime import datetime
from app.core.rag import chroma_collection
from app.core.config import CHROMA_PATH
import os

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/")
async def get_status():
    try:
        count = chroma_collection.count()
        db_size_mb = 0
        if os.path.exists(CHROMA_PATH):
            for root, _, files in os.walk(CHROMA_PATH):
                for f in files:
                    db_size_mb += os.path.getsize(os.path.join(root, f)) / (1024 * 1024)

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "chroma_collection_items": count,
            "chroma_db_size_mb": round(db_size_mb, 2),
            "chroma_path": str(CHROMA_PATH),
            "ollama_model": "llama3.1:8b",  # or make dynamic if you add switching later
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}