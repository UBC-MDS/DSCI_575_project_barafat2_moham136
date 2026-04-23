from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

API_TITLE = "Beauty Review Retrieval API"
API_VERSION = "0.1.0"

DEFAULT_TOP_K = 3
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))