from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/process/video")
def process_video(file: UploadFile = File(...)):
    return {"message": "Video processing started", "filename": file.filename}


@router.get("/videos")
def get_videos():
    return []
