# sky/processing/processor.py

import cv2

from models.jobs import StackJob


class ImageProcessor:

    def __init__(
        self,
        aligner,
        stacker,
        stretcher,
    ):
        self.aligner = aligner
        self.stacker = stacker
        self.stretcher = stretcher

    def process(self, job: StackJob):

        images = []

        reference = cv2.imread(
            str(job.input_files[0])
        )

        if reference is None:
            raise RuntimeError(
                "Unable to load reference frame"
            )

        images.append(reference)

        for path in job.input_files[1:]:

            image = cv2.imread(str(path))

            if image is None:
                continue

            aligned = self.aligner.align(
                image,
                reference,
            )

            if aligned is None:
                continue

            images.append(aligned)

        stacked = self.stacker.stack(images)

        result = self.stretcher.apply(stacked)

        success = cv2.imwrite(
            str(job.output_path),
            result,
        )

        if not success:
            raise RuntimeError(
                f"Unable to save {job.output_path}"
            )

        return {
            "input_count": len(job.input_files),
            "accepted_count": len(images),
            "output": str(job.output_path),
        }