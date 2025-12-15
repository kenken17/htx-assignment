from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/process/audio")
def process_audio(file: UploadFile = File(...)):
    return {"message": "Audio processing started", "filename": file.filename}


@router.get("/transcriptions")
def get_transcriptions():
    return []
