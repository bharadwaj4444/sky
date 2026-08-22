import logging
from pathlib import Path

from camera.backend import CameraBackend
from camera.frame_store import FrameStore
from camera.capture_service import CaptureService

from processing.orb_alignment import OrbAligner
from processing.stacking import MeanStacker
from processing.stretch import AstroStretch
from processing.processor import ImageProcessor
from processing.worker import StackWorker

from storage.repository import StorageRepository
from streaming.mjpeg import MjpegStreamer
from timelapse.manager import TimelapseManager

from camera.gstreamer import GStreamerCamera

from web.app import create_app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main():

    worker = None
    timelapse = None
    capture_service = None

    logger.info("Starting ..")

    try:
        logger.info("Creating FrameStore")
        frame_store = FrameStore()

        logger.info("Creating CameraBackend")
        camera = CameraBackend(
            device="/dev/video0",
            width=1920,
            height=1080,
            fps=30,
        )

        logger.info("Creating CaptureService")
        capture_service = CaptureService(
            camera,
            frame_store,
        )

        logger.info("Creating StorageRepository")
        storage = StorageRepository(
            Path("/mnt/usb_drive/astrophotography")
        )

        logger.info("Creating ImageProcessor")

        processor = ImageProcessor(
            aligner=OrbAligner(),
            stacker=MeanStacker(),
            stretcher=AstroStretch(
                black_percentile=1.0,
                white_percentile=99.8,
                stretch_factor=5.0,
            ),
        )

        logger.info("Creating StackWorker")

        worker = StackWorker(
            processor=processor,
            max_queue_size=3,
        )

        logger.info("Creating TimelapseManager")

        timelapse = TimelapseManager(
            frame_store=frame_store,
            storage=storage,
            worker=worker,
        )

        logger.info("Creating MjpegStreamer")

        streamer = MjpegStreamer(
            frame_store=frame_store,
        )

        logger.info("Creating Flask application")

        app = create_app(
            timelapse=timelapse,
            streamer=streamer,
            capture_service=capture_service,
        )

        logger.info("Starting StackWorker")
        worker.start()

        logger.info("Starting Camera")
        #capture_service.start()

        logger.info("Camera started")

        logger.info(
            "Starting web server on http://0.0.0.0:5000"
        )

        app.run(
            host="0.0.0.0",
            port=5000,
            threaded=True,
            debug=False,
            use_reloader=False,
        )

    except Exception:
        logger.exception("FATAL ERROR")

    finally:

        logger.info("Shutting down...")
        
        if timelapse is not None:
            timelapse.stop()

        if worker is not None:
            worker.stop()

        if capture_service is not None:
            capture_service.stop()


if __name__ == "__main__":
    main()