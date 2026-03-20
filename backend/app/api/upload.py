from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Annotated
from datetime import datetime
import uuid
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from app.core.rag import chroma_collection, storage_context, Settings
from app.core.config import DOCS_DIR
from pathlib import Path
import shutil
from pydantic import WithJsonSchema
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

# Create a typed alias with the correct schema hint
BinaryUploadFile = Annotated[
    UploadFile,
    WithJsonSchema({"type": "string", "format": "binary"})
]

@router.post("/", summary="Upload documents to the knowledge base")
async def upload_documents(
    files: List[BinaryUploadFile] = File(...),
    # testFile: UploadFile = File(...),
):
    """
    Upload one or more documents (PDF, DOCX, MD, TXT supported).
    Files are parsed, chunked, embedded, and added to the existing index.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    added_docs = 0
    added_chunks = 0
    errors = []

    # Use the global embed_model and storage context
    embed_model = Settings.embed_model

    # Simple node parser (you can tune chunk_size/overlap later)
    node_parser = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=200,
    )

    for file in files:
        logger.info(f"Processing file: {file.filename}")
        try:
            # Save temporarily (or process in memory)
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in [".pdf", ".docx", ".md", ".txt", ".markdown"]:
                errors.append(f"Unsupported file type: {file.filename}")
                continue

            # Temporary save path
            temp_path = DOCS_DIR / f"upload_{uuid.uuid4()}_{file.filename}"
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Load as LlamaIndex Document(s)
            # For simplicity we use SimpleDirectoryReader on single file
            from llama_index.core import SimpleDirectoryReader
            reader = SimpleDirectoryReader(
                input_files=[temp_path],
                required_exts=[file_ext],
            )
            docs = reader.load_data()

            if not docs:
                errors.append(f"No content extracted from {file.filename}")
                temp_path.unlink()  # cleanup
                continue

            # Add metadata to each document
            upload_time = datetime.utcnow().isoformat()
            for doc in docs:
                doc.metadata["filename"] = file.filename
                doc.metadata["upload_time"] = upload_time
                doc.metadata["source"] = "user_upload"

            # Parse into nodes/chunks
            nodes = node_parser.get_nodes_from_documents(docs)

            # Index (this upserts automatically via Chroma)
            from llama_index.core import VectorStoreIndex
            index = VectorStoreIndex.from_documents(
                docs,  # we pass docs, but nodes are used internally
                storage_context=storage_context,
                embed_model=embed_model,
                show_progress=False,  # quieter in API
            )

            # Alternative (more explicit upsert):
            # chroma_collection.upsert(
            #     ids=[str(uuid.uuid4()) for _ in nodes],
            #     embeddings=[embed_model.get_text_embedding(n.get_content()) for n in nodes],
            #     metadatas=[n.metadata for n in nodes],
            #     documents=[n.get_content() for n in nodes],
            # )

            added_docs += len(docs)
            added_chunks += len(nodes)

            # Cleanup temp file
            temp_path.unlink()

        except Exception as e:
            errors.append(f"Error processing {file.filename}: {str(e)}")

    status = {
        "message": "Upload completed",
        "added_documents": added_docs,
        "added_chunks": added_chunks,
        "errors": errors,
        "total_files_received": len(files),
    }

    if errors:
        status["warning"] = f"{len(errors)} file(s) had issues"

    return status