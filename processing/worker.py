import logging
import queue
import threading


logger = logging.getLogger(__name__)


class StackWorker:

    def __init__(
        self,
        processor,
        max_queue_size=3,
    ):
        self.processor = processor

        self._queue = queue.Queue(
            maxsize=max_queue_size
        )

        self._running = False
        self._thread = None

    def start(self):

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            name="stack-worker",
            daemon=True,
        )

        self._thread.start()

        logger.info("Stack worker started")

    def submit(self, job):

        if not self._running:
            raise RuntimeError(
                "Stack worker is not running"
            )

        self._queue.put(job)

    def stop(self):

        if not self._running:
            return

        logger.info("Stopping stack worker")

        self._running = False

        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass

        if self._thread is not None:
            self._thread.join(timeout=10)

    def _run(self):

        logger.info("Stack worker loop started")

        while True:

            job = self._queue.get()

            try:

                if job is None:
                    break

                logger.info(
                    "Processing stack job %s",
                    job.batch_number,
                )

                self.processor.process(job)

            except Exception:

                logger.exception(
                    "Stack processing failed"
                )

            finally:

                self._queue.task_done()

        logger.info("Stack worker stopped")