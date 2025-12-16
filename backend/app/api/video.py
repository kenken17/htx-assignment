import os
import shutil

from app.db import repository
from app.db.deps import get_db
from app.queue.models import Job
from app.video.detection import ObjectDetector
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()

# Paths for MobileNet SSD
PROTOTXT = "app/video/models/MobileNetSSD_deploy.prototxt"
MODEL = "app/video/models/MobileNetSSD_deploy.caffemodel"

detector = ObjectDetector(PROTOTXT, MODEL)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/process/video", status_code=202)
async def process_video(
    file: UploadFile = File(...), db: Session = Depends(get_db), request: Request = None
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    qm = request.app.state.queue
    job = qm.create_job(
        Job(type="video", payload={"file_path": file_path, "filename": file.filename})
    )
    await qm.enqueue(job.id)
    return {"job_id": job.id, "status": "queued"}


@router.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    return repository.get_videos(db)
