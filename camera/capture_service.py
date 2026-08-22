from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone

from models.frame import Frame


logger = logging.getLogger(__name__)


class CaptureService:

    def __init__(
        self,
        camera,
        frame_store,
    ):
        self.camera = camera
        self.frame_store = frame_store

        self._running = False
        self._thread = None
        self._sequence = 0

    @property
    def is_running(self) -> bool:
        return self._running


    @property
    def sequence(self) -> int:
        return self._sequence

    def start(self):

        if self._running:
            return
        
        logger.info("CAPTURE: start() called")

        self.camera.open()

        logger.info(
            "CAPTURE: camera opened = %s",
            self.camera.is_open,
        )

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            name="camera-capture",
            daemon=True,
        )

        self._thread.start()

        logger.info(
            "CAPTURE: thread started, alive=%s",
            self._thread.is_alive(),
        )

    def stop(self):

        if not self._running:
            return

        logger.info(
            "Stopping capture service"
        )

        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=5)

        self.camera.close()

        self._thread = None

    def _run(self):

        logger.info("CAPTURE: _run() ENTERED")

        while self._running:

            try:

                image = self.camera.read()

                logger.info(
                    "CAPTURE: read() -> %s",
                    None if image is None else image.shape,
                )

                if image is None:

                    logger.warning(
                        "Camera returned no frame"
                    )

                    time.sleep(0.05)
                    continue

                self._sequence += 1

                logger.info(
                    "CAPTURE: publishing frame %d",
                    self._sequence,
                )

                frame = Frame(
                    image=image,
                    sequence=self._sequence,
                    captured_at=datetime.now(
                        timezone.utc
                    ),
                )

                self.frame_store.publish(frame)

                if self._sequence == 1:

                    logger.info(
                        "First frame captured: %s",
                        image.shape,
                    )

            except Exception:
                logger.exception(
                    "CAPTURE: exception in capture loop"
                )
                time.sleep(1)

        logger.info(
            "CAPTURE: capture loop stopped"
        )