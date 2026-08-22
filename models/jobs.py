# sky/models/jobs.py

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StackJob:

    session_id: str
    batch_number: int
    input_files: tuple[Path, ...]
    output_path: Path