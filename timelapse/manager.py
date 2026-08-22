# sky/timelapse/manager.py

import threading
import time

from timelapse.batch_builder import BatchBuilder


class TimelapseManager:

    def __init__(
        self,
        frame_store,
        storage,
        worker,
    ):
        self.frame_store = frame_store
        self.storage = storage
        self.worker = worker

        self._running = False
        self._thread = None

    def get_status(self):

        return {
            "running": self._running,
            "session_id": (
                self._session.session_id
                if self._session
                else None
            ),
            "capture_interval":
                self._capture_interval,
            "batch_size":
                self._batch_size,
        }

    def start(
        self,
        capture_interval: float,
        batch_size: int,
    ):

        if self._running:
            raise RuntimeError(
                "Timelapse already running"
            )

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            args=(
                capture_interval,
                batch_size,
            ),
            daemon=True,
        )

        self._thread.start()

    def stop(self):

        self._running = False

        if self._thread:
            self._thread.join(timeout=5)

    def _run(
        self,
        capture_interval,
        batch_size,
    ):

        session = self.storage.create_session()

        batch_builder = BatchBuilder(
            session,
            batch_size,
        )

        last_sequence = -1

        next_capture = time.monotonic()

        while self._running:

            now = time.monotonic()

            if now < next_capture:
                time.sleep(
                    min(
                        0.05,
                        next_capture - now,
                    )
                )
                continue

            frame = self.frame_store.wait_for_newer_than(
                last_sequence,
                timeout=2,
            )

            if frame is None:
                continue

            last_sequence = frame.sequence

            path = self.storage.save_raw_frame(
                session,
                frame,
            )

            job = batch_builder.add(path)

            if job is not None:
                self.worker.submit(job)

            next_capture += capture_interval