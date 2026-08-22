from flask import Flask

from web.routes import register_routes


def create_app(
    *,
    timelapse=None,
    streamer=None,
    capture_service=None,
):

    print(">>> create_app() CALLED")

    app = Flask(__name__)

    register_routes(
        app,
        timelapse=timelapse,
        streamer=streamer,
        capture_service=capture_service,
    )

    print(">>> FINAL URL MAP:")
    print(app.url_map)

    return app