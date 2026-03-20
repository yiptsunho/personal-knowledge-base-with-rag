from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from pathlib import Path

# Settings
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = Ollama(model="llama3.1:8b", request_timeout=120.0)

# Load some test documents (create a small folder with 3-5 PDFs/MDs)
documents = SimpleDirectoryReader("data/test_docs").load_data()

# Build index
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
)

# Query
query_engine = index.as_query_engine(llm=llm)
response = query_engine.query("What is the main topic in these documents?")
print(response)