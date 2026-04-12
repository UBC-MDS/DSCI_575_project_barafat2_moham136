import pickle
import re
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

DOCS_PATH = "data/processed/documents.parquet"
BM25_PATH = "models/bm25_model.pkl"

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

def load_artifacts():
    docs = pd.read_parquet(DOCS_PATH)

    with open(BM25_PATH, "rb") as f:
        bm25 = pickle.load(f)

    return docs, bm25

df, bm25 = load_artifacts()

def bm25_search(query, top_k=3):
    tokenized_query = preprocess_text(query)
    scores = np.array(bm25.get_scores(tokenized_query))

    top_idx = np.argsort(-scores)[:top_k]

    results = df.iloc[top_idx].copy()
    results["score"] = scores[top_idx]

    return results[["title", "text", "score", "rating"]].reset_index(drop=True)
