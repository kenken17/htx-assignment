from typing import Literal, Optional

from app.search.unified_search import search_media
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/search")
def search(
    q: Optional[str] = None,
    top_k: int = Query(3, ge=1, le=50),
    ref_type: Optional[Literal["video", "transcription"]] = None,
    ref_id: Optional[int] = None,
):
    results = search_media(
        query=q,
        top_k=top_k,
        ref_type=ref_type,
        ref_id=ref_id,
        exclude_self=True,
    )
    return {"results": results}
