# sky/config.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CameraConfig:
    device_index: int = 0
    width: int = 1920
    height: int = 1080
    fps: int = 30


@dataclass(frozen=True)
class TimelapseConfig:
    capture_interval: float = 0.5
    batch_size: int = 20
    queue_size: int = 3


@dataclass(frozen=True)
class AppConfig:
    camera: CameraConfig
    timelapse: TimelapseConfig