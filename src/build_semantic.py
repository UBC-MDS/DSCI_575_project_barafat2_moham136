import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

# Load data
DOCUMENTS_PATH = "data/processed/documents.pkl"
df = pd.read_parquet('data/processed/merged.parquet')

if os.path.exists(DOCUMENTS_PATH):
    print("Loading existing documents from disk...")
    with open(DOCUMENTS_PATH, "rb") as f:
        documents = pickle.load(f)
else:
    print("Creating documents...")
    df['combined_text'] = (
        df['product_title'].fillna('') + ' ' +
        df['text'].fillna('')
    ).str.strip()

    documents = df['combined_text'].tolist()

    with open(DOCUMENTS_PATH, "wb") as f:
        pickle.dump(documents, f)
    print("Documents saved.")

# Generate embeddings 
model = SentenceTransformer('all-MiniLM-L6-v2')

EMBEDDINGS_PATH = "data/processed/embeddings.npy"

if os.path.exists(EMBEDDINGS_PATH):
    print("Loading existing embeddings from disk...")
    embeddings = np.load(EMBEDDINGS_PATH)
else:
    print("Generating embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True, batch_size=256)
    np.save(EMBEDDINGS_PATH, embeddings)
    print("Embeddings saved.")

# Build FAISS index 
dimension = embeddings.shape[1] 
index = faiss.IndexFlatL2(dimension)   
index.add(embeddings)

# Save index
os.makedirs('data/processed/faiss_index', exist_ok=True)
faiss.write_index(index, 'data/processed/faiss_index/index.faiss')
print("FAISS index saved.")