import numpy as np
from app.db.database import get_session
from app.db.models import Transcription, Video
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


def search_media(query: str, top_k: int = 3):
    session = get_session()

    # Fetch audio transcription embeddings
    audio_rows = session.query(Transcription).all()
    audio_embeds = [np.frombuffer(a.embedding, dtype=np.float32) for a in audio_rows]

    # Fetch video embeddings
    video_rows = session.query(Video).all()
    video_embeds = [np.frombuffer(v.embedding, dtype=np.float32) for v in video_rows]

    # Combine embeddings
    all_embeds = (
        np.vstack(audio_embeds + video_embeds)
        if audio_embeds or video_embeds
        else np.array([])
    )

    if all_embeds.size == 0:
        return []

    # Encode query
    query_emb = model.encode([query])[0].reshape(1, -1)

    # Compute cosine similarity
    sims = cosine_similarity(query_emb, all_embeds)[0]
    top_indices = sims.argsort()[::-1][:top_k]

    results = []
    total_audio = len(audio_embeds)
    for idx in top_indices:
        score = float(sims[idx])
        if idx < total_audio:
            a = audio_rows[idx]
            results.append(
                {
                    "type": "transcription",
                    "filename": a.filename,
                    "text": a.text,
                    "score": score,
                }
            )
        else:
            v = video_rows[idx - total_audio]
            results.append(
                {
                    "type": "video",
                    "filename": v.filename,
                    "summary": v.summary,
                    "score": score,
                }
            )

    return results
