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

# Ensure paths are relative to project root (not where script is run from)
BASE_DIR = Path(__file__).resolve().parents[1]

def resolve_path(path_str):
    return BASE_DIR / path_str.replace("../", "")


# Define download and save function
def download_and_save_parquet(dataset_name, config_name, DATA_PATH, RAW_CACHE_DIR):
    print("Downloading dataset from Hugging Face...")

    hf_dataset = load_dataset(
        dataset_name,
        config_name,
        split="full",
        cache_dir=RAW_CACHE_DIR,
        trust_remote_code=True,
        token=os.environ.get("HF_TOKEN")

    )

    print("Saving to parquet...")

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    hf_dataset.to_parquet(str(DATA_PATH))

    return DATA_PATH


# Define load data function
def load_data(dataset_name, config_name, DATA_PATH, RAW_CACHE_DIR):
    if not DATA_PATH.exists():
        print("Parquet file not found. Downloading...")
        download_and_save_parquet(dataset_name, config_name, DATA_PATH, RAW_CACHE_DIR)
    else:
        print("Loading from local parquet...")

    return DATA_PATH



os.makedirs(resolve_path("../data"), exist_ok=True)
os.makedirs(resolve_path("../data/raw"), exist_ok=True)
os.makedirs(resolve_path("../data/processed"), exist_ok=True)
# Download and save reviews data    
RAW_CACHE_DIR = resolve_path("../data/raw")
REVIEW_PATH = resolve_path("../data/processed/reviews.parquet")

REVIEWS_DATASET = "McAuley-Lab/Amazon-Reviews-2023"
REVIEWS_NAME = "raw_review_All_Beauty"

review_path = load_data(REVIEWS_DATASET, REVIEWS_NAME, REVIEW_PATH, RAW_CACHE_DIR)
reviews = con.execute(f"SELECT * FROM read_parquet('{review_path}')").df()


# Load metadata
META_PATH = resolve_path("../data/processed/meta.parquet")
meta_dataset = "McAuley-Lab/Amazon-Reviews-2023"
meta_name = "raw_meta_All_Beauty"

meta_path = load_data(meta_dataset, meta_name, META_PATH, RAW_CACHE_DIR)
metadata = con.execute(f"SELECT * FROM read_parquet('{meta_path}')").df()



# merging reviews and metadata on parent_asin and saving as merged.parquet
MERGED_PATH = resolve_path("../data/processed/merged.parquet")
con.execute(f"""
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
    FROM read_parquet('{REVIEW_PATH}') r
    JOIN read_parquet('{META_PATH}') m
    ON r.parent_asin = m.parent_asin
)
TO '{MERGED_PATH}'
(FORMAT PARQUET)
""")
