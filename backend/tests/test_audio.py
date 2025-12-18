import numpy as np


def test_audio_transcription_accuracy_formats_segments(monkeypatch, tmp_path):
    """
    Unit-test the transcription pipeline logic without invoking real Whisper or decoding real audio.
    Verifies: segments mapping + embedding bytes + message fields.
    """
    # Import after stubs are in place (from conftest)
    from app.processing import processor as processor_module

    # Patch read_file_as_bytes to avoid filesystem IO
    monkeypatch.setattr(
        processor_module,
        "read_file_as_bytes",
        lambda p: b"fake-audio-bytes",
        raising=True,
    )

    # Fake AudioSegment-like object
    class FakeAudio:
        max_dBFS = -3.0

        def set_channels(self, n):
            return self

        def set_frame_rate(self, r):
            return self

        def apply_gain(self, g):
            return self

        def get_array_of_samples(self):
            # 1 second @ 16k
            return [0] * 16000

        def export(self, path, format="wav"):
            # Write a small file to satisfy transcribe(tmp_path)
            with open(path, "wb") as f:
                f.write(b"RIFF....WAVEfmt ")

    # Patch pydub.AudioSegment.from_file to return our fake
    monkeypatch.setattr(
        processor_module.AudioSegment,
        "from_file",
        lambda *args, **kwargs: FakeAudio(),
        raising=True,
    )

    # Patch WHISPER_MODEL.transcribe with deterministic output
    processor_module.WHISPER_MODEL.transcribe = lambda p: {
        "text": "hello world",
        "segments": [
            {"start": 0.0, "end": 0.5, "text": "hello", "avg_logprob": -0.1},
            {"start": 0.5, "end": 1.0, "text": "world", "avg_logprob": -0.2},
        ],
    }

    # Patch embedding model
    processor_module.EMBED_MODEL.encode = lambda t: np.array(
        [1, 2, 3, 4], dtype=np.float32
    )

    # Capture what gets saved to DB (especially embedding bytes) without touching a real database
    captured = {}

    class _DummySession:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        processor_module, "SessionLocal", lambda: _DummySession(), raising=True
    )

    def _fake_save_transcription(db, filename, text, timestamps, embedding):
        captured["filename"] = filename
        captured["text"] = text
        captured["timestamps"] = timestamps
        captured["embedding"] = embedding

        class _Rec:
            id = 123

        return _Rec()

    monkeypatch.setattr(
        processor_module.repository,
        "save_transcription",
        _fake_save_transcription,
        raising=True,
    )

    # Create dummy file path
    p = tmp_path / "a.wav"
    p.write_bytes(b"x")

    out = processor_module._process_audio_sync(str(p), filename="a")

    assert out["text"].strip() == "hello world"
    assert out["segments"][0]["text"].strip() == "hello"
    assert out["segments"][0]["confidence"] == -0.1
    assert out["embedding_length"] == 4
    assert isinstance(captured["embedding"], (bytes, bytearray))
    assert len(captured["embedding"]) == 4 * 4  # 4 float32 values
