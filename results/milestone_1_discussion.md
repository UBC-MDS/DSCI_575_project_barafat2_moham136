# Retrieval Evaluation: BM25 vs Semantic Search
more details about query comparison found in `notebooks/queries_comparison.ipynb`
## Dataset
Amazon product reviews (hair care category).
Corpus: review title + review text, joined with product metadata.
Embedding model: all-MiniLM-L6-v2
BM25 implementation: rank_bm25 (BM25Okapi)
## Query Results and Observations

### Q1 [KEYWORD]: "argan oil hair spray"
| Rank | BM25 Result | Semantic Result |
|------|-------------|-----------------|
| 1    | ...         | ...             |
| ...  | ...         | ...             |

**Observation:** BM25 performs well here because the query contains exact product
terms. Both methods return relevant results, but BM25 ranks exact matches higher.
Semantic search may surface related products (e.g., argan oil serums) that are
relevant but not sprays.