# sky/processing/stacking.py

import numpy as np


class MeanStacker:

    def stack(self, images):

        if not images:
            raise ValueError(
                "No images supplied for stacking"
            )

        accumulator = images[0].astype(
            np.float32
        )

        accepted = 1

        for image in images[1:]:

            accumulator += image.astype(
                np.float32
            )

            accepted += 1

        result = accumulator / accepted

        return np.clip(
            result,
            0,
            255,
        ).astype(np.uint8)