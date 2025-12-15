from db.deps import get_db
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/process/audio")
def process_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return {"message": "Audio processing started", "filename": file.filename}


@router.get("/transcriptions")
def get_transcriptions(db: Session = Depends(get_db)):
    return []
