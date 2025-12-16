from app.api import audio, health, search, video
from app.db.database import Base, engine
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multimedia Processing Backend")

app.include_router(health.router)
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(search.router)
