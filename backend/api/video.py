from db.deps import get_db
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/process/video")
def process_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return {"message": "Video processing started", "filename": file.filename}


@router.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    return []  # Will connect to repository later
