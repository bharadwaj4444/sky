import threading

from models.frame import Frame


class FrameStore:

    def __init__(self):
        self._condition = threading.Condition()
        self._latest: Frame | None = None

    def publish(self, frame: Frame) -> None:

        with self._condition:

            self._latest = frame

            self._condition.notify_all()

    def get_latest(self) -> Frame | None:

        with self._condition:

            return self._latest

    def wait_for_newer_than(
        self,
        sequence: int,
        timeout: float | None = None,
    ) -> Frame | None:

        with self._condition:

            def has_new_frame():
                return (
                    self._latest is not None
                    and self._latest.sequence > sequence
                )

            if not has_new_frame():

                self._condition.wait_for(
                    has_new_frame,
                    timeout=timeout,
                )

            if has_new_frame():
                return self._latest

            return None