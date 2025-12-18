import sys
import types
from pathlib import Path

import numpy as np
import pytest

# Ensure repo root is on sys.path so `import app` works when running pytest from any cwd
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session", autouse=True)
def _stub_heavy_ml_modules():
    """
    Prevent tests from downloading/initializing heavy ML models at import time.
    We stub `sentence_transformers` and `whisper` before app modules are imported.
    """
    # ---- sentence_transformers stub ----
    if "sentence_transformers" not in sys.modules:
        st_mod = types.ModuleType("sentence_transformers")

        class DummySentenceTransformer:
            def __init__(self, *args, **kwargs):
                pass

            def encode(self, text):
                # Deterministic 4-d embedding; supports str or list[str]
                if isinstance(text, (list, tuple)):
                    # Return matrix
                    return np.stack([self.encode(t) for t in text], axis=0)
                # simple hash -> stable embedding
                h = sum(ord(c) for c in str(text)) % 97
                vec = np.array([h, h + 1, h + 2, h + 3], dtype=np.float32)
                return vec

        st_mod.SentenceTransformer = DummySentenceTransformer
        sys.modules["sentence_transformers"] = st_mod

    # ---- whisper stub ----
    if "whisper" not in sys.modules:
        w_mod = types.ModuleType("whisper")

        class DummyWhisperModel:
            def transcribe(self, path):
                return {"text": "dummy", "segments": []}

        def load_model(name="tiny", *args, **kwargs):
            return DummyWhisperModel()

        w_mod.load_model = load_model
        sys.modules["whisper"] = w_mod

    yield


@pytest.fixture()
def db_session(tmp_path, monkeypatch):
    """
    Provide a temporary SQLite DB and patch the app's SessionLocal/get_session to use it.
    """
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import after stubs are in place
    from app.db import database as database_module
    from app.db import deps as deps_module
    from app.db.database import Base

    # Patch globals used by app
    monkeypatch.setattr(database_module, "engine", engine, raising=True)
    monkeypatch.setattr(
        database_module, "SessionLocal", TestingSessionLocal, raising=True
    )
    monkeypatch.setattr(deps_module, "SessionLocal", TestingSessionLocal, raising=True)

    # Also patch helper
    def _get_session():
        return TestingSessionLocal()

    monkeypatch.setattr(database_module, "get_session", _get_session, raising=True)

    # Create schema
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
