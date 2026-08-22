from flask import Response, jsonify, request

import camera


def register_routes(
    app,
    *,
    timelapse,
    streamer,
    capture_service=None,
):

    print(">>> register_routes() CALLED")

    @app.get("/")
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sky Camera</title>
        </head>

        <body>
            <h1>Sky Camera</h1>

            <div>
                <img
                    id="camera"
                    src="/stream"
                    width="960"
                    style="max-width:100%;"
                >
            </div>

            <p id="status">
                Connecting to camera...
            </p>

            <script>
                fetch("/api/health")
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById(
                            "status"
                        ).textContent =
                            "Server: " + data.status;
                    })
                    .catch(error => {
                        document.getElementById(
                            "status"
                        ).textContent =
                            "Health check failed";
                    });
            </script>

        </body>
        </html>
        """

    @app.get("/api/health")
    def health():

        return jsonify({
            "status": "ok",
            "camera": {
                "open": True,
            },
            "capture": {
                "running": capture_service.is_running,
                "sequence": capture_service.sequence,
            },
        })

    @app.get("/stream")
    def stream():

        return Response(
            streamer.stream(),
            mimetype=(
                "multipart/x-mixed-replace; "
                "boundary=frame"
            ),
        )

    print(">>> ROUTES AFTER REGISTRATION:")
    print(app.url_map)