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

    def start(self):

        if self._running:
            return

        self.camera.open()

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            name="camera-capture",
            daemon=True,
        )

        self._thread.start()

        logger.info(
            "Capture service started"
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

        logger.info(
            "Capture loop started"
        )

        while self._running:

            try:

                image = self.camera.read()

                if image is None:

                    logger.warning(
                        "Camera returned no frame"
                    )

                    time.sleep(0.05)
                    continue

                self._sequence += 1

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
                    "Capture loop failed"
                )

                time.sleep(1)

        logger.info(
            "Capture loop stopped"
        )