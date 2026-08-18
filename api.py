from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parent / "backend"
backend_path = str(BACKEND_DIR)
if backend_path not in sys.path:
    # Ensure backend absolute imports like `core.*` and `commons.*` resolve on Vercel.
    sys.path.insert(0, backend_path)

from main import app
