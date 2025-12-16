import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional

JobType = Literal["video", "audio"]
JobStatus = Literal["queued", "running", "retrying", "succeeded", "failed"]


@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: JobType = "video"
    payload: dict[str, Any] = field(default_factory=dict)

    status: JobStatus = "queued"
    progress: int = 0
    message: str = "Queued"

    attempt: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    result: Optional[Any] = None

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()
