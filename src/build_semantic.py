import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

# Load data
DOCUMENTS_PATH = "data/processed/documents.pkl"
 

if os.path.exists(DOCUMENTS_PATH):
    print("Loading existing documents from disk...")
    with open(DOCUMENTS_PATH, "rb") as f:
        documents = pickle.load(f)
else:
    print("Creating documents...")
    df = pd.read_parquet('data/processed/merged.parquet')
    df['search_text'] = (
        df['product_title'].astype(str).fillna('') + ' ' +
        df['text'].astype(str).fillna('') + ' ' +
        df['description'].astype(str).fillna('')
        ).str.strip()

    documents = df['search_text'].tolist()
    df.to_parquet('data/processed/new_products.parquet', index=False)

    with open(DOCUMENTS_PATH, "wb") as f:
        pickle.dump(documents, f)
    print("Documents saved.")

# Generate embeddings 
model = SentenceTransformer('all-MiniLM-L6-v2')

EMBEDDINGS_PATH = "data/processed/new_embeddings.npy"

if os.path.exists(EMBEDDINGS_PATH):
    print("Loading existing embeddings from disk...")
    embeddings = np.load(EMBEDDINGS_PATH)
else:
    print("Generating embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True, batch_size=256)
    np.save(EMBEDDINGS_PATH, embeddings)
    print("Embeddings saved.")


INDEX_PATH = "data/processed/faiss_index/index_products.faiss"
os.makedirs('data/processed/faiss_index', exist_ok=True)

if os.path.exists(INDEX_PATH):
    print("FAISS index already exists. Skipping index creation.")
else:
    embeddings = np.array(embeddings, dtype=np.float32)
    embeddings = np.ascontiguousarray(embeddings)

    chunk_size = 10000
    for i in range(0, len(embeddings), chunk_size):
        chunk = embeddings[i:i+chunk_size]
        faiss.normalize_L2(chunk)
        embeddings[i:i+chunk_size] = chunk
    # Build FAISS index 
    
    dimension = embeddings.shape[1] 
    index = faiss.IndexFlatL2(dimension)   
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    print("FAISS index saved.")