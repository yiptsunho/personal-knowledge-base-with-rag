from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import chromadb
from app.core.config import CHROMA_PATH

# Global settings
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = Ollama(model="llama3.1:8b", request_timeout=180.0, temperature=0.2)

# Chroma setup
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
chroma_collection = chroma_client.get_or_create_collection("personal_knowledge")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Index (lazy load)
_index = None

def get_index():
    global _index
    if _index is None:
        _index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context,
        )
    return _index

def get_query_engine():
    index = get_index()
    return index.as_query_engine(similarity_top_k=4)  # adjust k as needed