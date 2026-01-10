"""
Health Check System for Qwen-Image-Layered.

Provides self-diagnostic capabilities:
- API key validation
- Dependency checking
- Disk space monitoring
- Error tracking
- System status reporting
"""

import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from .logging_config import get_logger
except ImportError:
    import importlib.util as _util
    from pathlib import Path as _Path
    _spec = _util.spec_from_file_location(
        "logging_config",
        _Path(__file__).parent / "logging_config.py"
    )
    _logging_config = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_logging_config)
    get_logger = _logging_config.get_logger

logger = get_logger("health_check")


class CheckStatus(Enum):
    """Status values for health checks."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    timestamp: datetime
    operation: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation,
            "message": self.message,
            "details": self.details,
        }


# Required dependencies
REQUIRED_PACKAGES = [
    ("PIL", "Pillow"),
    ("requests", "requests"),
    ("dotenv", "python-dotenv"),
]

OPTIONAL_PACKAGES = [
    ("pptx", "python-pptx"),
    ("psd_tools", "psd-tools"),
    ("gradio", "gradio"),
    ("fal_client", "fal-client"),
]

# Disk space thresholds
MIN_DISK_SPACE_BYTES = 100 * 1024 * 1024  # 100MB
WARN_DISK_SPACE_BYTES = 500 * 1024 * 1024  # 500MB


class HealthChecker:
    """
    System health checker.

    Usage:
        checker = HealthChecker()
        status = checker.check_all()
        print(checker.get_report())
    """

    _instance: Optional["HealthChecker"] = None
    _errors: List[ErrorRecord] = []

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize health checker.

        Args:
            output_dir: Output directory to check (default: ./output)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "output"
        self._local_errors: List[ErrorRecord] = []

    @classmethod
    def get_instance(cls, **kwargs) -> "HealthChecker":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance."""
        cls._instance = None
        cls._errors = []

    def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Dictionary with all check results
        """
        results = {
            "api_key": self._check_api_key(),
            "dependencies": self._check_dependencies(),
            "disk_space": self._check_disk_space(),
            "output_directory": self._check_output_directory(),
            "timestamp": datetime.now().isoformat(),
        }

        # Determine overall status
        statuses = [
            results["api_key"]["status"],
            results["dependencies"]["status"],
            results["disk_space"]["status"],
            results["output_directory"]["status"],
        ]

        if "error" in statuses:
            overall = CheckStatus.ERROR
        elif "warning" in statuses:
            overall = CheckStatus.WARNING
        elif all(s == "ok" for s in statuses):
            overall = CheckStatus.OK
        else:
            overall = CheckStatus.UNKNOWN

        results["overall_status"] = overall.value

        logger.info(f"Health check completed: {overall.value}")
        return results

    def _check_api_key(self) -> Dict[str, Any]:
        """
        Check API key configuration.

        Returns:
            Check result dictionary
        """
        fal_key = os.environ.get("FAL_KEY")

        if not fal_key:
            return {
                "status": "error",
                "message": "FAL_KEY environment variable not set",
                "hint": "Set FAL_KEY in .env file or environment",
            }

        if len(fal_key) < 10:
            return {
                "status": "warning",
                "message": "FAL_KEY appears to be too short",
                "hint": "Check your API key from fal.ai",
            }

        # Mask key for display
        masked = fal_key[:4] + "..." + fal_key[-4:] if len(fal_key) > 8 else "****"

        return {
            "status": "ok",
            "message": f"API key configured ({masked})",
            "key_length": len(fal_key),
        }

    def _check_dependencies(self) -> Dict[str, Any]:
        """
        Check required dependencies.

        Returns:
            Check result dictionary
        """
        packages = {}
        missing_required = []
        missing_optional = []

        # Check required packages
        for module_name, package_name in REQUIRED_PACKAGES:
            try:
                __import__(module_name)
                packages[module_name] = {"installed": True, "required": True}
            except ImportError:
                packages[module_name] = {"installed": False, "required": True}
                missing_required.append(package_name)

        # Check optional packages
        for module_name, package_name in OPTIONAL_PACKAGES:
            try:
                __import__(module_name)
                packages[module_name] = {"installed": True, "required": False}
            except ImportError:
                packages[module_name] = {"installed": False, "required": False}
                missing_optional.append(package_name)

        # Determine status
        if missing_required:
            status = "error"
            message = f"Missing required: {', '.join(missing_required)}"
        elif missing_optional:
            status = "warning"
            message = f"Missing optional: {', '.join(missing_optional)}"
        else:
            status = "ok"
            message = "All dependencies installed"

        return {
            "status": status,
            "message": message,
            "packages": packages,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
        }

    def _check_disk_space(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Check available disk space.

        Args:
            path: Path to check (default: current directory)

        Returns:
            Check result dictionary
        """
        check_path = Path(path) if path else Path.cwd()

        try:
            usage = shutil.disk_usage(check_path)
            free_bytes = usage.free

            # Convert to human-readable
            if free_bytes >= 1024**3:
                free_human = f"{free_bytes / 1024**3:.1f} GB"
            elif free_bytes >= 1024**2:
                free_human = f"{free_bytes / 1024**2:.1f} MB"
            else:
                free_human = f"{free_bytes / 1024:.1f} KB"

            # Determine status
            if free_bytes < MIN_DISK_SPACE_BYTES:
                status = "error"
                message = f"Very low disk space: {free_human}"
            elif free_bytes < WARN_DISK_SPACE_BYTES:
                status = "warning"
                message = f"Low disk space: {free_human}"
            else:
                status = "ok"
                message = f"Sufficient disk space: {free_human}"

            return {
                "status": status,
                "message": message,
                "free_bytes": free_bytes,
                "free_human": free_human,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Cannot check disk space: {e}",
                "free_bytes": 0,
                "free_human": "unknown",
            }

    def _check_output_directory(self) -> Dict[str, Any]:
        """
        Check output directory accessibility.

        Returns:
            Check result dictionary
        """
        try:
            # Create if doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Check if writable
            test_file = self.output_dir / ".health_check_test"
            test_file.write_text("test")
            test_file.unlink()

            return {
                "status": "ok",
                "message": f"Output directory ready: {self.output_dir}",
                "path": str(self.output_dir),
                "writable": True,
            }
        except PermissionError:
            return {
                "status": "error",
                "message": f"Cannot write to output directory: {self.output_dir}",
                "path": str(self.output_dir),
                "writable": False,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Output directory error: {e}",
                "path": str(self.output_dir),
                "writable": False,
            }

    def record_error(
        self,
        operation: str,
        message: str,
        **details: Any,
    ) -> None:
        """
        Record an error occurrence.

        Args:
            operation: Operation that failed
            message: Error message
            **details: Additional details
        """
        error = ErrorRecord(
            timestamp=datetime.now(),
            operation=operation,
            message=message,
            details=details,
        )
        self._local_errors.append(error)
        HealthChecker._errors.append(error)

        logger.error(f"Error recorded: [{operation}] {message}")

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent errors.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of error dictionaries
        """
        # Combine instance and class errors, sort by timestamp
        all_errors = sorted(
            self._local_errors + HealthChecker._errors,
            key=lambda e: e.timestamp,
            reverse=True,
        )
        # Remove duplicates
        seen = set()
        unique_errors = []
        for e in all_errors:
            key = (e.timestamp.isoformat(), e.operation, e.message)
            if key not in seen:
                seen.add(key)
                unique_errors.append(e)

        return [e.to_dict() for e in unique_errors[:limit]]

    def clear_errors(self) -> None:
        """Clear all recorded errors."""
        self._local_errors = []
        HealthChecker._errors = []
        logger.info("Error history cleared")

    def get_report(self) -> str:
        """
        Generate human-readable health report.

        Returns:
            Report string
        """
        results = self.check_all()

        lines = [
            "=" * 60,
            "System Health Report",
            "=" * 60,
            f"Timestamp: {results['timestamp']}",
            f"Overall Status: {results['overall_status'].upper()}",
            "",
            "--- API Key ---",
            f"  Status: {results['api_key']['status']}",
            f"  {results['api_key']['message']}",
            "",
            "--- Dependencies ---",
            f"  Status: {results['dependencies']['status']}",
            f"  {results['dependencies']['message']}",
            "",
            "--- Disk Space ---",
            f"  Status: {results['disk_space']['status']}",
            f"  {results['disk_space']['message']}",
            "",
            "--- Output Directory ---",
            f"  Status: {results['output_directory']['status']}",
            f"  {results['output_directory']['message']}",
        ]

        # Add recent errors if any
        errors = self.get_recent_errors(5)
        if errors:
            lines.append("")
            lines.append("--- Recent Errors ---")
            for e in errors:
                lines.append(f"  [{e['operation']}] {e['message']}")

        lines.append("=" * 60)

        return "\n".join(lines)

    def get_json_report(self) -> str:
        """
        Generate JSON health report.

        Returns:
            JSON string
        """
        results = self.check_all()
        results["recent_errors"] = self.get_recent_errors()
        return json.dumps(results, indent=2, default=str)


# Singleton instance for convenience functions
_checker: Optional[HealthChecker] = None


def _get_checker() -> HealthChecker:
    """Get or create checker instance."""
    global _checker
    if _checker is None:
        _checker = HealthChecker()
    return _checker


def run_health_check() -> Dict[str, Any]:
    """
    Run a complete health check.

    Returns:
        Health check results dictionary
    """
    return _get_checker().check_all()


def get_system_status() -> str:
    """
    Get overall system status.

    Returns:
        Status string: 'ok', 'warning', 'error', or 'unknown'
    """
    results = _get_checker().check_all()
    return results.get("overall_status", "unknown")


def get_recent_errors(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent system errors.

    Args:
        limit: Maximum number of errors

    Returns:
        List of error dictionaries
    """
    return _get_checker().get_recent_errors(limit)


def record_error(operation: str, message: str, **details: Any) -> None:
    """
    Record a system error.

    Args:
        operation: Operation that failed
        message: Error message
        **details: Additional details
    """
    _get_checker().record_error(operation, message, **details)


def get_health_report() -> str:
    """
    Get human-readable health report.

    Returns:
        Report string
    """
    return _get_checker().get_report()


def get_json_health_report() -> str:
    """
    Get JSON health report.

    Returns:
        JSON string
    """
    return _get_checker().get_json_report()
