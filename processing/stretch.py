import cv2
import numpy as np


class AstroStretch:
    """
    Simple percentile-based astronomical image stretch.

    Pipeline:
        input
          ↓
        percentile clipping
          ↓
        normalization
          ↓
        asinh stretch
          ↓
        uint8 output
    """

    def __init__(
        self,
        black_percentile: float = 1.0,
        white_percentile: float = 99.8,
        stretch_factor: float = 5.0,
    ):
        if not 0 <= black_percentile < white_percentile <= 100:
            raise ValueError(
                "Percentiles must satisfy "
                "0 <= black < white <= 100"
            )

        if stretch_factor <= 0:
            raise ValueError(
                "stretch_factor must be greater than zero"
            )

        self.black_percentile = black_percentile
        self.white_percentile = white_percentile
        self.stretch_factor = stretch_factor

    def apply(self, image: np.ndarray) -> np.ndarray:

        if image is None:
            raise ValueError("Image cannot be None")

        if image.size == 0:
            raise ValueError("Image cannot be empty")

        # Convert to float before processing.
        working = image.astype(np.float32)

        # Calculate luminance from the image.
        if len(working.shape) == 3:
            gray = cv2.cvtColor(
                working,
                cv2.COLOR_BGR2GRAY,
            )
        else:
            gray = working

        black_point = np.percentile(
            gray,
            self.black_percentile,
        )

        white_point = np.percentile(
            gray,
            self.white_percentile,
        )

        denominator = white_point - black_point

        # Prevent division by zero on nearly uniform images.
        if denominator <= 1e-6:
            return image.copy()

        # Normalize to 0–1.
        normalized = (
            working - black_point
        ) / denominator

        normalized = np.clip(
            normalized,
            0.0,
            1.0,
        )

        # Asinh stretch.
        stretched = np.arcsinh(
            normalized * self.stretch_factor
        ) / np.arcsinh(
            self.stretch_factor
        )

        result = stretched * 255.0

        return np.clip(
            result,
            0,
            255,
        ).astype(np.uint8)