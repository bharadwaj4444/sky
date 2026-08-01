import cv2
import time
import os
import numpy as np

class CameraController:
    def __init__(self, capture_dir):
        self.capture_dir = capture_dir
        self.latest_frame = None
        self.is_recording = False
        self.video_writer = None
        
        # PTZ and UI State
        self.zoom = 1.0
        self.pan_x = 0.5
        self.pan_y = 0.5
        self.show_histogram = False
        
        self.capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_FPS, 30)

        self.properties = {
            "exposure": cv2.CAP_PROP_EXPOSURE,
            "auto_exposure": cv2.CAP_PROP_AUTO_EXPOSURE,
            "gain": cv2.CAP_PROP_GAIN,
        }

    def update_ptz(self, zoom, x, y):
        self.zoom = max(1.0, float(zoom))
        self.pan_x = max(0.0, min(1.0, float(x)))
        self.pan_y = max(0.0, min(1.0, float(y)))

    def draw_histogram(self, frame):
        """Draws a live RGB histogram in the bottom right corner."""
        h, w = frame.shape[:2]
        hist_w, hist_h = 256, 100
        x_offset, y_offset = w - hist_w - 20, h - hist_h - 20
        
        # Draw a semi-transparent black background box for the graph
        overlay = frame.copy()
        cv2.rectangle(overlay, (x_offset, y_offset), (x_offset + hist_w, y_offset + hist_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Blue, Green, Red colors for OpenCV
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)] 
        
        for i, col in enumerate(colors):
            hist = cv2.calcHist([frame], [i], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, hist_h, cv2.NORM_MINMAX)
            
            # Fast numpy math to draw the graph lines
            pts = np.column_stack((np.arange(256), hist_h - np.round(hist).flatten()))
            pts += np.array([x_offset, y_offset])
            cv2.polylines(frame, [np.int32(pts)], False, col, 1)
            
        return frame

    def get_frame_bytes(self):
        ret, frame = self.capture.read()
        if not ret: return None
        
        # Save the FULL uncropped frame for raw captures/timelapse
        self.latest_frame = frame.copy()
        
        if self.is_recording and self.video_writer is not None:
            self.video_writer.write(frame)
            
        display_frame = frame.copy()
        
        # Apply digital zoom for live feed
        if self.zoom > 1.0:
            h, w = display_frame.shape[:2]
            new_w, new_h = int(w / self.zoom), int(h / self.zoom)
            
            center_x, center_y = int(w * self.pan_x), int(h * self.pan_y)
            x1 = max(0, center_x - new_w // 2)
            y1 = max(0, center_y - new_h // 2)
            x2, y2 = min(w, x1 + new_w), min(h, y1 + new_h)
            
            if x2 - x1 < new_w: x1 = max(0, x2 - new_w)
            if y2 - y1 < new_h: y1 = max(0, y2 - new_h)
                
            cropped = display_frame[y1:y2, x1:x2]
            display_frame = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_NEAREST)

        # Draw the histogram overlay if toggled on
        if self.show_histogram:
            display_frame = self.draw_histogram(display_frame)

        success, buffer = cv2.imencode('.jpg', display_frame)
        return buffer.tobytes() if success else None

    def apply_settings(self, settings_dict):
        for name, val in settings_dict.items():
            if name in self.properties:
                self.capture.set(self.properties[name], float(val))

    def get_settings(self):
        return {name: self.capture.get(prop) for name, prop in self.properties.items()}

    def take_photo(self, save_dir=None):
        if self.latest_frame is None: return None
        target_dir = save_dir if save_dir else self.capture_dir
        filename = f"manual_{int(time.time())}.jpg" if save_dir else f"raw_{int(time.time())}.jpg"
        filepath = os.path.join(target_dir, filename)
        cv2.imwrite(filepath, self.latest_frame)
        return filename

    def start_recording(self, save_dir=None):
        if not self.is_recording and self.latest_frame is not None:
            target_dir = save_dir if save_dir else self.capture_dir
            filename = f"manual_vid_{int(time.time())}.mp4"
            filepath = os.path.join(target_dir, filename)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            h, w = self.latest_frame.shape[:2]
            self.video_writer = cv2.VideoWriter(filepath, fourcc, 30.0, (w, h))
            self.is_recording = True
            return filename
        return None

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

    def release(self):
        self.stop_recording()
        self.capture.release()
