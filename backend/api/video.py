import os
import shutil

from db import repository
from db.deps import get_db
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from video.detection import ObjectDetector
from video.pipeline import process_video_frames
from video.summary import generate_video_embedding, generate_video_summary

router = APIRouter()

# Paths for MobileNet SSD
PROTOTXT = "video/models/MobileNetSSD_deploy.prototxt"
MODEL = "video/models/MobileNetSSD_deploy.caffemodel"

detector = ObjectDetector(PROTOTXT, MODEL)

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/process/video")
def process_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run pipeline: keyframes + object detection
    pipeline_result = process_video_frames(file_path, detector)
    keyframes = pipeline_result["keyframes"]
    detections = pipeline_result["objects"]

    # Generate summary and embedding
    summary_text = generate_video_summary(detections)
    embedding = generate_video_embedding(summary_text)

    # Save to DB
    video_record = repository.save_video(
        db,
        filename=file.filename,
        keyframes=keyframes,
        detected_objects=detections,
        summary=summary_text,
        embedding=embedding,
    )

    return {
        "filename": video_record.filename,
        "keyframes_count": len(keyframes),
        "objects_detected_count": len(detections),
        "summary": summary_text,
        "embedding_length": len(embedding),
        "message": "Video processed successfully",
    }


@router.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    return repository.get_videos(db)
