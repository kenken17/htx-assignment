from db import models
from sqlalchemy.orm import Session


def save_video(
    db: Session, filename: str, detected_objects: list, frame_timestamps: list
):
    video = models.Video(
        filename=filename,
        detected_objects=detected_objects,
        frame_timestamps=frame_timestamps,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def save_transcription(db: Session, filename: str, text: str, timestamps: list):
    transcription = models.Transcription(
        filename=filename, text=text, timestamps=timestamps
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    return transcription


def get_videos(db: Session):
    return db.query(models.Video).all()


def get_transcriptions(db: Session):
    return db.query(models.Transcription).all()
