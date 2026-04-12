import pickle
import re
from unittest import result
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

DOCS_PATH = "data/processed/documents.parquet"
BM25_PATH = "models/bm25_model.pkl"

# Global cache
_df = None
_bm25 = None

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

def load_artifacts():
    global _df, _bm25
    
    if _df is None or _bm25 is None:
        print("Loading BM25 artifacts...")
        _df = pd.read_parquet(DOCS_PATH)
        with open(BM25_PATH, "rb") as f:
            _bm25 = pickle.load(f)
    
    return _df, _bm25

def bm25_search(query, top_k=3):
    df, bm25 = load_artifacts()
    
    tokenized_query = preprocess_text(query)
    scores = np.array(bm25.get_scores(tokenized_query))
    top_idx = np.argsort(-scores)[:top_k]

    results = df.iloc[top_idx].copy()
    results["score"] = scores[top_idx]

    results["text"] = results["text"].apply(
    lambda x: x[:200] + "..." if isinstance(x, str) and len(x) > 200 else x
)

    return results[["title", "text", "score", "rating"]].reset_index(drop=True)