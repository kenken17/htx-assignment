import logging

from app.api import audio, health, jobs, search, video
from app.db.database import Base, engine
from app.processing.processor import process_job
from app.queue.manager import QueueManager
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multimedia Processing Backend")

app.include_router(health.router)
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(search.router)
app.include_router(jobs.router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@app.on_event("startup")
async def startup():
    app.state.queue = QueueManager()
    await app.state.queue.start(worker_count=1, processor=process_job)


@app.on_event("shutdown")
async def shutdown():
    await app.state.queue.shutdown()
