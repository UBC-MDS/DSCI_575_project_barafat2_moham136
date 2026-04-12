import duckdb
import nltk
import os
import pickle
import re
from rank_bm25 import BM25Okapi

nltk.download("stopwords")

from nltk.corpus import stopwords
stop_words = set(stopwords.words("english"))

# Preprocessing function
def preprocess_text(text):

    # Lowercase
    text = str(text).lower()

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove whitespace
    tokens = text.split()

    # remove stop words
    tokens = [word for word in tokens if word not in stop_words]

    return tokens


# Create a DuckDB connection
con = duckdb.connect()

os.makedirs("data/processed", exist_ok=True)

data_dir_tokenized = "data/processed/tokenized_corpus.pkl"
docs_path = "data/processed/documents.parquet"

if os.path.exists(data_dir_tokenized) and os.path.exists(docs_path):
    print("Loading tokenized corpus and documents from file...")
    with open(data_dir_tokenized, "rb") as f:
        tokenized_corpus = pickle.load(f)
    
    docs_path = "data/processed/documents.parquet"
    df = con.execute(f"SELECT * FROM read_parquet('{docs_path}')").df()
else:
    df = con.execute("""
        SELECT
            title,
            text,
            rating,
            product_title
        FROM read_parquet('data/processed/merged.parquet')
    """).df()

    df = df.reset_index(drop=True)
    df["text"] = df["text"].fillna("").astype(str)

    tokens = df["text"].map(preprocess_text)

    tokenized_corpus = tokens.tolist()

    with open(data_dir_tokenized, "wb") as f:
        pickle.dump(tokenized_corpus, f)
    
    
    df.to_parquet(docs_path, index=False)




## BM25 model
os.makedirs("models", exist_ok=True)
bm25_dir = "models/bm25_model.pkl"

if os.path.exists(bm25_dir):
    print("Loading BM25 model from file...")
    with open(bm25_dir, "rb") as f:
        bm25 = pickle.load(f)
else:
    bm25 = BM25Okapi(tokenized_corpus)
    
    
    with open(os.path.join("models", "bm25_model.pkl"), "wb") as f:
        pickle.dump(bm25, f)
