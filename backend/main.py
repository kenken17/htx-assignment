from api import audio, health, search, video
from fastapi import FastAPI

app = FastAPI(title="Multimedia Processing Backend")

app.include_router(health.router)
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(search.router)
