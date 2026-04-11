import datasets
import duckdb
datasets.logging.set_verbosity_error() 
from datasets import load_dataset
from pathlib import Path
import os
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

# Download the dataset from Hugging Face and save it as a parquet file for faster loading in the future. 
# The parquet file will be stored in the `data/processed` directory, while the raw dataset will be cached in `data/raw` by Hugging Face's `datasets` library.    
RAW_CACHE_DIR = "../data/raw"
DATA_PATH = Path("../data/processed/reviews.parquet")

HF_DATASET = "McAuley-Lab/Amazon-Reviews-2023"
HF_NAME = "raw_review_All_Beauty"


def download_and_save_parquet(dataset_name, config_name):
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


def load_data():
    if not DATA_PATH.exists():
        print("Parquet file not found. Downloading...")
        download_and_save_parquet(HF_DATASET, HF_NAME)
    else:
        print("Loading from local parquet...")

    return DATA_PATH

con = duckdb.connect()
data_path = load_data()
df = con.execute(f"SELECT * FROM read_parquet('{data_path}')").df()


