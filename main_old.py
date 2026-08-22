import os
import argparse
from camera import CameraController
from processor import MediaProcessor
from timelapse import TimelapseManager
from server import SkyServer

def main():
    parser = argparse.ArgumentParser(description="Automated Sky Camera System")
    parser.add_argument(
        '-s', '--storage', 
        type=str, 
        default=os.path.abspath(os.path.dirname(__file__)),
        help="Base directory for saving media"
    )
    args = parser.parse_args()

    BASE_DIR = os.path.abspath(args.storage)
    
    print(f"\n--- Storage Configuration ---")
    print(f"Base Directory: {BASE_DIR}")
    
    # NEW: Replaced captures/processed with 'sessions'
    DIRS = {
        'sessions': os.path.join(BASE_DIR, 'sessions'),
        'manual': os.path.join(BASE_DIR, 'manual')
    }
    
    for name, path in DIRS.items():
        os.makedirs(path, exist_ok=True)
        print(f" -> {name.capitalize()} folder ready: {path}")
    print("-----------------------------\n")

    print("Initializing Sky Camera Modules...")

    # Initialize Camera
    camera = CameraController(capture_dir=DIRS['manual']) # Default to manual
    
    # Processor now only needs the BASE_DIR so it can find 'master_dark.jpg'
    processor = MediaProcessor(base_dir=BASE_DIR)
    
    # Timelapse now manages the 'sessions' folder
    timelapse = TimelapseManager(
        camera=camera, 
        processor=processor, 
        sessions_dir=DIRS['sessions'],
        batch_size=5
    )

    server = SkyServer(
        camera=camera, 
        timelapse=timelapse, 
        processor=processor, 
        dirs=DIRS
    )

    try:
        print("Starting Web Interface on port 5000...")
        server.run()
    finally:
        camera.release()

if __name__ == '__main__':
    main()
