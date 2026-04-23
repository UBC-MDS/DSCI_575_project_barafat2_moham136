from typing import List, Literal, Optional
from pydantic import BaseModel, Field


SearchMethod = Literal["bm25", "semantic", "hybrid"]
RAGMethod = Literal["semantic", "hybrid"]


class HealthResponse(BaseModel):
    status: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    method: SearchMethod = "bm25"
    top_k: int = Field(default=3, ge=1, le=20)


class SearchResult(BaseModel):
    product_title: str
    text: str
    rating: Optional[float] = None
    score: Optional[float] = None
    score_label: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]


class RAGRequest(BaseModel):
    question: str = Field(..., min_length=1)
    method: RAGMethod = "semantic"
    top_k: int = Field(default=5, ge=1, le=20)


class SourceResult(BaseModel):
    product_title: str
    text: str
    rating: Optional[float] = None
    score: Optional[float] = None
    score_label: Optional[str] = None


class RAGResponse(BaseModel):
    answer: str
    sources: List[SourceResult] = []