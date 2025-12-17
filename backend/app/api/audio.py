import os
import shutil

from app.db import repository
from app.db.deps import get_db
from app.queue.models import Job
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/process/audio", status_code=202)
async def process_audio(
    file: UploadFile = File(...), db: Session = Depends(get_db), request: Request = None
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    qm = request.app.state.queue
    job = qm.create_job(
        Job(
            type="audio",
            payload={"file_path": file_path, "filename": file.filename},
        )
    )
    await qm.enqueue(job.id)
    return {"job_id": job.id, "status": "queued"}


@router.get("/transcriptions")
def get_transcriptions(db: Session = Depends(get_db)):
    return repository.get_transcriptions(db)
