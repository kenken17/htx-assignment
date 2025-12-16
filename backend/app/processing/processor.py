import asyncio
import io
import os

import numpy as np
import whisper
from app.db import repository
from app.db.database import SessionLocal
from app.queue.errors import NonRetryableJobError
from app.queue.models import Job
from app.video.detection import ObjectDetector
from app.video.pipeline import process_video_frames
from app.video.summary import generate_video_embedding, generate_video_summary
from pydub import AudioSegment
from sentence_transformers import SentenceTransformer

# Use the same embedding model as video
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Whisper tiny (CPU-friendly)
WHISPER_MODEL = whisper.load_model("tiny")

# MobileNet SSD paths (README tells how to download these)
PROTOTXT = "app/video/models/MobileNetSSD_deploy.prototxt"
MODEL = "app/video/models/MobileNetSSD_deploy.caffemodel"

_detector = None


def _set(job: Job, progress: int, message: str) -> None:
    job.progress = progress
    job.message = message
    job.touch()


def _ensure_file_exists(path: str) -> None:
    if not path:
        raise NonRetryableJobError("No input file path provided")

    if not os.path.exists(path):
        raise NonRetryableJobError(f"Input file not found: {path}")

    if os.path.getsize(path) == 0:
        raise NonRetryableJobError(f"Input file is empty: {path}")


def _ensure_models_exist() -> None:
    missing = [p for p in (PROTOTXT, MODEL) if not os.path.exists(p)]
    if missing:
        raise NonRetryableJobError(
            "MobileNet-SSD model files are missing: "
            + ", ".join(missing)
            + ". Please download them as described in the README."
        )


def _get_detector():
    global _detector

    _ensure_models_exist()

    if _detector is None:
        _detector = ObjectDetector(PROTOTXT, MODEL)
    return _detector


def _process_video_sync(file_path: str, filename: str) -> dict:
    detector = _get_detector()

    with SessionLocal() as db:
        pipeline_result = process_video_frames(file_path, detector)
        keyframes = pipeline_result["keyframes"]
        detections = pipeline_result["objects"]

        summary_text = generate_video_summary(detections)
        embedding_bytes = generate_video_embedding(summary_text)

        video_record = repository.save_video(
            db,
            filename=filename,
            keyframes=keyframes,
            detected_objects=detections,
            summary=summary_text,
            embedding=embedding_bytes,
        )

        return {
            "filename": video_record.filename,
            "keyframes_count": len(keyframes),
            "objects_detected_count": len(detections),
            "summary": summary_text,
            "embedding_length": len(embedding_bytes),
            "message": "Video processed successfully",
        }


def _process_audio_sync(audio_bytes: bytes, filename: str) -> dict:
    # Preprocess: format conversion + normalization + resample to 16k mono
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    audio = audio.set_channels(1).set_frame_rate(16000)
    if audio.max_dBFS != float("-inf"):
        audio = audio.apply_gain(-audio.max_dBFS)

    samples = audio.get_array_of_samples()
    tmp_path = f"/tmp/{filename}.wav"
    audio.export(tmp_path, format="wav")

    # Transcribe with whisper-tiny
    result = WHISPER_MODEL.transcribe(tmp_path)
    transcription_text = (result.get("text") or "").strip()

    # Segments with timestamps + confidence
    segments = []
    for seg in result.get("segments", []):
        segments.append(
            {
                "start": seg.get("start", 0.0),
                "end": seg.get("end", 0.0),
                "text": seg.get("text", ""),
                # avg_logprob is commonly present; keep it as “confidence-like”
                "confidence": seg.get("avg_logprob", 1.0),
            }
        )

    # Fallback if no segments
    if not segments:
        duration = len(samples) / 16000.0
        segments = [
            {
                "start": 0.0,
                "end": float(duration),
                "text": transcription_text,
                "confidence": 1.0,
            }
        ]

    # Embedding
    embedding_vector = EMBED_MODEL.encode(transcription_text)
    embedding_bytes = np.asarray(embedding_vector, dtype=np.float32).tobytes()

    with SessionLocal() as db:
        record = repository.save_transcription(
            db,
            filename=filename,
            text=transcription_text,
            timestamps=segments,
            embedding=embedding_bytes,
        )

    return {
        "filename": filename,
        "transcription_id": record.id,
        "text": transcription_text,
        "segments": segments,
        "message": "Audio processed successfully",
        "embedding_length": len(embedding_vector),
    }


async def process_job(job: Job) -> None:
    if job.type == "video":
        file_path = job.payload["file_path"]

        _ensure_file_exists(file_path)
        _ensure_models_exist()

        _set(job, 5, "Preparing video processing")
        file_path = job.payload["file_path"]
        filename = job.payload["filename"]

        _set(job, 15, "Extracting keyframes")
        # inside _process_video_sync you can keep current code,
        # but ideally split it so you can update progress at milestones

        job.result = await asyncio.to_thread(_process_video_sync, file_path, filename)
        _set(job, 95, "Finalizing")
        return

    if job.type == "audio":
        audio_bytes = job.payload.get("audio_bytes")
        filename = job.payload.get("filename")

        if not audio_bytes:
            raise NonRetryableJobError("Audio payload is empty")

        _set(job, 5, "Preparing audio processing")
        audio_bytes = job.payload["audio_bytes"]
        filename = job.payload["filename"]

        _set(job, 20, "Preprocessing audio")
        job.result = await asyncio.to_thread(_process_audio_sync, audio_bytes, filename)
        _set(job, 95, "Finalizing")
        return

    raise ValueError(f"Unknown job type: {job.type}")
