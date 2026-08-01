import threading
import time
import os

class TimelapseManager:
    def __init__(self, camera, processor, sessions_dir, batch_size=10):
        self.camera = camera
        self.processor = processor
        self.sessions_dir = sessions_dir
        self.batch_size = batch_size
        self.is_running = False
        self.images_taken = 0
        self.thread = None
        self.current_session_dir = None

    def start(self):
        if not self.is_running:
            session_name = f"session_{int(time.time())}"
            self.current_session_dir = os.path.join(self.sessions_dir, session_name)
            os.makedirs(self.current_session_dir, exist_ok=True)
            print(f"Started new session: {session_name}")

            self.is_running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.is_running = False

    def update_settings(self, batch_size):
        self.batch_size = int(batch_size)
        print(f"Settings updated: {self.batch_size} batch size.")

    def _loop(self):
        while self.is_running:
            filename = self.camera.take_photo(save_dir=self.current_session_dir)
            if filename:
                self.images_taken += 1
                print(f"Captured {self.images_taken}/{self.batch_size}")

            if self.images_taken >= self.batch_size:
                print("Batch complete. Triggering processor for this session...")
                threading.Thread(
                    target=self.processor.align_and_stack, 
                    args=(self.current_session_dir,), 
                    daemon=True
                ).start()
                self.images_taken = 0 
            
            # Tiny fixed hardware buffer to prevent SD card write crashes
            time.sleep(0.5)
            
        print("Timelapse stopped.")