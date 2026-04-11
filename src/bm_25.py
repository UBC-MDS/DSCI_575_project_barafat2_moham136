import duckdb
import rank_bm25
import nltk


# Create a DuckDB connection
con = duckdb.connect()

df = con.execute("""
    SELECT *
    FROM read_parquet('../data/processed/merged.parquet')
""").df()