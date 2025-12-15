import numpy as np
from db.deps import get_db
from db.models import Transcription
from fastapi import APIRouter, Depends, Query
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

router = APIRouter()

# Load same embedding model used in audio processing
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


@router.get("/search")
def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(2, description="Number of results"),
    db: Session = Depends(get_db),
):
    # Generate query embedding
    query_embedding = embedding_model.encode(q)

    # Load all transcriptions with embeddings
    records = db.query(Transcription).filter(Transcription.embedding.isnot(None)).all()

    if not records:
        return {"query": q, "results": []}

    # Prepare embeddings matrix
    embeddings = np.array([r.embedding for r in records])

    # Compute cosine similarity
    similarities = cosine_similarity(query_embedding.reshape(1, -1), embeddings)[0]

    # Rank results
    ranked = sorted(zip(records, similarities), key=lambda x: x[1], reverse=True)[
        :limit
    ]

    # Format response
    results = []
    for record, score in ranked:
        results.append(
            {
                "filename": record.filename,
                "text": record.text,
                "similarity": float(score),
                "timestamps": record.timestamps,
                "created_at": record.created_at,
            }
        )

    return {"query": q, "results": results}
