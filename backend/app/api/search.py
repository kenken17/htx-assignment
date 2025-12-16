from app.search.unified_search import search_media
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/search")
def search(q: str = Query(..., description="Query text"), top_k: int = 3):
    """
    Perform unified search across audio transcriptions and video summaries.
    Uses embeddings stored in SQLite.
    """
    results = search_media(q, top_k)
    return {"query": q, "results": results}
