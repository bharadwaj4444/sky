# sky/storage/repository.py

from pathlib import Path

import cv2

from models.frame import Frame
from models.session import CaptureSession


class StorageRepository:

    def __init__(self, base_directory: Path):
        self.base_directory = base_directory

    def create_session(self) -> CaptureSession:

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        session_id = now.strftime("%Y%m%d_%H%M%S")

        session_dir = self.base_directory / session_id

        (session_dir / "raw").mkdir(
            parents=True,
            exist_ok=False,
        )

        (session_dir / "stacks").mkdir()
        (session_dir / "video").mkdir()

        return CaptureSession(
            session_id=session_id,
            directory=session_dir,
            started_at=now,
        )

    def save_raw_frame(
        self,
        session: CaptureSession,
        frame: Frame,
    ) -> Path:

        path = (
            session.directory
            / "raw"
            / f"frame_{frame.sequence:09d}.jpg"
        )

        success = cv2.imwrite(
            str(path),
            frame.image,
        )

        if not success:
            raise RuntimeError(
                f"Unable to save frame: {path}"
            )

        return path