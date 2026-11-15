from fastapi import FastAPI, HTTPException, Query
from . import storage
from .schemas import SearchResult, SearchResults, PageResult
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .storage import BASE_DIR


app = FastAPI()


@app.get("/api/search", response_model=SearchResults)
def search_pages(term: str = Query(min_length=1), limit: int = Query(default=10, ge=1, le=100)) -> SearchResults:
    term = term.strip()

    if not term:
        raise HTTPException(status_code=400, detail="Terme vide")

    hits = storage.search(term, limit)
    results = [SearchResult(id=hit.id, title=hit.title, score=hit.score) for hit in hits]

    return SearchResults(results=results)


@app.get("/api/pages/{page_id}", response_model=PageResult)
def read_page(page_id: int) -> PageResult:
    page = storage.fetch_page(page_id)

    if page is None:
        raise HTTPException(status_code=404, detail="Article introuvable")

    return PageResult(id=page.id, title=page.title, text=page.text)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")