from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import chromadb
from pathlib import Path

# Settings (global for convenience)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0, temperature=0.1)

# Persistent Chroma client & collection
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # creates folder if missing
chroma_collection = chroma_client.get_or_create_collection("personal_knowledge")

# Vector store wrapper
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load documents (only if index doesn't exist or you want to refresh)
data_dir = Path("data/test_docs")
if not chroma_collection.count():  # simple check: empty collection → ingest
    print("Ingesting documents...")
    documents = SimpleDirectoryReader(data_dir).load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )
    print(f"Ingested {len(documents)} documents / {chroma_collection.count()} chunks.")
else:
    print("Loading existing index from Chroma...")
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

# Query engine
query_engine = index.as_query_engine(similarity_top_k=3)  # retrieve top 3 chunks

# Test query
response = query_engine.query("How many vaccines have mochi taken?")
print("\nResponse:")
print(response.response)
print("\nSources:")
for source in response.source_nodes:
    print(f"- {source.node.get_text()[:200]}... (score: {source.score:.3f})")