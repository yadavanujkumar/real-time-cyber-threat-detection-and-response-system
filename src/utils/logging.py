# src/utils/logging.py

import logging
import logging.handlers
import json
import os
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Converts log records into JSON format for better parsing and analysis in production systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "process": record.process,
            "thread": record.thread,
        }

        # Include exception information if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


def get_log_level() -> int:
    """
    Determines the log level based on the environment variable `LOG_LEVEL`.
    Defaults to INFO if not set or invalid.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    valid_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    return valid_levels.get(log_level, logging.INFO)


def configure_logging(log_file: str = "app.log", max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5) -> None:
    """
    Configures the logging system for production use.
    - Logs to both console and a rotating file handler.
    - Uses JSON formatting for structured logs.
    - Supports log rotation to prevent disk space issues.

    Args:
        log_file (str): Path to the log file.
        max_bytes (int): Maximum size of a log file before rotation (default: 10MB).
        backup_count (int): Number of backup files to keep (default: 5).
    """
    log_level = get_log_level()

    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(JSONFormatter())

    # Create a rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(JSONFormatter())

    # Add handlers to the root logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger instance with the given name.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)


# Example usage
if __name__ == "__main__":
    # Configure logging
    configure_logging()

    # Get a logger
    logger = get_logger(__name__)

    # Log messages at various levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("An exception occurred.")