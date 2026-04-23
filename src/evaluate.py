"""
Quantitative evaluation of BM25, semantic, and hybrid search pipelines.

Metrics:
    precision@k: fraction of top-k results that are relevant
    recall@k:    fraction of all relevant products found in top-k

Usage:
    python src/evaluate.py
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from search import bm25_search
from semantic_search import semantic_search
from hybrid_search import search_hybrid


# ---------------------------------------------------------------------------
# Test queries with known relevant products
# Each entry has:
#   query:             the search string
#   relevant_keywords: substrings that should appear in a relevant product title
#                      (case-insensitive partial match, so you don't need exact titles)
# ---------------------------------------------------------------------------
TEST_QUERIES = [
    {
        "query": "moisturizing face cream",
        "relevant_keywords": ["moistur", "face cream", "hydrat", "lotion", "cerave", "neutrogena"],
    },
    {
        "query": "red lipstick long lasting",
        "relevant_keywords": ["lipstick", "lip color", "lip colour", "matte lip", "lip stain"],
    },
    {
        "query": "gentle shampoo for sensitive scalp",
        "relevant_keywords": ["shampoo", "scalp", "gentle", "sulfate free", "hair wash"],
    },
    {
        "query": "anti aging serum vitamin c",
        "relevant_keywords": ["serum", "vitamin c", "anti aging", "anti-aging", "retinol", "brightening"],
    },
    {
        "query": "sunscreen SPF 50 face",
        "relevant_keywords": ["sunscreen", "spf", "sun protection", "sunblock", "uv"],
    },
    {
        "query": "volumizing mascara black",
        "relevant_keywords": ["mascara", "volume", "lash", "eye"],
    },
    {
        "query": "natural deodorant aluminum free",
        "relevant_keywords": ["deodorant", "aluminum free", "natural", "aluminum-free"],
    },
    {
        "query": "exfoliating face scrub",
        "relevant_keywords": ["scrub", "exfoliat", "peel", "face wash"],
    },
    {
        "query": "hair oil argan shine",
        "relevant_keywords": ["hair oil", "argan", "shine", "serum", "moroccan"],
    },
    {
        "query": "eyeshadow palette neutral",
        "relevant_keywords": ["eyeshadow", "eye shadow", "palette", "neutral", "nude"],
    },
]


def is_relevant(product_title: str, relevant_keywords: list) -> bool:
    """
    Check if a product title matches any of the relevant keywords.

    Args:
        product_title:     the product title string from search results
        relevant_keywords: list of lowercase substrings to match against

    Returns:
        True if any keyword is found in the lowercased title
    """
    title_lower = str(product_title).lower()
    return any(kw in title_lower for kw in relevant_keywords)


def precision_at_k(results: pd.DataFrame, relevant_keywords: list, k: int) -> float:
    """
    Compute precision@k: fraction of top-k results that are relevant.

    Args:
        results:           DataFrame with a 'product_title' column
        relevant_keywords: list of keywords defining relevance
        k:                 cutoff rank

    Returns:
        precision@k as a float between 0 and 1
    """
    top_k = results.head(k)
    relevant_count = sum(
        is_relevant(row["product_title"], relevant_keywords)
        for _, row in top_k.iterrows()
    )
    return relevant_count / k


def recall_at_k(results: pd.DataFrame, relevant_keywords: list, k: int, total_relevant: int) -> float:
    """
    Compute recall@k: fraction of all relevant products retrieved in top-k.

    Args:
        results:           DataFrame with a 'product_title' column
        relevant_keywords: list of keywords defining relevance
        k:                 cutoff rank
        total_relevant:    estimated total number of relevant products in the corpus

    Returns:
        recall@k as a float between 0 and 1
    """
    if total_relevant == 0:
        return 0.0
    top_k = results.head(k)
    relevant_count = sum(
        is_relevant(row["product_title"], relevant_keywords)
        for _, row in top_k.iterrows()
    )
    return relevant_count / total_relevant


def estimate_total_relevant(search_fn, query: str, relevant_keywords: list, large_k: int = 50) -> int:
    """
    Estimate total relevant products by fetching a large result set.

    Args:
        search_fn:         one of bm25_search, semantic_search, search_hybrid
        query:             the search query string
        relevant_keywords: list of keywords defining relevance
        large_k:           how many results to fetch for the estimate

    Returns:
        count of relevant products found in the large result set
    """
    try:
        results = search_fn(query, top_k=large_k)
    except TypeError:
        results = search_fn(query, top_k=large_k, alpha=0.5)

    return sum(
        is_relevant(row["product_title"], relevant_keywords)
        for _, row in results.iterrows()
    )


def evaluate_pipeline(search_fn, fn_name: str, k_values: list = [3, 5, 10]) -> pd.DataFrame:
    """
    Run all test queries through a search function and compute metrics.

    Args:
        search_fn: callable, one of bm25_search / semantic_search / search_hybrid
        fn_name:   display name for this pipeline
        k_values:  list of k cutoffs to evaluate at

    Returns:
        DataFrame with one row per query and columns for each metric/k combo
    """
    rows = []

    for item in TEST_QUERIES:
        query = item["query"]
        keywords = item["relevant_keywords"]

        try:
            results = search_fn(query, top_k=max(k_values))
        except TypeError:
            results = search_fn(query, top_k=max(k_values), alpha=0.5)

        total_relevant = estimate_total_relevant(search_fn, query, keywords)
        total_relevant = max(total_relevant, 1)

        row = {"query": query}
        for k in k_values:
            row[f"precision@{k}"] = round(precision_at_k(results, keywords, k), 3)
            row[f"recall@{k}"]    = round(recall_at_k(results, keywords, k, total_relevant), 3)

        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"\n{'='*60}")
    print(f"Pipeline: {fn_name}")
    print('='*60)
    print(df.to_string(index=False))

    mean_row = df.drop(columns="query").mean().round(3)
    print(f"\nMean scores across {len(TEST_QUERIES)} queries:")
    print(mean_row.to_string())

    return df


def compare_pipelines(k_values: list = [3, 5, 10]) -> pd.DataFrame:
    """
    Compare BM25, semantic, and hybrid pipelines on all test queries.

    Args:
        k_values: list of k cutoffs to evaluate at

    Returns:
        DataFrame with mean scores for each pipeline side by side
    """
    pipelines = [
        (bm25_search,     "BM25"),
        (semantic_search, "Semantic"),
        (search_hybrid,   "Hybrid"),
    ]

    summary_rows = []

    for fn, name in pipelines:
        print(f"\nEvaluating {name}...")
        df = evaluate_pipeline(fn, name, k_values)
        means = df.drop(columns="query").mean().round(3)
        means["pipeline"] = name
        summary_rows.append(means)

    summary = pd.DataFrame(summary_rows).set_index("pipeline")

    print(f"\n{'='*60}")
    print("SUMMARY: Mean scores across all queries")
    print('='*60)
    print(summary.to_string())

    return summary


if __name__ == "__main__":
    K_VALUES = [3, 5, 10]
    summary = compare_pipelines(k_values=K_VALUES)

    # Save results to CSV
    out_path = ROOT / "results" / "evaluation_results.csv"
    out_path.parent.mkdir(exist_ok=True)
    summary.to_csv(out_path)
    print(f"\nResults saved to {out_path}")