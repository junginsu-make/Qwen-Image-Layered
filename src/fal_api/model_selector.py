"""
Intelligent Model Selector for Cost-Quality Optimization.

Automatically selects the best AI model based on:
- Task complexity
- Budget constraints
- Quality requirements
- Speed preferences

Supports all models in the ModelRegistry.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

try:
    from .logging_config import get_logger
    from .model_registry import (
        ModelRegistry, ModelInfo, ModelType, ModelTier,
        get_model, list_models
    )
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
        "model_registry",
        _Path(__file__).parent / "model_registry.py"
    )
    _model_registry = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_model_registry)
    ModelRegistry = _model_registry.ModelRegistry
    ModelInfo = _model_registry.ModelInfo
    ModelType = _model_registry.ModelType
    ModelTier = _model_registry.ModelTier
    get_model = _model_registry.get_model
    list_models = _model_registry.list_models

logger = get_logger("model_selector")


class TaskComplexity(Enum):
    """Task complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskType(Enum):
    """Types of tasks for model selection."""
    GENERATION = "generation"
    EDITING = "editing"
    UPSCALING = "upscaling"
    ANALYSIS = "analysis"
    DECOMPOSITION = "decomposition"
    OCR = "ocr"
    STYLE_TRANSFER = "style_transfer"


@dataclass
class ModelRecommendation:
    """Recommendation result from model selector."""
    model: str
    cost: float
    reason: str
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    complexity: TaskComplexity = TaskComplexity.MEDIUM
    confidence: float = 0.8
    estimated_time: float = 5.0  # seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "cost": self.cost,
            "reason": self.reason,
            "alternatives": self.alternatives,
            "complexity": self.complexity.value,
            "confidence": self.confidence,
            "estimated_time": self.estimated_time,
        }


# Complexity indicators in prompts/tasks
COMPLEXITY_INDICATORS = {
    TaskComplexity.LOW: [
        "simple", "basic", "quick", "fast", "preview",
        "icon", "logo", "minimal", "draft"
    ],
    TaskComplexity.MEDIUM: [
        "standard", "normal", "moderate", "regular",
        "product", "photo", "illustration"
    ],
    TaskComplexity.HIGH: [
        "complex", "detailed", "professional", "commercial",
        "artwork", "masterpiece", "high quality", "4k", "8k",
        "intricate", "realistic", "photorealistic"
    ],
}

# Model recommendations by task and complexity
MODEL_RECOMMENDATIONS = {
    TaskType.GENERATION: {
        TaskComplexity.LOW: [
            ("nano-banana", 0.039, "Fast generation for previews"),
            ("flux-schnell", 0.003, "Ultra-fast basic generation"),
        ],
        TaskComplexity.MEDIUM: [
            ("nano-banana", 0.039, "Good balance of speed and quality"),
            ("flux-dev", 0.025, "Higher quality generation"),
        ],
        TaskComplexity.HIGH: [
            ("nano-banana-pro", 0.15, "Best quality for professional use"),
            ("nano-banana-pro", 0.30, "4K quality for commercial projects"),
        ],
    },
    TaskType.EDITING: {
        TaskComplexity.LOW: [
            ("nano-banana-edit", 0.039, "Quick edits"),
            ("lama-inpainting", 0.01, "Simple inpainting"),
        ],
        TaskComplexity.MEDIUM: [
            ("nano-banana-edit", 0.039, "Standard editing"),
        ],
        TaskComplexity.HIGH: [
            ("nano-banana-pro-edit", 0.15, "Advanced semantic editing"),
        ],
    },
    TaskType.UPSCALING: {
        TaskComplexity.LOW: [
            ("creative-upscaler", 0.02, "Standard 2x upscaling"),
        ],
        TaskComplexity.MEDIUM: [
            ("creative-upscaler", 0.02, "Quality 2x upscaling"),
        ],
        TaskComplexity.HIGH: [
            ("creative-upscaler", 0.04, "4x upscaling with enhancement"),
        ],
    },
    TaskType.ANALYSIS: {
        TaskComplexity.LOW: [
            ("llava-next", 0.01, "Basic image analysis"),
        ],
        TaskComplexity.MEDIUM: [
            ("llava-next", 0.01, "Standard analysis"),
        ],
        TaskComplexity.HIGH: [
            ("llava-next", 0.02, "Detailed analysis"),
        ],
    },
}


class ModelSelector:
    """
    Intelligent model selector for optimal cost-quality balance.

    Usage:
        selector = ModelSelector()

        # Get recommendation
        result = selector.select_model(
            task="Generate product photo",
            budget=0.20,
            prefer_quality=True
        )

        print(f"Use: {result['model']} (${result['cost']})")
        print(f"Reason: {result['reason']}")
    """

    def __init__(self):
        """Initialize the selector."""
        self._model_cache: Dict[str, ModelInfo] = {}

    def assess_complexity(
        self,
        task: str,
        image_path: Optional[str] = None
    ) -> TaskComplexity:
        """
        Assess task complexity.

        Args:
            task: Task description
            image_path: Optional image path for context

        Returns:
            TaskComplexity enum value
        """
        task_lower = task.lower()

        # Check for high complexity indicators
        for indicator in COMPLEXITY_INDICATORS[TaskComplexity.HIGH]:
            if indicator in task_lower:
                return TaskComplexity.HIGH

        # Check for low complexity indicators
        for indicator in COMPLEXITY_INDICATORS[TaskComplexity.LOW]:
            if indicator in task_lower:
                return TaskComplexity.LOW

        # Default to medium
        return TaskComplexity.MEDIUM

    def detect_task_type(self, task: str) -> TaskType:
        """
        Detect the type of task.

        Args:
            task: Task description

        Returns:
            TaskType enum value
        """
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["generate", "create", "make", "생성"]):
            return TaskType.GENERATION
        elif any(kw in task_lower for kw in ["edit", "modify", "change", "편집", "수정"]):
            return TaskType.EDITING
        elif any(kw in task_lower for kw in ["upscale", "enlarge", "업스케일", "확대"]):
            return TaskType.UPSCALING
        elif any(kw in task_lower for kw in ["analyze", "describe", "분석", "설명"]):
            return TaskType.ANALYSIS
        elif any(kw in task_lower for kw in ["decompose", "layer", "분해", "레이어"]):
            return TaskType.DECOMPOSITION
        elif any(kw in task_lower for kw in ["ocr", "text", "extract", "텍스트", "추출"]):
            return TaskType.OCR
        elif any(kw in task_lower for kw in ["style", "transfer", "스타일"]):
            return TaskType.STYLE_TRANSFER

        # Default to generation
        return TaskType.GENERATION

    def select_model(
        self,
        task: str,
        budget: Optional[float] = None,
        prefer_quality: bool = False,
        prefer_speed: bool = False,
        task_type: Optional[TaskType] = None,
    ) -> Dict[str, Any]:
        """
        Select the optimal model for a task.

        Args:
            task: Task description
            budget: Maximum budget (optional)
            prefer_quality: Prefer quality over cost
            prefer_speed: Prefer speed over quality
            task_type: Override auto-detected task type

        Returns:
            Dictionary with model recommendation
        """
        # Detect task type and complexity
        detected_type = task_type or self.detect_task_type(task)
        complexity = self.assess_complexity(task)

        # Adjust complexity based on preferences
        if prefer_quality and complexity != TaskComplexity.HIGH:
            complexity = TaskComplexity(
                min(complexity.value, TaskComplexity.HIGH.value)
                if hasattr(complexity, 'value') else TaskComplexity.HIGH
            )
            # Actually upgrade complexity
            if complexity == TaskComplexity.LOW:
                complexity = TaskComplexity.MEDIUM
            elif complexity == TaskComplexity.MEDIUM:
                complexity = TaskComplexity.HIGH

        if prefer_speed and complexity != TaskComplexity.LOW:
            complexity = TaskComplexity.LOW

        # Get recommendations for this task type and complexity
        recommendations = MODEL_RECOMMENDATIONS.get(detected_type, {}).get(complexity, [])

        if not recommendations:
            # Fallback to generation recommendations
            recommendations = MODEL_RECOMMENDATIONS[TaskType.GENERATION][complexity]

        # Filter by budget if specified
        valid_options = []
        for model_name, cost, reason in recommendations:
            if budget is None or cost <= budget:
                valid_options.append((model_name, cost, reason))

        # If no options within budget, suggest cheapest alternative
        if not valid_options and budget is not None:
            # Find cheapest option across all complexities
            all_options = []
            for comp in TaskComplexity:
                opts = MODEL_RECOMMENDATIONS.get(detected_type, {}).get(comp, [])
                all_options.extend(opts)

            all_options.sort(key=lambda x: x[1])
            if all_options:
                cheapest = all_options[0]
                return ModelRecommendation(
                    model=cheapest[0],
                    cost=cheapest[1],
                    reason=f"Budget constrained: {cheapest[2]}",
                    complexity=complexity,
                    confidence=0.6,
                    alternatives=[],
                ).to_dict()

        if not valid_options:
            # Ultimate fallback
            return ModelRecommendation(
                model="nano-banana",
                cost=0.039,
                reason="Default fast generation model",
                complexity=TaskComplexity.MEDIUM,
                confidence=0.5,
            ).to_dict()

        # Select best option
        best = valid_options[0]

        # Build alternatives list
        alternatives = []
        for model_name, cost, reason in valid_options[1:3]:
            alternatives.append({
                "model": model_name,
                "cost": cost,
                "reason": reason,
            })

        # Calculate confidence based on match quality
        confidence = 0.9 if prefer_quality or prefer_speed else 0.85

        # Estimate time (rough approximation)
        estimated_time = 3.0 if complexity == TaskComplexity.LOW else \
                        8.0 if complexity == TaskComplexity.MEDIUM else 15.0

        return ModelRecommendation(
            model=best[0],
            cost=best[1],
            reason=best[2],
            alternatives=alternatives,
            complexity=complexity,
            confidence=confidence,
            estimated_time=estimated_time,
        ).to_dict()

    def calculate_cost_quality_score(
        self,
        model: str,
        task: str,
        budget: Optional[float] = None
    ) -> float:
        """
        Calculate cost-quality score for a model.

        Higher score = better value (quality/cost ratio).

        Args:
            model: Model name
            task: Task description
            budget: Optional budget constraint

        Returns:
            Score between 0 and 1
        """
        # Get model info
        try:
            model_info = get_model(model)
            cost = model_info.price_per_image
        except (KeyError, AttributeError):
            # Unknown model, assume medium cost
            cost = 0.05

        # Quality factor based on model tier
        quality_factors = {
            "nano-banana-pro": 1.0,
            "nano-banana-pro-edit": 1.0,
            "flux-dev": 0.85,
            "nano-banana": 0.75,
            "nano-banana-edit": 0.75,
            "flux-schnell": 0.6,
            "creative-upscaler": 0.8,
            "llava-next": 0.7,
            "lama-inpainting": 0.7,
        }
        quality = quality_factors.get(model, 0.5)

        # Cost efficiency (inverse relationship)
        max_cost = 0.30  # Highest expected cost
        cost_efficiency = 1.0 - (cost / max_cost)

        # Combined score (weighted average)
        score = (quality * 0.6) + (cost_efficiency * 0.4)

        # Budget penalty
        if budget is not None and cost > budget:
            score *= 0.5  # Heavy penalty for over budget

        return min(1.0, max(0.0, score))

    def get_budget_options(
        self,
        task: str,
        min_budget: float = 0.0,
        max_budget: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Get model options across budget range.

        Args:
            task: Task description
            min_budget: Minimum budget
            max_budget: Maximum budget

        Returns:
            List of options sorted by cost
        """
        task_type = self.detect_task_type(task)
        options = []

        for complexity in TaskComplexity:
            recommendations = MODEL_RECOMMENDATIONS.get(task_type, {}).get(complexity, [])
            for model_name, cost, reason in recommendations:
                if min_budget <= cost <= max_budget:
                    options.append({
                        "model": model_name,
                        "cost": cost,
                        "reason": reason,
                        "complexity": complexity.value,
                        "score": self.calculate_cost_quality_score(model_name, task),
                    })

        # Sort by cost
        options.sort(key=lambda x: x["cost"])

        # Remove duplicates
        seen = set()
        unique_options = []
        for opt in options:
            if opt["model"] not in seen:
                seen.add(opt["model"])
                unique_options.append(opt)

        return unique_options


# Singleton instance
_selector: Optional[ModelSelector] = None


def _get_selector() -> ModelSelector:
    """Get or create selector instance."""
    global _selector
    if _selector is None:
        _selector = ModelSelector()
    return _selector


# Convenience functions
def select_model(
    task: str,
    budget: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Select optimal model for a task.

    Args:
        task: Task description
        budget: Optional budget constraint
        **kwargs: Additional options

    Returns:
        Model recommendation dictionary
    """
    return _get_selector().select_model(task, budget=budget, **kwargs)


def assess_complexity(task: str) -> TaskComplexity:
    """
    Assess task complexity.

    Args:
        task: Task description

    Returns:
        TaskComplexity enum
    """
    return _get_selector().assess_complexity(task)


def calculate_cost_quality_score(
    model: str,
    task: str,
    budget: Optional[float] = None
) -> float:
    """
    Calculate cost-quality score.

    Args:
        model: Model name
        task: Task description
        budget: Optional budget

    Returns:
        Score between 0-1
    """
    return _get_selector().calculate_cost_quality_score(model, task, budget)
