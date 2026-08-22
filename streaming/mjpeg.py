import logging
import cv2

logger = logging.getLogger(__name__)


class MjpegStreamer:

    def __init__(
        self,
        frame_store,
        jpeg_quality=85,
    ):
        self.frame_store = frame_store
        self.jpeg_quality = jpeg_quality

    def stream(self):

        logger.info("MJPEG client connected")

        last_sequence = -1

        while True:

            frame = self.frame_store.wait_for_newer_than(
                last_sequence,
                timeout=5,
            )

            if frame is None:

                logger.warning(
                    "No new frame available"
                )

                continue

            last_sequence = frame.sequence

            logger.info(
                "Streaming frame %s",
                frame.sequence,
            )

            success, encoded = cv2.imencode(
                ".jpg",
                frame.image,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    self.jpeg_quality,
                ],
            )

            if not success:

                logger.warning(
                    "JPEG encoding failed"
                )

                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + encoded.tobytes()
                + b"\r\n"
            )