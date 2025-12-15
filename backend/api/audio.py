import io

import numpy as np
import whisper
from db import repository
from db.deps import get_db
from fastapi import APIRouter, Depends, File, UploadFile
from pydub import AudioSegment
from sqlalchemy.orm import Session

router = APIRouter()

# Load Whisper tiny once
model = whisper.load_model("tiny")


@router.post("/process/audio")
async def process_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Read uploaded file
    audio_bytes = await file.read()

    # Convert any audio format to WAV 16kHz mono using Pydub
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    audio = audio.set_channels(1).set_frame_rate(16000)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0

    # Save temporary WAV for whisper
    tmp_path = f"/tmp/{file.filename}"
    audio.export(tmp_path, format="wav")

    # Transcribe with Whisper
    result = model.transcribe(tmp_path)
    transcription_text = result["text"]

    # Extract segments with timestamps and confidence
    segments = []
    for seg in result.get("segments", []):
        segments.append(
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "confidence": seg.get(
                    "avg_logprob", 1.0
                ),  # optional, average log probability
            }
        )

    # Fallback: if no segments, use full audio as one
    if not segments:
        duration = len(samples) / 16000
        segments = [
            {
                "start": 0.0,
                "end": duration,
                "text": transcription_text,
                "confidence": 1.0,
            }
        ]

    # Save to DB
    record = repository.save_transcription(
        db, file.filename, transcription_text, segments
    )

    return {
        "filename": file.filename,
        "transcription_id": record.id,
        "text": transcription_text,
        "segments": segments,
        "message": "Audio processed successfully",
    }


@router.get("/transcriptions")
def get_transcriptions(db: Session = Depends(get_db)):
    return repository.get_transcriptions(db)
