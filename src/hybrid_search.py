import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords


BASE_DIR = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd()

DOCS_PATH = BASE_DIR / "data" / "processed" / "documents.parquet"
BM25_PATH = BASE_DIR / "models" / "bm25_model.pkl"
EMBEDDINGS_PATH = BASE_DIR / "data" / "processed" / "embeddings.npy"

nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return tokens


docs = pd.read_parquet(DOCS_PATH)

with open(BM25_PATH, "rb") as f:
    bm25 = pickle.load(f)


docs["semantic_text"] = (
    docs["product_title"].fillna("").astype(str) + " " +
    docs["title"].fillna("").astype(str) + " " +
    docs["text"].fillna("").astype(str)
)

model = SentenceTransformer("all-MiniLM-L6-v2")

if EMBEDDINGS_PATH.exists():
    print("Loading saved embeddings...")
    doc_embeddings = np.load(EMBEDDINGS_PATH)
else:
    print("Computing embeddings...")
    doc_embeddings = model.encode(
        docs["semantic_text"].tolist(),
        show_progress_bar=True,
        normalize_embeddings=True
    )
    np.save(EMBEDDINGS_PATH, doc_embeddings)


def min_max_scale(x):
    x = np.asarray(x, dtype=float)
    denom = x.max() - x.min()
    if denom == 0:
        return np.zeros_like(x)
    return (x - x.min()) / denom


def search_hybrid(query, top_k=5, alpha=0.5):
    # BM25 scores
    query_tokens = preprocess_text(query)
    bm25_scores = np.array(bm25.get_scores(query_tokens), dtype=float)

    # Semantic scores
    query_embedding = model.encode([query], normalize_embeddings=True)[0]
    semantic_scores = doc_embeddings @ query_embedding

    # Normalize before combining
    bm25_scaled = min_max_scale(bm25_scores)
    semantic_scaled = min_max_scale(semantic_scores)

    hybrid_scores = alpha * bm25_scaled + (1 - alpha) * semantic_scaled

    top_idx = np.argsort(-hybrid_scores)[:top_k]

    results = docs.iloc[top_idx].copy()
    results["bm25_score"] = bm25_scores[top_idx]
    results["semantic_score"] = semantic_scores[top_idx]
    results["hybrid_score"] = hybrid_scores[top_idx]

    cols = [c for c in [
        "title", "text", "rating","hybrid_score"
    ] if c in results.columns]

    return results[cols].reset_index(drop=True)