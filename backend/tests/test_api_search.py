import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient


class DummyQueue:
    def __init__(self):
        self.jobs = []
        self.enqueued = []

    def create_job(self, job):
        self.jobs.append(job)
        return job

    async def enqueue(self, job_id):
        self.enqueued.append(job_id)


def test_video_and_audio_endpoints_accept_upload(monkeypatch, tmp_path):
    """
    API endpoint test (video + audio): ensure we accept multipart upload, save file,
    create a job, and enqueue it.
    """
    from app.api import audio as audio_api
    from app.api import video as video_api

    app = FastAPI()
    app.state.queue = DummyQueue()
    app.include_router(video_api.router)
    app.include_router(audio_api.router)

    client = TestClient(app)

    # Video upload
    resp = client.post(
        "/process/video",
        files={"file": ("clip.mp4", b"fake-video", "video/mp4")},
    )

    assert resp.status_code == 202

    payload = resp.json()

    assert payload["status"] == "queued"
    assert "job_id" in payload

    # Audio upload
    resp2 = client.post(
        "/process/audio",
        files={"file": ("clip.wav", b"fake-audio", "audio/wav")},
    )

    assert resp2.status_code == 202
    payload2 = resp2.json()

    assert payload2["status"] == "queued"
    assert "job_id" in payload2


def test_search_across_media_types(db_session, monkeypatch):
    """
    Search should return both video and transcription results ranked by cosine similarity.
    """
    from app.db import models
    from app.search import unified_search as us

    # Patch search model encode -> deterministic query vector
    monkeypatch.setattr(
        us.model,
        "encode",
        lambda q: np.array([1, 0, 0, 0], dtype=np.float32),
        raising=False,
    )

    # Create two embeddings: video closer than transcription
    video_emb = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32).tobytes()
    tr_emb = np.array([0.2, 0.0, 0.0, 0.0], dtype=np.float32).tobytes()

    v = models.Video(
        filename="v.mp4",
        keyframes=[],
        detected_objects=[],
        summary="summary",
        embedding=video_emb,
    )
    t = models.Transcription(
        filename="a.wav", text="hello", timestamps=[], embedding=tr_emb
    )
    db_session.add_all([v, t])
    db_session.commit()

    results = us.search_media(query="anything", top_k=2)

    assert len(results) == 2
    assert results[0]["type"] == "video"
    assert results[1]["type"] == "transcription"
    assert results[0]["score"] >= results[1]["score"]
