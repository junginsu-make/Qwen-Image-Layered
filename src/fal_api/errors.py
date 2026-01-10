"""
Error Handling Module - Custom exceptions and error utilities.
Provides consistent error handling across all modules.
"""

import functools
import time
from typing import Callable, Any, Optional


# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================

class FalAPIError(Exception):
    """Base exception for Fal AI API errors."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "success": False,
            "error": self.message,
            "error_code": self.code,
            "details": self.details
        }


class APIKeyError(FalAPIError):
    """Raised when FAL_KEY is not configured."""

    def __init__(self, message: str = None):
        super().__init__(
            message or "FAL_KEY environment variable not set. Please configure your API key.",
            code="API_KEY_MISSING"
        )


class NetworkError(FalAPIError):
    """Raised when network request fails."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(
            message,
            code="NETWORK_ERROR",
            details={"original_error": str(original_error) if original_error else None}
        )


class APITimeoutError(FalAPIError):
    """Raised when API request times out."""

    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"API request timed out after {timeout_seconds} seconds",
            code="TIMEOUT",
            details={"timeout": timeout_seconds}
        )


class APIRateLimitError(FalAPIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, retry_after: int = None):
        super().__init__(
            "API rate limit exceeded. Please try again later.",
            code="RATE_LIMIT",
            details={"retry_after": retry_after}
        )


class ImageProcessingError(FalAPIError):
    """Raised when image processing fails."""

    def __init__(self, message: str, image_path: str = None):
        super().__init__(
            message,
            code="IMAGE_PROCESSING_ERROR",
            details={"image_path": image_path}
        )


class InvalidInputError(FalAPIError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(
            message,
            code="INVALID_INPUT",
            details={"field": field, "value": str(value) if value else None}
        )


class FileNotFoundError(FalAPIError):
    """Raised when required file is not found."""

    def __init__(self, file_path: str):
        super().__init__(
            f"File not found: {file_path}",
            code="FILE_NOT_FOUND",
            details={"file_path": file_path}
        )


class DependencyError(FalAPIError):
    """Raised when required dependency is not installed."""

    def __init__(self, package: str, install_cmd: str = None):
        super().__init__(
            f"Required package '{package}' is not installed.",
            code="DEPENDENCY_MISSING",
            details={
                "package": package,
                "install_command": install_cmd or f"pip install {package}"
            }
        )


# ============================================================
# ERROR HANDLING UTILITIES
# ============================================================

def safe_result(success: bool, **kwargs) -> dict:
    """Create a standardized result dictionary."""
    result = {"success": success}
    result.update(kwargs)
    return result


def error_result(error: Exception) -> dict:
    """Convert exception to error result dict."""
    if isinstance(error, FalAPIError):
        return error.to_dict()

    return {
        "success": False,
        "error": str(error),
        "error_code": "UNKNOWN_ERROR"
    }


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (NetworkError, APITimeoutError)
) -> Callable:
    """
    Decorator to retry function on specific errors.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise

            raise last_error

        return wrapper
    return decorator


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to catch and convert API errors to result dicts.
    Use this on public-facing functions to ensure consistent error format.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FalAPIError as e:
            return e.to_dict()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "UNEXPECTED_ERROR"
            }

    return wrapper


def validate_api_key() -> bool:
    """Check if FAL_KEY is configured."""
    import os
    key = os.environ.get("FAL_KEY")
    if not key:
        raise APIKeyError()
    return True


def validate_file_exists(file_path: str) -> bool:
    """Check if file exists."""
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    return True


def validate_image_file(file_path: str) -> bool:
    """Validate that file is a valid image."""
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in valid_extensions:
        raise InvalidInputError(
            f"Invalid image format. Supported: {valid_extensions}",
            field="file_path",
            value=file_path
        )

    return True


# ============================================================
# NETWORK ERROR HANDLING
# ============================================================

def handle_network_error(func: Callable) -> Callable:
    """Decorator to catch network-related errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            raise NetworkError("Connection failed. Check your internet connection.", e)
        except TimeoutError as e:
            raise APITimeoutError(30)
        except Exception as e:
            if "timeout" in str(e).lower():
                raise APITimeoutError(30)
            elif "connection" in str(e).lower():
                raise NetworkError("Network connection error", e)
            raise

    return wrapper


# ============================================================
# LOGGING UTILITIES
# ============================================================

def log_error(error: Exception, context: str = None):
    """Log error with context."""
    import sys
    error_info = f"[ERROR] {type(error).__name__}: {error}"
    if context:
        error_info = f"[{context}] {error_info}"
    print(error_info, file=sys.stderr)


def log_warning(message: str, context: str = None):
    """Log warning message."""
    import sys
    warning_info = f"[WARNING] {message}"
    if context:
        warning_info = f"[{context}] {warning_info}"
    print(warning_info, file=sys.stderr)


# ============================================================
# ERROR CODES REFERENCE
# ============================================================

ERROR_CODES = {
    "API_KEY_MISSING": "FAL_KEY environment variable not configured",
    "NETWORK_ERROR": "Network request failed",
    "TIMEOUT": "Request timed out",
    "RATE_LIMIT": "API rate limit exceeded",
    "IMAGE_PROCESSING_ERROR": "Failed to process image",
    "INVALID_INPUT": "Input validation failed",
    "FILE_NOT_FOUND": "Required file not found",
    "DEPENDENCY_MISSING": "Required package not installed",
    "UNKNOWN_ERROR": "Unexpected error occurred",
    "UNEXPECTED_ERROR": "Unhandled exception occurred"
}
