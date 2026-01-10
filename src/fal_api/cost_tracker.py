"""
Cost tracking module for Qwen-Image-Layered.

Tracks API usage costs across all operations with:
- Per-operation cost recording
- Session and cumulative totals
- Cost reports and summaries
- Budget warnings
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

try:
    from .logging_config import get_logger
except ImportError:
    # Fallback for direct module loading
    import importlib.util as _util
    from pathlib import Path as _Path
    _spec = _util.spec_from_file_location(
        "logging_config",
        _Path(__file__).parent / "logging_config.py"
    )
    _logging_config = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_logging_config)
    get_logger = _logging_config.get_logger

logger = get_logger("cost_tracker")


class OperationType(Enum):
    """Types of billable operations."""
    DECOMPOSE = "decompose"
    GENERATE = "generate"
    EDIT = "edit"
    UPSCALE = "upscale"
    STYLE_TRANSFER = "style_transfer"
    OCR = "ocr"
    TEXT_REMOVE = "text_remove"
    TEXT_REPLACE = "text_replace"
    ANALYSIS = "analysis"
    OTHER = "other"


# Default cost per operation (in USD)
DEFAULT_COSTS = {
    OperationType.DECOMPOSE: 0.05,
    OperationType.GENERATE: 0.039,  # nano-banana
    OperationType.EDIT: 0.039,  # nano-banana-edit
    OperationType.UPSCALE: 0.02,
    OperationType.STYLE_TRANSFER: 0.03,
    OperationType.OCR: 0.01,
    OperationType.TEXT_REMOVE: 0.03,
    OperationType.TEXT_REPLACE: 0.03,
    OperationType.ANALYSIS: 0.01,
    OperationType.OTHER: 0.01,
}


@dataclass
class CostEntry:
    """A single cost entry."""
    timestamp: datetime
    operation: OperationType
    model: str
    cost: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation.value,
            "model": self.model,
            "cost": self.cost,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostEntry":
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            operation=OperationType(data["operation"]),
            model=data["model"],
            cost=data["cost"],
            details=data.get("details", {}),
        )


class CostTracker:
    """
    Tracks API usage costs.

    Usage:
        tracker = CostTracker()
        tracker.record(OperationType.GENERATE, "nano-banana", 0.039)
        print(f"Total: ${tracker.get_total():.2f}")
    """

    _instance: Optional["CostTracker"] = None

    def __init__(
        self,
        budget_limit: Optional[float] = None,
        persist_path: Optional[str] = None,
    ):
        """
        Initialize cost tracker.

        Args:
            budget_limit: Optional budget limit (USD) for warnings
            persist_path: Path to persist cost history
        """
        self.entries: List[CostEntry] = []
        self.budget_limit = budget_limit
        self.persist_path = Path(persist_path) if persist_path else None
        self._session_start = datetime.now()

        # Load existing history if persist path exists
        if self.persist_path and self.persist_path.exists():
            self._load_history()

    @classmethod
    def get_instance(cls, **kwargs) -> "CostTracker":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance."""
        cls._instance = None

    def record(
        self,
        operation: OperationType,
        model: str,
        cost: Optional[float] = None,
        **details: Any,
    ) -> CostEntry:
        """
        Record a cost entry.

        Args:
            operation: Type of operation
            model: Model used
            cost: Cost in USD (uses default if not provided)
            **details: Additional details (image count, etc.)

        Returns:
            The created CostEntry
        """
        if cost is None:
            cost = DEFAULT_COSTS.get(operation, 0.01)

        entry = CostEntry(
            timestamp=datetime.now(),
            operation=operation,
            model=model,
            cost=cost,
            details=details,
        )
        self.entries.append(entry)

        logger.info(f"Cost recorded: ${cost:.4f} for {operation.value} ({model})")

        # Check budget
        if self.budget_limit:
            total = self.get_total()
            if total >= self.budget_limit:
                logger.warning(f"Budget limit reached! Total: ${total:.2f} >= ${self.budget_limit:.2f}")
            elif total >= self.budget_limit * 0.8:
                logger.warning(f"Approaching budget limit: ${total:.2f} / ${self.budget_limit:.2f}")

        # Auto-persist if path configured
        if self.persist_path:
            self._save_history()

        return entry

    def get_total(self) -> float:
        """Get total cost."""
        return sum(e.cost for e in self.entries)

    def get_session_total(self) -> float:
        """Get total cost for current session."""
        return sum(
            e.cost for e in self.entries
            if e.timestamp >= self._session_start
        )

    def get_by_operation(self) -> Dict[str, float]:
        """Get costs grouped by operation type."""
        result: Dict[str, float] = {}
        for entry in self.entries:
            key = entry.operation.value
            result[key] = result.get(key, 0) + entry.cost
        return result

    def get_by_model(self) -> Dict[str, float]:
        """Get costs grouped by model."""
        result: Dict[str, float] = {}
        for entry in self.entries:
            result[entry.model] = result.get(entry.model, 0) + entry.cost
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost summary."""
        return {
            "total_cost": self.get_total(),
            "session_cost": self.get_session_total(),
            "entry_count": len(self.entries),
            "by_operation": self.get_by_operation(),
            "by_model": self.get_by_model(),
            "budget_limit": self.budget_limit,
            "budget_remaining": (
                self.budget_limit - self.get_total()
                if self.budget_limit else None
            ),
            "session_start": self._session_start.isoformat(),
        }

    def get_report(self) -> str:
        """Generate human-readable cost report."""
        summary = self.get_summary()

        lines = [
            "=" * 50,
            "Cost Report",
            "=" * 50,
            f"Total Cost: ${summary['total_cost']:.4f}",
            f"Session Cost: ${summary['session_cost']:.4f}",
            f"Operations: {summary['entry_count']}",
            "",
            "By Operation:",
        ]

        for op, cost in summary["by_operation"].items():
            lines.append(f"  {op}: ${cost:.4f}")

        lines.append("")
        lines.append("By Model:")

        for model, cost in summary["by_model"].items():
            lines.append(f"  {model}: ${cost:.4f}")

        if summary["budget_limit"]:
            lines.append("")
            lines.append(f"Budget Limit: ${summary['budget_limit']:.2f}")
            lines.append(f"Budget Remaining: ${summary['budget_remaining']:.2f}")

        lines.append("=" * 50)

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all entries."""
        self.entries = []
        self._session_start = datetime.now()
        logger.info("Cost tracker cleared")

    def _load_history(self) -> None:
        """Load history from file."""
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entries = [CostEntry.from_dict(e) for e in data.get("entries", [])]
                logger.info(f"Loaded {len(self.entries)} cost entries from history")
        except Exception as e:
            logger.warning(f"Failed to load cost history: {e}")

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "entries": [e.to_dict() for e in self.entries],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cost history: {e}")


# Convenience functions
def get_tracker(**kwargs) -> CostTracker:
    """Get the global cost tracker instance."""
    return CostTracker.get_instance(**kwargs)


def record_cost(
    operation: OperationType,
    model: str,
    cost: Optional[float] = None,
    **details: Any,
) -> CostEntry:
    """Record a cost to the global tracker."""
    return get_tracker().record(operation, model, cost, **details)


def get_total_cost() -> float:
    """Get total cost from global tracker."""
    return get_tracker().get_total()


def get_cost_report() -> str:
    """Get cost report from global tracker."""
    return get_tracker().get_report()


def set_budget_limit(limit: float) -> None:
    """Set budget limit on global tracker."""
    get_tracker().budget_limit = limit
    logger.info(f"Budget limit set to ${limit:.2f}")
