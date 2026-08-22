from __future__ import annotations

import logging

import cv2
import numpy as np


logger = logging.getLogger(__name__)


class GStreamerCamera:

    def __init__(
        self,
        device: str = "/dev/video0",
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
    ):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps

        self._capture: cv2.VideoCapture | None = None

    def _build_pipeline(self) -> str:
        return (
            f"v4l2src device={self.device} ! "
            f"image/jpeg,"
            f"width={self.width},"
            f"height={self.height},"
            f"framerate={self.fps}/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink "
            "drop=true "
            "max-buffers=1 "
            "sync=false"
        )

    def open(self) -> None:

        if self._capture is not None:
            return

        pipeline = self._build_pipeline()

        logger.info(
            "Opening camera: %s",
            pipeline,
        )

        capture = cv2.VideoCapture(
            pipeline,
            cv2.CAP_GSTREAMER,
        )

        if not capture.isOpened():
            capture.release()

            raise RuntimeError(
                f"Unable to open camera: {self.device}"
            )

        self._capture = capture

        logger.info(
            "Camera opened successfully"
        )

    def read(self) -> np.ndarray | None:

        if self._capture is None:
            raise RuntimeError(
                "Camera is not open"
            )

        success, frame = self._capture.read()

        if not success or frame is None:
            return None

        return frame

    def close(self) -> None:

        capture = self._capture
        self._capture = None

        if capture is not None:
            logger.info("Closing camera")
            capture.release()

    @property
    def is_open(self) -> bool:
        return self._capture is not None