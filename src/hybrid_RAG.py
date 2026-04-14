import os
import pickle
import re
import pandas as pd
import numpy as np
import faiss
import nltk
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate

from search import bm25_search, preprocess_text, load_artifacts
from semantic_search import semantic_search, load_semantic_artifacts

nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords

load_dotenv()

stop_words = set(stopwords.words("english"))

# HYBRID RETRIEVER  (Reciprocal Rank Fusion)

def reciprocal_rank_fusion(
    bm25_results: pd.DataFrame,
    sem_results: pd.DataFrame,
    k: int = 60
) -> pd.DataFrame:
    """
    Reciprocal Rank Fusion (RRF):
        RRF_score(doc) = sum over retrievers of  1 / (k + rank)

    k=60 is the standard default (Robertson & Zaragoza, 2009).
    Lower rank (i.e. rank=1 is best) gives a higher RRF score.
    """
    rrf_scores: dict[str, float] = {}
    doc_store:  dict[str, dict]  = {}


    # BM25 ranks
    for rank, (_, row) in enumerate(bm25_results.iterrows(), start=1):
        title = str(row["product_title"])
        rrf_scores[title] = rrf_scores.get(title, 0.0) + 1.0 / (k + rank)
        if title not in doc_store:
            doc_store[title] = {
                "product_title": title,
                "text": row.get("text", ""),
                "rating": row.get("rating", None),
            }

    # Semantic ranks
    for rank, (_, row) in enumerate(sem_results.iterrows(), start=1):
        title = str(row["product_title"])
        rrf_scores[title] = rrf_scores.get(title, 0.0) + 1.0 / (k + rank)
        if title not in doc_store:
            doc_store[title] = {
                "product_title": title,
                "text": row.get("text", ""),
                "rating": row.get("rating", None),
            }

    # Sort by RRF score descending
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    rows = []
    for title, score in ranked:
        entry = doc_store[title].copy()
        entry["rrf_score"] = round(score, 6)
        rows.append(entry)

    return pd.DataFrame(rows)


def hybrid_search(query: str, top_k: int = 5) -> pd.DataFrame:
    """
    Full hybrid retriever:
      1. BM25 top-k (keyword match)
      2. Semantic top-k (embedding similarity)
      3. RRF re-ranking
      4. Return top-k fused results
    """
    bm25_results = bm25_search(query, top_k=top_k)
    sem_results  = semantic_search(query, top_k=top_k)
    fused        = reciprocal_rank_fusion(bm25_results, sem_results)
    return fused.head(top_k).reset_index(drop=True)


# RAG PIPELINE WITH HYBRID RETRIEVER

def _load_llm():
    endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        task="text-generation",
        max_new_tokens=300,
        provider="auto",
    )
    return ChatHuggingFace(llm=endpoint)


PROMPT_TEMPLATE = """
You are a helpful product recommendation assistant.
Use ONLY the product information provided below to answer the user's question.
Products are ranked by relevance. If none match well, say so honestly.

Retrieved Products:
{context}

User Question: {question}

Your Answer:
"""

prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


def _format_context(results: pd.DataFrame) -> str:
    parts = []
    for i, row in results.iterrows():
        part = (
            f"Product {i+1}: {row['product_title']}\n"
            f"Description: {row.get('text', 'N/A')}\n"
            f"Rating: {row.get('rating', 'N/A')}\n"
            f"Relevance score (RRF): {row.get('rrf_score', 'N/A')}"
        )
        parts.append(part)
    return "\n\n---\n\n".join(parts)


def hybrid_rag_query(question: str, top_k: int = 5) -> str:
    """
    Main entry point for the hybrid RAG pipeline.
    Replaces the semantic-only retriever from Step 2 with the hybrid retriever.
    """
    llm = _load_llm()

    # Retrieve with hybrid search
    results = hybrid_search(question, top_k=top_k)
    context = _format_context(results)

    # Fill prompt and call LLM
    filled_prompt = prompt.invoke({"context": context, "question": question})
    response = llm.invoke(filled_prompt)
    return response.content


# QUICK TEST

if __name__ == "__main__":
    query = "I need a good moisturizer for sensitive skin. What do your top 5 recommends under 20$?"

    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    print("\n--- BM25 results ---")
    print(bm25_search(query, top_k=3)[["product_title", "score"]].to_string())

    print("\n--- Semantic results ---")
    print(semantic_search(query, top_k=3)[["product_title", "score"]].to_string())

    print("\n--- Hybrid (RRF) results ---")
    print(hybrid_search(query, top_k=5)[["product_title", "rrf_score"]].to_string())

    print("\n--- LLM answer ---")
    print(hybrid_rag_query(query, top_k=5))