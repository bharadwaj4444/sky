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

        logger.info("Opening camera")

        self.camera.open()

        logger.info("Camera opened successfully")

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            name="camera-capture",
            daemon=True,
        )

        self._thread.start()

        logger.info("Capture thread started")

    def stop(self):

        logger.info("Stopping capture service")

        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=5)

        self.camera.close()

    def _run(self):

        logger.info("Capture loop started")

        while self._running:

            try:
                success, image = self.camera.read()

                logger.info(
                    "camera.read(): success=%s image=%s",
                    success,
                    None if image is None else image.shape,
                )

                if not success or image is None:
                    logger.warning("Failed to capture frame")
                    time.sleep(0.1)
                    continue

                self._sequence += 1

                frame = Frame(
                    image=image,
                    sequence=self._sequence,
                    captured_at=datetime.now(timezone.utc),
                )

                self.frame_store.publish(frame)

                if self._sequence == 1:
                    logger.info(
                        "First frame published: shape=%s",
                        image.shape,
                    )

            except Exception:
                logger.exception("Capture loop error")
                time.sleep(1)

        logger.info("Capture loop stopped")