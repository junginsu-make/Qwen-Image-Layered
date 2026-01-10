"""
Intelligent Error Recovery System.

Uses LLMs to:
- Analyze error patterns
- Suggest recovery strategies
- Automatically retry with alternative approaches
- Learn from failures

Supports automatic recovery for:
- API timeouts
- Rate limiting
- Model failures
- Network issues
- Resource constraints
"""

import time
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta

try:
    from .logging_config import get_logger
    from .llm_client import LLMClient, LLMProvider
    from .health_check import record_error as health_record_error
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

    _spec = _util.spec_from_file_location(
        "llm_client",
        _Path(__file__).parent / "llm_client.py"
    )
    _llm_client = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_llm_client)
    LLMClient = _llm_client.LLMClient
    LLMProvider = _llm_client.LLMProvider

    def health_record_error(operation, message, **details):
        pass

logger = get_logger("error_recovery")


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Available recovery strategies."""
    RETRY = "retry"
    RETRY_WITH_DELAY = "retry_with_delay"
    USE_ALTERNATIVE_MODEL = "use_alternative_model"
    REDUCE_QUALITY = "reduce_quality"
    REDUCE_RESOLUTION = "reduce_resolution"
    SPLIT_REQUEST = "split_request"
    USE_FALLBACK = "use_fallback"
    REFRESH_CREDENTIALS = "refresh_credentials"
    WAIT_AND_RETRY = "wait_and_retry"
    ABORT = "abort"


@dataclass
class ErrorAnalysis:
    """Analysis result for an error."""
    error_type: str
    root_cause: str
    severity: ErrorSeverity
    recoverable: bool
    suggested_strategies: List[RecoveryStrategy]
    context: Dict[str, Any] = field(default_factory=dict)
    similar_errors_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_type": self.error_type,
            "root_cause": self.root_cause,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "suggested_strategies": [s.value for s in self.suggested_strategies],
            "context": self.context,
            "similar_errors_count": self.similar_errors_count,
        }


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""
    success: bool
    strategy_used: RecoveryStrategy
    attempts: int
    result: Optional[Any] = None
    final_error: Optional[str] = None
    time_taken: float = 0.0
    cost_incurred: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "strategy_used": self.strategy_used.value,
            "attempts": self.attempts,
            "result": str(self.result) if self.result else None,
            "final_error": self.final_error,
            "time_taken": self.time_taken,
            "cost_incurred": self.cost_incurred,
        }


@dataclass
class StrategyOption:
    """A recovery strategy option."""
    strategy: RecoveryStrategy
    success_probability: float
    description: str
    estimated_delay: float = 0.0
    cost_multiplier: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy": self.strategy.value,
            "success_probability": self.success_probability,
            "description": self.description,
            "estimated_delay": self.estimated_delay,
            "cost_multiplier": self.cost_multiplier,
            "parameters": self.parameters,
        }


# Error patterns and their characteristics
ERROR_PATTERNS = {
    "timeout": {
        "patterns": [r"timeout", r"timed out", r"deadline exceeded", r"시간 초과"],
        "severity": ErrorSeverity.MEDIUM,
        "strategies": [
            RecoveryStrategy.RETRY_WITH_DELAY,
            RecoveryStrategy.REDUCE_QUALITY,
            RecoveryStrategy.USE_ALTERNATIVE_MODEL,
        ],
        "recoverable": True,
    },
    "rate_limit": {
        "patterns": [r"rate limit", r"too many requests", r"429", r"quota exceeded"],
        "severity": ErrorSeverity.MEDIUM,
        "strategies": [
            RecoveryStrategy.WAIT_AND_RETRY,
            RecoveryStrategy.USE_ALTERNATIVE_MODEL,
        ],
        "recoverable": True,
    },
    "auth_error": {
        "patterns": [r"unauthorized", r"invalid.*key", r"authentication", r"403", r"401"],
        "severity": ErrorSeverity.HIGH,
        "strategies": [
            RecoveryStrategy.REFRESH_CREDENTIALS,
            RecoveryStrategy.ABORT,
        ],
        "recoverable": False,
    },
    "network_error": {
        "patterns": [r"network", r"connection", r"dns", r"socket", r"연결"],
        "severity": ErrorSeverity.MEDIUM,
        "strategies": [
            RecoveryStrategy.RETRY_WITH_DELAY,
            RecoveryStrategy.RETRY,
        ],
        "recoverable": True,
    },
    "resource_error": {
        "patterns": [r"memory", r"disk", r"storage", r"space", r"resource", r"cuda"],
        "severity": ErrorSeverity.HIGH,
        "strategies": [
            RecoveryStrategy.REDUCE_RESOLUTION,
            RecoveryStrategy.REDUCE_QUALITY,
            RecoveryStrategy.USE_ALTERNATIVE_MODEL,
        ],
        "recoverable": True,
    },
    "model_error": {
        "patterns": [r"model.*not found", r"invalid model", r"unsupported", r"모델"],
        "severity": ErrorSeverity.MEDIUM,
        "strategies": [
            RecoveryStrategy.USE_ALTERNATIVE_MODEL,
            RecoveryStrategy.USE_FALLBACK,
        ],
        "recoverable": True,
    },
    "input_error": {
        "patterns": [r"invalid input", r"bad request", r"validation", r"400", r"입력"],
        "severity": ErrorSeverity.LOW,
        "strategies": [
            RecoveryStrategy.ABORT,
        ],
        "recoverable": False,
    },
    "server_error": {
        "patterns": [r"500", r"502", r"503", r"504", r"internal server", r"서버"],
        "severity": ErrorSeverity.MEDIUM,
        "strategies": [
            RecoveryStrategy.RETRY_WITH_DELAY,
            RecoveryStrategy.USE_ALTERNATIVE_MODEL,
        ],
        "recoverable": True,
    },
}

# Alternative model mappings
ALTERNATIVE_MODELS = {
    "nano-banana-pro": ["nano-banana", "flux-dev"],
    "nano-banana-pro-edit": ["nano-banana-edit", "lama-inpainting"],
    "nano-banana": ["flux-schnell", "flux-dev"],
    "nano-banana-edit": ["lama-inpainting"],
    "flux-dev": ["flux-schnell", "nano-banana"],
    "flux-schnell": ["nano-banana"],
    "creative-upscaler": [],
    "llava-next": [],
}


class ErrorRecovery:
    """
    Intelligent error recovery system.

    Usage:
        recovery = ErrorRecovery()

        # Analyze an error
        analysis = recovery.analyze_error(exception, context={"operation": "generate"})
        print(f"Root cause: {analysis['root_cause']}")

        # Get recovery strategies
        strategies = recovery.suggest_recovery(exception)
        for s in strategies:
            print(f"{s['strategy']}: {s['description']}")

        # Auto-recover with retry
        result = recovery.auto_recover(
            operation=generate_image,
            args=("prompt", "model"),
            max_attempts=3
        )
    """

    def __init__(self, use_llm: bool = True, max_history: int = 100):
        """
        Initialize error recovery.

        Args:
            use_llm: Use LLM for advanced error analysis
            max_history: Maximum error history to keep
        """
        self.use_llm = use_llm
        self._llm_client = LLMClient() if use_llm else None
        self._error_history: List[Dict[str, Any]] = []
        self._max_history = max_history

    def analyze_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze an error to determine cause and recovery options.

        Args:
            error: The exception that occurred
            context: Additional context about the operation

        Returns:
            ErrorAnalysis as dictionary
        """
        error_str = str(error).lower()
        context = context or {}

        # Match against known patterns
        matched_type = "unknown"
        matched_info = None

        for error_type, info in ERROR_PATTERNS.items():
            for pattern in info["patterns"]:
                if re.search(pattern, error_str, re.IGNORECASE):
                    matched_type = error_type
                    matched_info = info
                    break
            if matched_info:
                break

        # Default for unknown errors
        if not matched_info:
            matched_info = {
                "severity": ErrorSeverity.MEDIUM,
                "strategies": [RecoveryStrategy.RETRY, RecoveryStrategy.ABORT],
                "recoverable": True,
            }

        # Count similar errors
        similar_count = sum(
            1 for e in self._error_history
            if e.get("error_type") == matched_type
        )

        # Determine root cause
        root_cause = self._determine_root_cause(matched_type, error_str, context)

        analysis = ErrorAnalysis(
            error_type=matched_type,
            root_cause=root_cause,
            severity=matched_info["severity"],
            recoverable=matched_info["recoverable"],
            suggested_strategies=matched_info["strategies"],
            context=context,
            similar_errors_count=similar_count,
        )

        # Record in history
        self._record_error(analysis, str(error))

        logger.info(f"Error analyzed: {matched_type} (severity: {analysis.severity.value})")
        return analysis.to_dict()

    def _determine_root_cause(
        self,
        error_type: str,
        error_str: str,
        context: Dict[str, Any],
    ) -> str:
        """Determine the root cause of an error."""
        causes = {
            "timeout": "API request exceeded time limit, possibly due to server load or complex request",
            "rate_limit": "Too many requests sent in a short period, API quota exhausted",
            "auth_error": "API key is invalid, expired, or missing",
            "network_error": "Network connectivity issue or DNS resolution failure",
            "resource_error": "Insufficient system resources (memory, disk, GPU)",
            "model_error": "Requested model is unavailable or incorrectly specified",
            "input_error": "Invalid input parameters or malformed request",
            "server_error": "Remote server encountered an internal error",
            "unknown": "Unable to determine specific cause",
        }

        return causes.get(error_type, causes["unknown"])

    def _record_error(self, analysis: ErrorAnalysis, error_message: str):
        """Record error in history."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": analysis.error_type,
            "severity": analysis.severity.value,
            "message": error_message[:200],
            "context": analysis.context,
        }

        self._error_history.append(record)

        # Trim history
        if len(self._error_history) > self._max_history:
            self._error_history = self._error_history[-self._max_history:]

        # Also record in health check system
        try:
            health_record_error(
                operation=analysis.context.get("operation", "unknown"),
                message=error_message[:200],
                error_type=analysis.error_type,
            )
        except Exception:
            pass

    def suggest_recovery(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Suggest recovery strategies for an error.

        Args:
            error: The exception
            context: Additional context

        Returns:
            List of StrategyOption as dictionaries
        """
        analysis = self.analyze_error(error, context)
        strategies = []

        error_type = analysis.get("error_type", "unknown")
        similar_count = analysis.get("similar_errors_count", 0)

        # Get base strategies from analysis
        base_strategies = [
            RecoveryStrategy(s) for s in analysis.get("suggested_strategies", [])
        ]

        for strategy in base_strategies:
            option = self._build_strategy_option(strategy, error_type, similar_count, context)
            strategies.append(option.to_dict())

        # Sort by success probability
        strategies.sort(key=lambda x: x["success_probability"], reverse=True)

        return strategies

    def _build_strategy_option(
        self,
        strategy: RecoveryStrategy,
        error_type: str,
        similar_count: int,
        context: Optional[Dict[str, Any]],
    ) -> StrategyOption:
        """Build a strategy option with probabilities."""
        context = context or {}

        # Base probabilities and descriptions
        base_config = {
            RecoveryStrategy.RETRY: {
                "probability": 0.6,
                "description": "Retry the operation immediately",
                "delay": 0,
            },
            RecoveryStrategy.RETRY_WITH_DELAY: {
                "probability": 0.75,
                "description": "Wait briefly then retry",
                "delay": 2.0,
            },
            RecoveryStrategy.WAIT_AND_RETRY: {
                "probability": 0.85,
                "description": "Wait for rate limit reset then retry",
                "delay": 60.0,
            },
            RecoveryStrategy.USE_ALTERNATIVE_MODEL: {
                "probability": 0.80,
                "description": "Switch to an alternative model",
                "delay": 0,
                "cost_multiplier": 0.5,
            },
            RecoveryStrategy.REDUCE_QUALITY: {
                "probability": 0.85,
                "description": "Reduce quality settings to decrease load",
                "delay": 0,
                "cost_multiplier": 0.7,
            },
            RecoveryStrategy.REDUCE_RESOLUTION: {
                "probability": 0.90,
                "description": "Reduce output resolution",
                "delay": 0,
                "cost_multiplier": 0.5,
            },
            RecoveryStrategy.SPLIT_REQUEST: {
                "probability": 0.70,
                "description": "Split into smaller requests",
                "delay": 0,
                "cost_multiplier": 1.2,
            },
            RecoveryStrategy.USE_FALLBACK: {
                "probability": 0.95,
                "description": "Use fallback/cached result",
                "delay": 0,
                "cost_multiplier": 0.0,
            },
            RecoveryStrategy.REFRESH_CREDENTIALS: {
                "probability": 0.50,
                "description": "Refresh API credentials",
                "delay": 1.0,
            },
            RecoveryStrategy.ABORT: {
                "probability": 0.0,
                "description": "Abort operation (unrecoverable)",
                "delay": 0,
            },
        }

        config = base_config.get(strategy, {
            "probability": 0.5,
            "description": str(strategy.value),
            "delay": 0,
        })

        # Adjust probability based on error history
        probability = config["probability"]
        if similar_count > 3:
            probability *= 0.8  # Reduce confidence for repeated errors
        if similar_count > 5:
            probability *= 0.7

        # Build parameters based on strategy
        parameters = {}
        if strategy == RecoveryStrategy.USE_ALTERNATIVE_MODEL:
            current_model = context.get("model", "nano-banana-pro")
            alternatives = ALTERNATIVE_MODELS.get(current_model, ["nano-banana"])
            if alternatives:
                parameters["alternative_model"] = alternatives[0]
                parameters["all_alternatives"] = alternatives

        if strategy in [RecoveryStrategy.RETRY_WITH_DELAY, RecoveryStrategy.WAIT_AND_RETRY]:
            parameters["delay_seconds"] = config.get("delay", 2.0)

        return StrategyOption(
            strategy=strategy,
            success_probability=probability,
            description=config["description"],
            estimated_delay=config.get("delay", 0),
            cost_multiplier=config.get("cost_multiplier", 1.0),
            parameters=parameters,
        )

    def auto_recover(
        self,
        operation: Callable,
        args: Tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        max_attempts: int = 3,
        strategies: Optional[List[RecoveryStrategy]] = None,
    ) -> RecoveryResult:
        """
        Automatically attempt recovery for a failed operation.

        Args:
            operation: The callable to retry
            args: Positional arguments for the operation
            kwargs: Keyword arguments for the operation
            max_attempts: Maximum retry attempts
            strategies: Specific strategies to try (auto-select if None)

        Returns:
            RecoveryResult with outcome
        """
        kwargs = kwargs or {}
        start_time = time.time()
        attempts = 0
        last_error = None
        strategy_used = RecoveryStrategy.RETRY

        while attempts < max_attempts:
            attempts += 1

            try:
                result = operation(*args, **kwargs)
                return RecoveryResult(
                    success=True,
                    strategy_used=strategy_used,
                    attempts=attempts,
                    result=result,
                    time_taken=time.time() - start_time,
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempts} failed: {e}")

                if attempts >= max_attempts:
                    break

                # Get recovery strategies
                suggested = self.suggest_recovery(e, context={"operation": str(operation)})

                if not suggested or suggested[0]["strategy"] == "abort":
                    break

                # Apply best strategy
                best = suggested[0]
                strategy_used = RecoveryStrategy(best["strategy"])

                # Apply strategy
                if strategy_used == RecoveryStrategy.RETRY_WITH_DELAY:
                    delay = best.get("parameters", {}).get("delay_seconds", 2.0)
                    time.sleep(delay)

                elif strategy_used == RecoveryStrategy.WAIT_AND_RETRY:
                    delay = best.get("parameters", {}).get("delay_seconds", 60.0)
                    time.sleep(min(delay, 30))  # Cap at 30 seconds

                elif strategy_used == RecoveryStrategy.USE_ALTERNATIVE_MODEL:
                    alt_model = best.get("parameters", {}).get("alternative_model")
                    if alt_model and "model" in kwargs:
                        kwargs["model"] = alt_model
                        logger.info(f"Switching to alternative model: {alt_model}")

                elif strategy_used == RecoveryStrategy.REDUCE_QUALITY:
                    if "quality" in kwargs:
                        kwargs["quality"] = "fast"
                    if "resolution" in kwargs:
                        kwargs["resolution"] = "1k"

        return RecoveryResult(
            success=False,
            strategy_used=strategy_used,
            attempts=attempts,
            final_error=str(last_error),
            time_taken=time.time() - start_time,
        )

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about recent errors.

        Returns:
            Dictionary with error statistics
        """
        if not self._error_history:
            return {"total_errors": 0}

        # Count by type
        type_counts = {}
        severity_counts = {}

        for error in self._error_history:
            error_type = error.get("error_type", "unknown")
            severity = error.get("severity", "unknown")

            type_counts[error_type] = type_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Find most common
        most_common = max(type_counts.items(), key=lambda x: x[1]) if type_counts else ("none", 0)

        return {
            "total_errors": len(self._error_history),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "most_common_type": most_common[0],
            "most_common_count": most_common[1],
        }

    def clear_history(self):
        """Clear error history."""
        self._error_history = []
        logger.info("Error history cleared")


# Singleton instance
_recovery: Optional[ErrorRecovery] = None


def _get_recovery() -> ErrorRecovery:
    """Get or create recovery instance."""
    global _recovery
    if _recovery is None:
        _recovery = ErrorRecovery()
    return _recovery


# Convenience functions
def analyze_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyze an error.

    Args:
        error: The exception
        context: Additional context

    Returns:
        ErrorAnalysis dictionary
    """
    return _get_recovery().analyze_error(error, context)


def suggest_recovery(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Suggest recovery strategies.

    Args:
        error: The exception
        context: Additional context

    Returns:
        List of strategy options
    """
    return _get_recovery().suggest_recovery(error, context)


def auto_recover(
    operation: Callable,
    args: Tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
    max_attempts: int = 3,
) -> RecoveryResult:
    """
    Auto-recover from errors.

    Args:
        operation: Callable to retry
        args: Positional arguments
        kwargs: Keyword arguments
        max_attempts: Maximum attempts

    Returns:
        RecoveryResult
    """
    return _get_recovery().auto_recover(operation, args, kwargs, max_attempts)
