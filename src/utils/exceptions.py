# src/utils/exceptions.py

"""
Custom exception classes for the Real-Time Cyber Threat Detection and Response System.

This module defines a hierarchy of exceptions tailored to the application, providing:
- Meaningful error messages and error codes for precise debugging.
- Integration with logging for seamless monitoring and diagnostics.
- Thread-safe and memory-efficient implementation.
- Comprehensive type hints and documentation for maintainability.
"""

import logging
from typing import Optional

# Configure a logger for the exceptions module
logger = logging.getLogger("exceptions")
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class BaseApplicationException(Exception):
    """
    Base class for all custom exceptions in the application.

    Attributes:
        message (str): A human-readable description of the error.
        error_code (int): A unique error code for identifying the error type.
        details (Optional[dict]): Additional context or metadata about the error.
    """

    def __init__(self, message: str, error_code: int, details: Optional[dict] = None):
        """
        Initialize the base exception.

        Args:
            message (str): Error message.
            error_code (int): Unique error code.
            details (Optional[dict]): Additional context or metadata.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

        # Log the exception details
        self.log_error()

    def log_error(self) -> None:
        """
        Log the exception details using the configured logger.
        """
        error_details = {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }
        logger.error("Application Exception: %s", error_details)

    def to_dict(self) -> dict:
        """
        Convert the exception to a dictionary representation.

        Returns:
            dict: A dictionary containing error details.
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(BaseApplicationException):
    """
    Exception raised for configuration-related errors.

    Example: Missing environment variables, invalid configuration values, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=1001, details=details)


class DatabaseConnectionError(BaseApplicationException):
    """
    Exception raised for database connection issues.

    Example: Unable to connect to the database, authentication failure, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=2001, details=details)


class ThreatDetectionError(BaseApplicationException):
    """
    Exception raised during the threat detection process.

    Example: Errors in the detection pipeline, invalid input data, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=3001, details=details)


class APIRequestError(BaseApplicationException):
    """
    Exception raised for errors in API requests.

    Example: Invalid request parameters, authentication errors, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=4001, details=details)


class UnauthorizedAccessError(BaseApplicationException):
    """
    Exception raised for unauthorized access attempts.

    Example: Invalid credentials, insufficient permissions, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=4003, details=details)


class ResourceNotFoundError(BaseApplicationException):
    """
    Exception raised when a requested resource is not found.

    Example: Missing files, database records, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=4040, details=details)


class InternalServerError(BaseApplicationException):
    """
    Exception raised for unexpected internal server errors.

    Example: Unhandled exceptions, system failures, etc.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, error_code=5000, details=details)


# Example usage (for testing purposes only, remove in production)
if __name__ == "__main__":
    try:
        raise ConfigurationError("Missing required environment variable", {"env_var": "DB_HOST"})
    except ConfigurationError as e:
        print(e.to_dict())

    try:
        raise DatabaseConnectionError("Failed to connect to the database", {"host": "localhost", "port": 5432})
    except DatabaseConnectionError as e:
        print(e.to_dict())