import pandas as pd
import numpy as np
from search import bm25_search
from semantic_search import semantic_search

def normalize_scores(scores):
    """Normalize scores to 0-1 range using min-max normalization."""
    if len(scores) == 0:
        return scores
    min_score = scores.min()
    max_score = scores.max()
    if max_score == min_score:
        return np.ones_like(scores)
    return (scores - min_score) / (max_score - min_score)

def search_hybrid(query, top_k=3, alpha=0.5):
    """
    Hybrid search combining BM25 and semantic search.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        alpha: Weight for BM25 (1-alpha will be weight for semantic)
               alpha=1.0 means pure BM25, alpha=0.0 means pure semantic
    
    Returns:
        DataFrame with top_k results sorted by hybrid score
    """
    # Get more results from each method to ensure good coverage after merging
    fetch_k = top_k * 3
    
    # Get BM25 results
    bm25_results = bm25_search(query, top_k=fetch_k)
    bm25_results = bm25_results.copy()
    bm25_results['bm25_score'] = normalize_scores(bm25_results['score'].values)
    
    # Get semantic results
    semantic_results = semantic_search(query, top_k=fetch_k)
    semantic_results = semantic_results.copy()
    # For semantic, lower distance is better, so invert it
    semantic_results['semantic_score'] = 1 / (1 + semantic_results['distance'].values)
    semantic_results['semantic_score'] = normalize_scores(semantic_results['semantic_score'].values)
    
    # Merge results on title (assuming title is unique enough)
    # You might want to use a different key if you have product IDs
    bm25_results = bm25_results[['title', 'text', 'rating', 'bm25_score']]
    semantic_results = semantic_results[['title', 'text', 'rating', 'semantic_score']]
    
    # Outer merge to get all results from both methods
    merged = pd.merge(
        bm25_results, 
        semantic_results, 
        on=['title', 'text', 'rating'], 
        how='outer'
    )
    
    # Fill missing scores with 0 (items only found by one method)
    merged['bm25_score'] = merged['bm25_score'].fillna(0)
    merged['semantic_score'] = merged['semantic_score'].fillna(0)
    
    # Calculate hybrid score
    merged['hybrid_score'] = (
        alpha * merged['bm25_score'] + 
        (1 - alpha) * merged['semantic_score']
    )
    
    # Sort by hybrid score and return top_k
    merged = merged.sort_values('hybrid_score', ascending=False)

    merged["text"] = merged["text"].apply(
    lambda x: x[:200] + "..." if isinstance(x, str) and len(x) > 200 else x
)
    
    # Return with relevant columns
    return merged[['title', 'text', 'hybrid_score', 'rating']].head(top_k).reset_index(drop=True)