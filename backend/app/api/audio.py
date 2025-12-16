from app.db import repository
from app.db.deps import get_db
from app.queue.models import Job
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/process/audio", status_code=202)
async def process_audio(
    file: UploadFile = File(...), db: Session = Depends(get_db), request: Request = None
):
    audio_bytes = await file.read()

    qm = request.app.state.queue
    job = qm.create_job(
        Job(
            type="audio",
            payload={"audio_bytes": audio_bytes, "filename": file.filename},
        )
    )
    await qm.enqueue(job.id)
    return {"job_id": job.id, "status": "queued"}


@router.get("/transcriptions")
def get_transcriptions(db: Session = Depends(get_db)):
    return repository.get_transcriptions(db)
