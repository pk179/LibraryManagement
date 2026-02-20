import logging
import logging.handlers
import os
from typing import Optional

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Create module-level logger
_logger = logging.getLogger("library_app")
_logger.setLevel(logging.INFO)

# Prevent adding multiple handlers if module is reloaded
if not _logger.handlers:
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(module)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)


def log_info(message: str, *, extra: Optional[dict] = None) -> None:
    """Log an informational message"""
    _logger.info(message, extra=extra)


def log_warning(message: str, *, extra: Optional[dict] = None) -> None:
    """Log a warning message"""
    _logger.warning(message, extra=extra)


def log_error(message: str, *, extra: Optional[dict] = None) -> None:
    """Log an error message"""
    _logger.error(message, extra=extra)


def log_exception(message: str, *, extra: Optional[dict] = None) -> None:
    """
    Log an exception with stack trace
    """
    _logger.exception(message, extra=extra)


def get_logger() -> logging.Logger:
    """Return the underlying logger"""
    return _logger
