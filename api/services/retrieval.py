from typing import Dict, List

from api.services.loaders import get_search_functions


def _normalize_search_results(df) -> List[Dict]:
    if df is None:
        return []

    score_col = next(
        (col for col in ("hybrid_score", "score", "distance") if col in df.columns),
        None,
    )

    normalized = []
    for _, row in df.iterrows():
        item = {
            "product_title": str(row.get("product_title", "")),
            "text": str(row.get("text", "")),
            "rating": None,
            "score": None,
            "score_label": score_col,
        }

        if "rating" in df.columns and row.get("rating") is not None:
            try:
                item["rating"] = float(row["rating"])
            except Exception:
                item["rating"] = None

        if score_col is not None:
            value = row.get(score_col)
            if value is not None:
                try:
                    item["score"] = float(value)
                except Exception:
                    item["score"] = None

        normalized.append(item)

    return normalized


def run_search(query: str, method: str, top_k: int) -> List[Dict]:
    functions = get_search_functions()

    if method not in functions:
        raise ValueError(f"Unsupported search method: {method}")

    result_df = functions[method](query, top_k)
    return _normalize_search_results(result_df)