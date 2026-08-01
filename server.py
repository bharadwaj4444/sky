import os
import glob
import shutil
from flask import Flask, render_template, request, jsonify, Response, send_from_directory

class SkyServer:
    def __init__(self, camera, timelapse, processor, dirs):
        self.camera = camera
        self.timelapse = timelapse
        self.processor = processor
        self.dirs = dirs
        self.app = Flask(__name__)
        self.setup_routes()

    def get_target_dir(self, folder_name):
        # 'processed' from the UI now maps to the 'sessions' master directory
        if folder_name == 'processed': return self.dirs['sessions']
        return self.dirs['manual']

    def setup_routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/stream', 'stream', self.stream)
        
        self.app.add_url_rule('/api/system/health', 'system_health', self.system_health)
        self.app.add_url_rule('/api/capture', 'capture_image', self.capture_image, methods=['POST'])
        self.app.add_url_rule('/api/control/record', 'control_record', self.control_record, methods=['POST'])
        self.app.add_url_rule('/api/control/ptz', 'control_ptz', self.control_ptz, methods=['POST'])
        self.app.add_url_rule('/api/control/histogram', 'control_hist', self.control_hist, methods=['POST'])
        self.app.add_url_rule('/api/config', 'config', self.config, methods=['GET', 'POST'])
        
        self.app.add_url_rule('/api/control/timelapse', 'control_timelapse', self.control_timelapse, methods=['POST'])
        self.app.add_url_rule('/api/config/timelapse', 'config_timelapse', self.config_timelapse, methods=['GET', 'POST'])
        self.app.add_url_rule('/api/control/make_video', 'make_video', self.make_video, methods=['POST'])
        
        self.app.add_url_rule('/api/gallery/', 'gallery', self.gallery)
        
        # --- NEW:  allows serving from subdirectories ---
        self.app.add_url_rule('/image//', 'serve_image', self.serve_image)

    def index(self): return render_template('index.html')

    def stream(self):
        def gen():
            while True:
                frame = self.camera.get_frame_bytes()
                if frame: yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def system_health(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_c = int(f.read()) / 1000.0
        except FileNotFoundError:
            temp_c = 0.0
        total, used, free = shutil.disk_usage("/")
        return jsonify({"temp_c": round(temp_c, 1), "free_gb": round(free / (2**30), 1), "total_gb": round(total / (2**30), 1)})

    def capture_image(self):
        filename = self.camera.take_photo(save_dir=self.dirs['manual'])
        if filename: return jsonify({"status": "success", "message": filename})
        return jsonify({"status": "error", "message": "No frame available"}), 503

    def control_record(self):
        action = request.json.get('action')
        if action == 'start':
            filename = self.camera.start_recording(save_dir=self.dirs['manual'])
            return jsonify({"status": "success", "message": filename})
        elif action == 'stop':
            self.camera.stop_recording()
            return jsonify({"status": "success"})
        return jsonify({"status": "error"}), 400

    def control_ptz(self):
        data = request.json
        self.camera.update_ptz(data.get('zoom', 1.0), data.get('pan_x', 0.5), data.get('pan_y', 0.5))
        return jsonify({"status": "success"})

    def control_hist(self):
        self.camera.show_histogram = not self.camera.show_histogram
        return jsonify({"status": "success", "showing": self.camera.show_histogram})

    def config(self):
        if request.method == 'POST': self.camera.apply_settings(request.json)
        return jsonify(self.camera.get_settings())

    def control_timelapse(self):
        action = request.json.get('action')
        if action == 'start': self.timelapse.start()
        elif action == 'stop': self.timelapse.stop()
        return jsonify({"running": self.timelapse.is_running})

    def config_timelapse(self):
        if request.method == 'GET': return jsonify({"interval": self.timelapse.interval, "batch_size": self.timelapse.batch_size})
        elif request.method == 'POST':
            data = request.json
            self.timelapse.update_settings(data.get('interval'), data.get('batch_size'))
            return jsonify({"status": "success"})

    def make_video(self):
        # --- NEW: FIND THE MOST RECENT SESSION AUTOMATICALLY ---
        sessions = sorted(glob.glob(os.path.join(self.dirs['sessions'], 'session_*')), key=os.path.getmtime)
        if not sessions:
            return jsonify({"status": "error", "message": "No sessions found"}), 400
        
        latest_session = sessions[-1]
        filename = self.processor.generate_video(latest_session, fps=request.json.get('fps', 10))
        
        if filename: 
            rel_path = os.path.join(os.path.basename(latest_session), filename)
            return jsonify({"status": "success", "message": rel_path})
        return jsonify({"status": "error", "message": "Not enough stacked images"}), 400

    def gallery(self, folder):
        target_dir = self.get_target_dir(folder)
        files = []
        
        if folder == 'processed':
            # --- NEW: RECURSIVE SEARCH ---
            # Search all session folders for stacked outputs and videos, ignoring raw files
            for ext in ('**/stacked_*.jpg', '**/*.mp4'):
                search_path = os.path.join(target_dir, ext)
                files.extend(glob.glob(search_path, recursive=True))
        else:
            for ext in ('*.jpg', '*.mp4'):
                files.extend(glob.glob(os.path.join(target_dir, ext)))
                
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Return relative paths (e.g. "session_123/stacked_abc.jpg") so the UI can construct the URL correctly
        rel_files = [os.path.relpath(f, target_dir) for f in files]
        return jsonify({"files": rel_files})

    def serve_image(self, folder, filename):
        target_dir = self.get_target_dir(folder)
        return send_from_directory(target_dir, filename)

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port, threaded=True)
