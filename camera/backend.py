import logging

import cv2


logger = logging.getLogger(__name__)


class CameraBackend:

    def __init__(
        self,
        device="/dev/video0",
        width=1920,
        height=1080,
        fps=30,
    ):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.capture = None

    def open(self):

        logger.info(
            "Opening camera: %s",
            self.device,
        )

        self.capture = cv2.VideoCapture(
            self.device,
            cv2.CAP_V4L2,
        )

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Unable to open {self.device}"
            )

        # Set FOURCC BEFORE resolution/FPS.
        self.capture.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"MJPG"),
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width,
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height,
        )

        self.capture.set(
            cv2.CAP_PROP_FPS,
            self.fps,
        )

        logger.info(
            "Actual: %.0fx%.0f @ %.2f FPS",
            self.capture.get(
                cv2.CAP_PROP_FRAME_WIDTH
            ),
            self.capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            ),
            self.capture.get(
                cv2.CAP_PROP_FPS
            ),
        )

    def read(self):

        if self.capture is None:
            raise RuntimeError(
                "Camera is not open"
            )

        return self.capture.read()

    def close(self):

        if self.capture is not None:

            logger.info("Releasing camera")

            self.capture.release()

            self.capture = None