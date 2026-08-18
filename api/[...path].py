from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
backend_path = str(BACKEND_DIR)
if backend_path not in sys.path:
    # Ensure backend absolute imports like `core.*` and `commons.*` resolve on Vercel.
    sys.path.insert(0, backend_path)

from main import app as _app

async def app(scope, receive, send):
    if scope["type"] in ("http", "websocket"):
        path = scope.get("path", "")
        if path.startswith("/api"):
            scope["path"] = path[4:]
            
        raw_path = scope.get("raw_path", b"")
        if raw_path.startswith(b"/api"):
            scope["raw_path"] = raw_path[4:]
            
    await _app(scope, receive, send)
