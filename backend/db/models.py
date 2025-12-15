from datetime import datetime

from db.database import Base
from sqlalchemy import JSON, Column, DateTime, Integer, String, Text


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    detected_objects = Column(JSON)
    frame_timestamps = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    text = Column(Text)
    timestamps = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
