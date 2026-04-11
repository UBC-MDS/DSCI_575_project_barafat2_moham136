import datasets
import duckdb
datasets.logging.set_verbosity_error() 
from datasets import load_dataset
from pathlib import Path
import os
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
con = duckdb.connect()

# Define download and save function
def download_and_save_parquet(dataset_name, config_name, DATA_PATH, RAW_CACHE_DIR):
    print("Downloading dataset from Hugging Face...")

    hf_dataset = load_dataset(
        dataset_name,
        config_name,
        split="full",
        cache_dir=RAW_CACHE_DIR
    )

    print("Saving to parquet...")

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    pq.write_table(hf_dataset.data, DATA_PATH)

    return DATA_PATH


# Define load data function
def load_data(dataset_name, config_name, DATA_PATH, RAW_CACHE_DIR):
    if not DATA_PATH.exists():
        print("Parquet file not found. Downloading...")
        download_and_save_parquet(dataset_name, config_name, DATA_PATH, RAW_CACHE_DIR)
    else:
        print("Loading from local parquet...")

    return DATA_PATH




# Download and save reviews data    
RAW_CACHE_DIR = "../data/raw"
REVIEW_PATH = Path("../data/processed/reviews.parquet")

REVIEWS_DATASET = "McAuley-Lab/Amazon-Reviews-2023"
REVIEWS_NAME = "raw_review_All_Beauty"

review_path = load_data(REVIEWS_DATASET, REVIEWS_NAME, REVIEW_PATH, RAW_CACHE_DIR)
reviews = con.execute(f"SELECT * FROM read_parquet('{review_path}')").df()


# Load metadata
META_PATH = Path("../data/processed/meta.parquet")
meta_dataset = "McAuley-Lab/Amazon-Reviews-2023"
meta_name = "raw_meta_All_Beauty"

meta_path = load_data(meta_dataset, meta_name, META_PATH, RAW_CACHE_DIR)
metadata = con.execute(f"SELECT * FROM read_parquet('{meta_path}')").df()



# merging reviews and metadata on parent_asin and saving as merged.parquet
con.execute("""
COPY (
    SELECT
        r.rating,
        r.title,
        r.text,
        r.verified_purchase,
        m.title AS product_title,
        m.average_rating,
        m.price,
        m.description,
        m.store,
        m.details
    FROM read_parquet('../data/processed/reviews.parquet') r
    JOIN read_parquet('../data/processed/meta.parquet') m
    ON r.parent_asin = m.parent_asin
)
TO '../data/processed/merged.parquet'
(FORMAT PARQUET)
""")
