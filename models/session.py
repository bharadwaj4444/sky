# sky/models/session.py

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass(frozen=True)
class CaptureSession:

    session_id: str
    directory: Path
    started_at: datetime