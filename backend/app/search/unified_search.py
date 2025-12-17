from typing import Literal, Optional

import numpy as np
from app.db.database import get_session
from app.db.models import Transcription, Video
from sentence_transformers import SentenceTransformer

RefType = Literal["video", "transcription"]

model = SentenceTransformer("all-MiniLM-L6-v2")


def cosine_sim_matrix(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = np.linalg.norm(query_vec)
    matrix_norms = np.linalg.norm(matrix, axis=1)
    return (matrix @ query_vec) / ((query_norm * matrix_norms) + 1e-12)


def search_media(
    query: Optional[str] = None,
    top_k: int = 3,
    ref_type: Optional[RefType] = None,
    ref_id: Optional[int] = None,
    exclude_self: bool = True,
):
    session = get_session()

    q = (query or "").strip()

    # Require either a non-empty query OR a reference
    if not q and not (ref_type and ref_id is not None):
        return []

    # Fetch rows
    audio_rows = session.query(Transcription).all()
    video_rows = session.query(Video).all()

    # Build embedding arrays and aligned metadata
    audio_embeds = []
    audio_meta = []
    for a in audio_rows:
        if a.embedding:
            audio_embeds.append(np.frombuffer(a.embedding, dtype=np.float32))
            audio_meta.append(a)

    video_embeds = []
    video_meta = []
    for v in video_rows:
        if v.embedding:
            video_embeds.append(np.frombuffer(v.embedding, dtype=np.float32))
            video_meta.append(v)

    if not audio_embeds and not video_embeds:
        return []

    all_embeds = np.vstack(audio_embeds + video_embeds)

    # Build query embedding (either text or reference embedding)
    reference_key = None  # used to filter out self result if requested

    if q:
        query_emb = model.encode(q)
    else:
        # Reference search: load the reference record embedding
        if ref_type == "transcription":
            ref = session.query(Transcription).filter_by(id=ref_id).first()
            if not ref or not ref.embedding:
                return []
            query_emb = np.frombuffer(ref.embedding, dtype=np.float32)
            reference_key = ("transcription", ref_id)
        elif ref_type == "video":
            ref = session.query(Video).filter_by(id=ref_id).first()
            if not ref or not ref.embedding:
                return []
            query_emb = np.frombuffer(ref.embedding, dtype=np.float32)
            reference_key = ("video", ref_id)
        else:
            return []

    sims = cosine_sim_matrix(query_emb, all_embeds)

    # Sort all indices by similarity descending
    sorted_indices = sims.argsort()[::-1]

    results = []
    total_audio = len(audio_embeds)

    for idx in sorted_indices:
        score = float(sims[idx])

        if idx < total_audio:
            a = audio_meta[idx]
            item_key = ("transcription", a.id)
            if exclude_self and reference_key and item_key == reference_key:
                continue
            results.append(
                {
                    "type": "transcription",
                    "id": a.id,
                    "filename": a.filename,
                    "text": a.text,
                    "score": score,
                }
            )
        else:
            v = video_meta[idx - total_audio]
            item_key = ("video", v.id)
            if exclude_self and reference_key and item_key == reference_key:
                continue
            results.append(
                {
                    "type": "video",
                    "id": v.id,
                    "filename": v.filename,
                    "summary": v.summary,
                    "score": score,
                }
            )

        if len(results) >= top_k:
            break

    return results
