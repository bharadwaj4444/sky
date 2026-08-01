import cv2
import numpy as np
import glob
import os
import time

class MediaProcessor:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def astro_stretch(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        p_black, p_white = np.percentile(v, (2, 99.5))
        v_stretched = np.clip((v - p_black) * (255.0 / (p_white - p_black)), 0, 255).astype(np.uint8)
        gamma = 1.3
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        v_gamma = cv2.LUT(v_stretched, table)
        hsv_stretched = cv2.merge([h, s, v_gamma])
        return cv2.cvtColor(hsv_stretched, cv2.COLOR_HSV2BGR)

    def align_and_stack(self, session_dir):
        """Stacks raw images in a specific session folder without deleting them."""
        search_pattern = os.path.join(session_dir, 'raw_*.jpg')
        image_files = sorted(glob.glob(search_pattern))
        
        if len(image_files) < 2:
            print("Processor: Not enough images to stack in this session.")
            return False

        print(f"Processor: Stacking {len(image_files)} images in {os.path.basename(session_dir)}...")
        
        # Look for master dark in the base storage directory
        master_dark_path = os.path.join(self.base_dir, 'master_dark.jpg')
        master_dark = cv2.imread(master_dark_path) if os.path.exists(master_dark_path) else None

        reference_image = cv2.imread(image_files[0])
        if master_dark is not None:
            reference_image = cv2.subtract(reference_image, master_dark)

        stacked_image = np.zeros_like(reference_image, dtype=np.float32)
        stacked_image += reference_image.astype(np.float32)
        
        orb = cv2.ORB_create(5000)
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        keypoints_ref, desc_ref = orb.detectAndCompute(cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY), None)

        for file in image_files[1:]:
            img = cv2.imread(file)
            if master_dark is not None: img = cv2.subtract(img, master_dark)

            kp_img, desc_img = orb.detectAndCompute(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), None)
            if desc_img is None or desc_ref is None: continue

            matches = sorted(matcher.match(desc_img, desc_ref), key=lambda x: x.distance)
            matches = matches[:int(len(matches) * 0.15)]
            
            if len(matches) > 10:
                pts1 = np.float32([kp_img[m.queryIdx].pt for m in matches])
                pts2 = np.float32([keypoints_ref[m.trainIdx].pt for m in matches])
                matrix, _ = cv2.estimateAffinePartial2D(pts1, pts2, method=cv2.RANSAC)
                if matrix is not None:
                    h_dim, w_dim = reference_image.shape[:2]
                    img = cv2.warpAffine(img, matrix, (w_dim, h_dim))
            
            stacked_image += img.astype(np.float32)

        stacked_image = np.clip(stacked_image / len(image_files), 0, 255).astype(np.uint8)
        final_image = self.astro_stretch(stacked_image)
        
        # Save the processed image directly into the session folder
        output_name = f"stacked_{int(time.time())}.jpg"
        cv2.imwrite(os.path.join(session_dir, output_name), final_image)
        print(f"Processor: Saved {output_name} to {os.path.basename(session_dir)}")

        # RAW IMAGES ARE NO LONGER DELETED HERE
        return True

    def generate_video(self, session_dir, fps=10):
        """Compiles only the stacked images in a specific session into an MP4."""
        search_pattern = os.path.join(session_dir, 'stacked_*.jpg')
        images = sorted(glob.glob(search_pattern))
        if len(images) < 2: return None
            
        print(f"Processor: Compiling video at {fps} FPS...")
        first_frame = cv2.imread(images[0])
        height, width = first_frame.shape[:2]
        
        output_name = f"timelapse_{int(time.time())}.mp4"
        output_path = os.path.join(session_dir, output_name)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, float(fps), (width, height))
        
        for img_path in images:
            video.write(cv2.imread(img_path))
        video.release()
        return output_name
