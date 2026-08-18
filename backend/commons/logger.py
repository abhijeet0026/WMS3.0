"""
Central logging module for Whitfield Fulfillment WMS.

Provides structured logger setup for modules across backend layers.
"""

import logging
import os
import sys

# Ensure logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
try:
    os.makedirs(LOGS_DIR, exist_ok=True)
except Exception:
    pass

if os.environ.get("VERCEL"):
    LOG_FILE_PATH = "/tmp/app.log"
else:
    LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

try:
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
except Exception as e:
    file_handler = None

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)


def logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance for a given module name.

    Ensures single attachment of console and file handlers to prevent duplicate logs.

    Args:
        name (str): The module name requesting the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_instance = logging.getLogger(name)
    log_instance.setLevel(logging.INFO)

    if not log_instance.handlers:
        if file_handler:
            log_instance.addHandler(file_handler)
        log_instance.addHandler(console_handler)

    return log_instance
