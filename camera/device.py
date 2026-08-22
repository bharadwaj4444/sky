import logging

import cv2


logger = logging.getLogger(__name__)


class CameraDevice:

    def __init__(
        self,
        device_index=0,
        width=1920,
        height=1080,
        fps=30,
    ):
        self.device_index = device_index
        self.width = width
        self.height = height
        self.fps = fps

        self.capture = None

    def open(self):

        logger.info(
            "Opening camera device %s",
            self.device_index,
        )

        self.capture = cv2.VideoCapture(
            self.device_index,
            cv2.CAP_V4L2,
        )

        logger.info("VideoCapture created")

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Unable to open camera {self.device_index}"
            )

        logger.info("Camera opened")

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

        self.capture.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"MJPG"),
        )

        logger.info(
            "Requested camera settings: "
            "%sx%s @ %s FPS",
            self.width,
            self.height,
            self.fps,
        )

        actual_width = self.capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )

        actual_height = self.capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )

        actual_fps = self.capture.get(
            cv2.CAP_PROP_FPS
        )

        logger.info(
            "Actual camera settings: "
            "%sx%s @ %s FPS",
            actual_width,
            actual_height,
            actual_fps,
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