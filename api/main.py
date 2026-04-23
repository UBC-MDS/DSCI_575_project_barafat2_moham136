from fastapi import FastAPI, HTTPException

from api.config import API_TITLE, API_VERSION
from api.schemas import (
    HealthResponse,
    SearchRequest,
    SearchResponse,
    RAGRequest,
    RAGResponse,
)
from api.services.retrieval import run_search
from api.services.rag import run_rag


app = FastAPI(title=API_TITLE, version=API_VERSION)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/search", response_model=SearchResponse)
def search_reviews(payload: SearchRequest) -> SearchResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        results = run_search(
            query=query,
            method=payload.method,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc

    return SearchResponse(results=results)


@app.post("/rag", response_model=RAGResponse)
def rag_reviews(payload: RAGRequest) -> RAGResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = run_rag(
            question=question,
            method=payload.method,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG request failed: {exc}") from exc

    return RAGResponse(**result)