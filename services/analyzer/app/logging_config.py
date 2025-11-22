"""Logging configuration"""

import logging
import sys
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging():
    """Setup structured JSON logging"""
    logger = logging.getLogger()

    # Clear existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "name": "logger", "levelname": "level"},
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set level
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
