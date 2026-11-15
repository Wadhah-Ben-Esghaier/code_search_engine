from pydantic import BaseModel


class SearchResult(BaseModel):
    id: int
    title: str
    score: float


class SearchResults(BaseModel):
    results: list[SearchResult]


class PageResult(BaseModel):
    id: int
    title: str
    text: str