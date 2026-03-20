import chromadb
from app.core.config import CHROMA_PATH

print(f"CHROMA_PATH: {CHROMA_PATH}")
client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_collection("personal_knowledge")  # or get_or_create_collection if needed

print("Collection count:", collection.count())
if collection.count() > 0:
    # Peek at first few items
    peek = collection.peek(limit=3)
    print("Sample IDs:", peek['ids'])
    print("Sample metadatas:", peek['metadatas'])
    print("Sample documents length:", [len(d) for d in peek['documents']])
else:
    print("Collection is EMPTY → that's why no retrieval happens!")