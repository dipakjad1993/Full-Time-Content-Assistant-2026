"""WSGI entry for prod (gunicorn linux / waitress windows). Keeps server.py as source of truth."""
import os
from server import app  # noqa: F401

if __name__ == "__main__":
    try:
        from waitress import serve
        serve(app, host=os.environ.get("HOST", "127.0.0.1"),
              port=int(os.environ.get("PORT", "5000")), threads=8)
    except ImportError:
        app.run(host=os.environ.get("HOST", "127.0.0.1"),
                port=int(os.environ.get("PORT", "5000")), threaded=True)
