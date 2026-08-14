"""
Application entrypoint for Whitfield Fulfillment WMS backend API.

Starts the Uvicorn ASGI server hosting the FastAPI application aggregator.
"""

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from commons.logger import logger
from core.apis.api import create_app

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

logging = logger(__name__)
app = create_app()

if __name__ == "__main__":
    logging.info("Starting Uvicorn web server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
