from functools import lru_cache
import sys

from api.config import SRC_DIR

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


@lru_cache(maxsize=1)
def get_search_functions():
    from search import bm25_search
    from semantic_search import semantic_search
    from hybrid_search import search_hybrid

    return {
        "bm25": bm25_search,
        "semantic": semantic_search,
        "hybrid": search_hybrid,
    }


@lru_cache(maxsize=1)
def get_rag_functions():
    from RAG_pipeline import rag_query
    from hybrid_RAG import hybrid_rag_query

    return {
        "semantic": rag_query,
        "hybrid": hybrid_rag_query,
    }