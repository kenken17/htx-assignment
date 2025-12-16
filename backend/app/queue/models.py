import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional

JobType = Literal["video", "audio"]
JobStatus = Literal["queued", "running", "succeeded", "failed"]


@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: JobType = "video"
    payload: dict[str, Any] = field(default_factory=dict)

    status: JobStatus = "queued"
    progress: int = 0  # 0..100
    message: str = "Queued"
    error: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    result: Optional[Any] = None  # still useful, but endpoints won’t wait anymore

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()
