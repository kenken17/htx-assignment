from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/search")
def search(q: str = Query(..., description="Search query")):
    return {"query": q, "videos": [], "transcriptions": []}
