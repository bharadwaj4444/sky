# sky/timelapse/batch_builder.py

from pathlib import Path

from models.jobs import StackJob
from models.session import CaptureSession


class BatchBuilder:

    def __init__(
        self,
        session: CaptureSession,
        batch_size: int,
    ):
        self.session = session
        self.batch_size = batch_size

        self._files: list[Path] = []
        self._batch_number = 0

    def add(self, file: Path) -> StackJob | None:

        self._files.append(file)

        if len(self._files) < self.batch_size:
            return None

        self._batch_number += 1

        output_path = (
            self.session.directory
            / "stacks"
            / f"stack_{self._batch_number:06d}.jpg"
        )

        job = StackJob(
            session_id=self.session.session_id,
            batch_number=self._batch_number,
            input_files=tuple(self._files),
            output_path=output_path,
        )

        self._files.clear()

        return job