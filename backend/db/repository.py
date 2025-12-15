import numpy as np
from db import models
from sqlalchemy.orm import Session


def save_video(
    db,
    filename: str,
    keyframes: list,
    detected_objects: list,
    summary: str,
    embedding: list,
):
    video = models.Video(
        filename=filename,
        keyframes=keyframes,
        detected_objects=detected_objects,
        summary=summary,
        embedding=embedding,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def save_transcription(
    db: Session, filename: str, text: str, timestamps: list, embedding=None
):
    transcription = models.Transcription(
        filename=filename, text=text, timestamps=timestamps, embedding=embedding
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    return transcription


def get_videos(db: Session):
    records = db.query(models.Video).all()
    result = []

    for r in records:
        # Deserialize embedding if present
        embedding_array = None
        if r.embedding is not None:
            embedding_array = np.frombuffer(r.embedding, dtype=np.float32)
            embedding_array = embedding_array.tolist()  # optional, for JSON response

        result.append(
            {
                "id": r.id,
                "filename": r.filename,
                "summary": r.summary,
                "embedding": embedding_array,
                "created_at": r.created_at.isoformat(),
            }
        )

    return result


def get_transcriptions(db: Session):
    records = db.query(models.Transcription).all()
    result = []

    for r in records:
        # Deserialize embedding if present
        embedding_array = None
        if r.embedding is not None:
            embedding_array = np.frombuffer(r.embedding, dtype=np.float32)
            embedding_array = embedding_array.tolist()

        result.append(
            {
                "id": r.id,
                "filename": r.filename,
                "text": r.text,
                "timestamps": r.timestamps,
                "embedding": embedding_array,
                "created_at": r.created_at.isoformat(),
            }
        )

    return result
