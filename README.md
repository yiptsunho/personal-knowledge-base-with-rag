## Personal Second Brain – RAG Knowledge Base

A production-style personal knowledge base using local LLM (Ollama), embeddings, and vector search.

### Features
- Upload multiple documents (PDF, DOCX, MD, TXT) via API
- Persistent Chroma vector database
- Conversational querying with source citations
- Local/private inference (no cloud LLM calls required)
- FastAPI backend + Swagger UI for testing
- File type & size validation

### API Endpoints[](http://localhost:8000/docs)
- `POST /upload` – Upload files to index
- `POST /chat` – Ask questions about your documents
- `GET /status` – Health check & collection stats

### Quick Start
1. Install Ollama & pull model: `ollama pull llama3.1:8b`
2. `cd backend`
3. Activate venv: `source rag-env-312/bin/activate` (or your name)
4. `python -m uvicorn app.main:app --reload`
5. Open http://127.0.0.1:8000/docs

### Example Usage (curl)
```bash
# Upload
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "files=@path/to/your/document.pdf"

# Query
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is in my vaccination certificate?"}'