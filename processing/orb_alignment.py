import cv2
import numpy as np


class OrbAligner:

    def align(
        self,
        image,
        reference,
    ):

        gray_img = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        gray_ref = cv2.cvtColor(
            reference,
            cv2.COLOR_BGR2GRAY,
        )

        orb = cv2.ORB_create(
            nfeatures=1000,
        )

        kp1, des1 = orb.detectAndCompute(
            gray_img,
            None,
        )

        kp2, des2 = orb.detectAndCompute(
            gray_ref,
            None,
        )

        if des1 is None or des2 is None:
            return None

        matcher = cv2.BFMatcher(
            cv2.NORM_HAMMING,
            crossCheck=True,
        )

        matches = matcher.match(
            des1,
            des2,
        )

        if len(matches) < 10:
            return None

        matches = sorted(
            matches,
            key=lambda m: m.distance,
        )

        matches = matches[
            :max(10, int(len(matches) * 0.2))
        ]

        source = np.float32([
            kp1[m.queryIdx].pt
            for m in matches
        ])

        destination = np.float32([
            kp2[m.trainIdx].pt
            for m in matches
        ])

        matrix, inliers = cv2.estimateAffinePartial2D(
            source,
            destination,
            method=cv2.RANSAC,
        )

        if matrix is None:
            return None

        height, width = reference.shape[:2]

        return cv2.warpAffine(
            image,
            matrix,
            (width, height),
        )