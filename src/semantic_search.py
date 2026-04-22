import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path

# Resolve paths relative to THIS file, so they work regardless of
# which directory the app is launched from.
# BASE_DIR = Path(__file__).resolve().parents[1]  # project root (one level above src/)
BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH   = BASE_DIR / "data" / "processed" / "faiss_index" / "index_products.faiss"
PARQUET_PATH = BASE_DIR / "data" / "processed" / "new_products.parquet"

# Global cache 
_model = None
_index = None
_df    = None


def load_semantic_artifacts():
    global _model, _index, _df

    if _model is None or _index is None or _df is None:
        print("Loading semantic search artifacts...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        _index = faiss.read_index(str(INDEX_PATH))
        _df    = pd.read_parquet(str(PARQUET_PATH))

    return _model, _index, _df


def semantic_search(query, top_k=5):
    model, index, df = load_semantic_artifacts()

    query_embedding = model.encode([query]).astype('float32')
    distances, indices = index.search(query_embedding, top_k)

    results = df.iloc[indices[0]].copy()
    results['score'] = distances[0]

    final = pd.DataFrame(results)[["product_title", "text", "score", "rating"]]
    final["text"] = final["text"].apply(
        lambda x: x[:200] + "..." if isinstance(x, str) and len(x) > 200 else x
    )

    return final