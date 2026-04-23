from typing import Dict, List

from api.services.loaders import get_rag_functions
from api.services.retrieval import run_search


def run_rag(question: str, method: str, top_k: int) -> Dict:
    functions = get_rag_functions()

    if method not in functions:
        raise ValueError(f"Unsupported RAG method: {method}")

    answer = functions[method](question, top_k=top_k)

    source_method = "hybrid" if method == "hybrid" else "semantic"

    try:
        sources: List[Dict] = run_search(question, source_method, top_k)
    except Exception:
        sources = []

    return {
        "answer": answer,
        "sources": sources,
    }