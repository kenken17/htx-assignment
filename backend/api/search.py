from fastapi import APIRouter, Query
from search.unified_search import search_media

router = APIRouter()


@router.get("/search")
def search(q: str = Query(..., description="Query text"), top_k: int = 3):
    """
    Perform unified search across audio transcriptions and video summaries.
    Uses embeddings stored in SQLite.
    """
    results = search_media(q, top_k)
    return {"query": q, "results": results}
