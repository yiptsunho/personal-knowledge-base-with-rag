from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # now points to project root
DATA_DIR = BASE_DIR / "data"
CHROMA_PATH = BASE_DIR / "chroma_db"          # ← change to root-level
DOCS_DIR = DATA_DIR / "test_docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)