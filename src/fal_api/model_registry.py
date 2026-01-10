"""
Model Registry - Extensible Architecture for Fal AI Models

This module provides a flexible registry system for managing multiple AI models.
New models can be easily added without modifying existing code.

Usage:
    from src.fal_api.model_registry import ModelRegistry, get_model, list_models

    # Get a model
    model = get_model("nano-banana-pro")

    # Register a new model
    ModelRegistry.register_model("new-model", {...})

    # List all available models
    models = list_models()
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ModelType(Enum):
    """Types of AI models supported."""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    IMAGE_EDIT = "image_edit"
    UPSCALE = "upscale"
    STYLE_TRANSFER = "style_transfer"
    ANALYSIS = "analysis"


class ModelTier(Enum):
    """Model quality/price tiers."""
    FAST = "fast"        # Quick, lower cost
    STANDARD = "standard"  # Balanced
    PRO = "pro"          # High quality
    ULTRA = "ultra"      # Maximum quality


@dataclass
class ModelInfo:
    """Information about a registered AI model."""
    name: str
    endpoint: str
    model_type: ModelType
    tier: ModelTier
    price_per_image: float
    description: str
    capabilities: List[str] = field(default_factory=list)
    max_resolution: Optional[str] = None
    supports_4k: bool = False
    average_time_seconds: float = 10.0
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "endpoint": self.endpoint,
            "type": self.model_type.value,
            "tier": self.tier.value,
            "price": self.price_per_image,
            "description": self.description,
            "capabilities": self.capabilities,
            "max_resolution": self.max_resolution,
            "supports_4k": self.supports_4k,
            "average_time": self.average_time_seconds,
            "parameters": self.parameters
        }


class ModelRegistry:
    """
    Central registry for all AI models.

    Provides a unified interface for:
    - Registering new models
    - Retrieving model information
    - Listing available models
    - Finding models by capability
    """

    _models: Dict[str, ModelInfo] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        """Initialize with default models if not already done."""
        if not cls._initialized:
            cls._register_default_models()
            cls._initialized = True

    @classmethod
    def _register_default_models(cls):
        """Register all built-in Fal AI models."""

        # =================================================================
        # NANO BANANA MODELS (Google Gemini-based)
        # =================================================================

        cls._models["nano-banana"] = ModelInfo(
            name="nano-banana",
            endpoint="fal-ai/nano-banana",
            model_type=ModelType.TEXT_TO_IMAGE,
            tier=ModelTier.FAST,
            price_per_image=0.039,
            description="Fast text-to-image generation based on Gemini 2.5 Flash",
            capabilities=[
                "text_to_image",
                "fast_generation",
                "basic_prompts",
                "quick_iterations"
            ],
            max_resolution="2K",
            supports_4k=False,
            average_time_seconds=5.0,
            parameters={
                "prompt": {"type": "string", "required": True},
                "aspect_ratio": {"type": "string", "default": "1:1"},
                "num_images": {"type": "int", "default": 1, "max": 4}
            }
        )

        cls._models["nano-banana-pro"] = ModelInfo(
            name="nano-banana-pro",
            endpoint="fal-ai/nano-banana-pro",
            model_type=ModelType.TEXT_TO_IMAGE,
            tier=ModelTier.PRO,
            price_per_image=0.15,
            description="High-quality generation with Gemini 3 Pro - perfect text rendering",
            capabilities=[
                "text_to_image",
                "perfect_text_rendering",
                "character_consistency",
                "semantic_understanding",
                "infographics",
                "4k_output"
            ],
            max_resolution="4K",
            supports_4k=True,
            average_time_seconds=15.0,
            parameters={
                "prompt": {"type": "string", "required": True},
                "aspect_ratio": {"type": "string", "default": "1:1"},
                "resolution": {"type": "string", "default": "2k", "options": ["2k", "4k"]},
                "num_images": {"type": "int", "default": 1, "max": 4}
            }
        )

        cls._models["nano-banana-edit"] = ModelInfo(
            name="nano-banana-edit",
            endpoint="fal-ai/nano-banana/edit",
            model_type=ModelType.IMAGE_EDIT,
            tier=ModelTier.FAST,
            price_per_image=0.039,
            description="Fast image editing with natural language prompts",
            capabilities=[
                "image_editing",
                "object_modification",
                "style_change",
                "quick_edits"
            ],
            max_resolution="2K",
            supports_4k=False,
            average_time_seconds=8.0,
            parameters={
                "image_url": {"type": "string", "required": True},
                "prompt": {"type": "string", "required": True}
            }
        )

        cls._models["nano-banana-pro-edit"] = ModelInfo(
            name="nano-banana-pro-edit",
            endpoint="fal-ai/nano-banana-pro/edit",
            model_type=ModelType.IMAGE_EDIT,
            tier=ModelTier.PRO,
            price_per_image=0.15,
            description="Advanced semantic editing with context understanding",
            capabilities=[
                "advanced_editing",
                "semantic_understanding",
                "relationship_aware",
                "lighting_adjustment",
                "composition_aware",
                "4k_output"
            ],
            max_resolution="4K",
            supports_4k=True,
            average_time_seconds=20.0,
            parameters={
                "image_url": {"type": "string", "required": True},
                "prompt": {"type": "string", "required": True},
                "resolution": {"type": "string", "default": "2k", "options": ["2k", "4k"]}
            }
        )

        # =================================================================
        # FLUX MODELS (for future extension)
        # =================================================================

        cls._models["flux-schnell"] = ModelInfo(
            name="flux-schnell",
            endpoint="fal-ai/flux/schnell",
            model_type=ModelType.TEXT_TO_IMAGE,
            tier=ModelTier.FAST,
            price_per_image=0.003,
            description="Ultra-fast FLUX generation",
            capabilities=[
                "text_to_image",
                "ultra_fast",
                "basic_quality"
            ],
            max_resolution="1024x1024",
            supports_4k=False,
            average_time_seconds=2.0,
            parameters={
                "prompt": {"type": "string", "required": True},
                "image_size": {"type": "string", "default": "square_hd"}
            }
        )

        cls._models["flux-dev"] = ModelInfo(
            name="flux-dev",
            endpoint="fal-ai/flux/dev",
            model_type=ModelType.TEXT_TO_IMAGE,
            tier=ModelTier.STANDARD,
            price_per_image=0.025,
            description="High-quality FLUX generation with fine control",
            capabilities=[
                "text_to_image",
                "high_quality",
                "detailed_control",
                "style_variety"
            ],
            max_resolution="2048x2048",
            supports_4k=False,
            average_time_seconds=10.0,
            parameters={
                "prompt": {"type": "string", "required": True},
                "image_size": {"type": "string", "default": "landscape_4_3"},
                "num_inference_steps": {"type": "int", "default": 28}
            }
        )

        # =================================================================
        # UPSCALE MODELS
        # =================================================================

        cls._models["creative-upscaler"] = ModelInfo(
            name="creative-upscaler",
            endpoint="fal-ai/creative-upscaler",
            model_type=ModelType.UPSCALE,
            tier=ModelTier.STANDARD,
            price_per_image=0.02,
            description="AI upscaling with detail enhancement",
            capabilities=[
                "upscale_2x",
                "upscale_4x",
                "detail_enhancement",
                "noise_reduction"
            ],
            max_resolution="8192x8192",
            supports_4k=True,
            average_time_seconds=15.0,
            parameters={
                "image_url": {"type": "string", "required": True},
                "scale": {"type": "int", "default": 2, "options": [2, 4]}
            }
        )

        # =================================================================
        # ANALYSIS MODELS
        # =================================================================

        cls._models["llava-next"] = ModelInfo(
            name="llava-next",
            endpoint="fal-ai/llava-next",
            model_type=ModelType.ANALYSIS,
            tier=ModelTier.STANDARD,
            price_per_image=0.01,
            description="Vision-language model for image understanding",
            capabilities=[
                "image_analysis",
                "ocr",
                "object_detection",
                "scene_description"
            ],
            max_resolution="4096x4096",
            supports_4k=True,
            average_time_seconds=5.0,
            parameters={
                "image_url": {"type": "string", "required": True},
                "prompt": {"type": "string", "required": True}
            }
        )

        # =================================================================
        # INPAINTING MODELS
        # =================================================================

        cls._models["lama-inpainting"] = ModelInfo(
            name="lama-inpainting",
            endpoint="fal-ai/lama",
            model_type=ModelType.IMAGE_EDIT,
            tier=ModelTier.STANDARD,
            price_per_image=0.01,
            description="Object removal and inpainting",
            capabilities=[
                "object_removal",
                "inpainting",
                "background_fill",
                "text_removal"
            ],
            max_resolution="2048x2048",
            supports_4k=False,
            average_time_seconds=8.0,
            parameters={
                "image_url": {"type": "string", "required": True},
                "mask_url": {"type": "string", "required": True}
            }
        )

    @classmethod
    def register_model(cls, name: str, model_info: ModelInfo) -> None:
        """
        Register a new model or update existing one.

        Args:
            name: Unique model identifier
            model_info: ModelInfo object with model details

        Example:
            ModelRegistry.register_model("my-custom-model", ModelInfo(
                name="my-custom-model",
                endpoint="fal-ai/my-model",
                model_type=ModelType.TEXT_TO_IMAGE,
                tier=ModelTier.STANDARD,
                price_per_image=0.05,
                description="My custom model"
            ))
        """
        cls._ensure_initialized()
        cls._models[name] = model_info

    @classmethod
    def register(cls, name: str, **kwargs) -> None:
        """
        Register a model using keyword arguments.

        Args:
            name: Unique model identifier
            **kwargs: Model properties

        Example:
            ModelRegistry.register(
                "new-model",
                endpoint="fal-ai/new-model",
                model_type=ModelType.TEXT_TO_IMAGE,
                tier=ModelTier.FAST,
                price_per_image=0.01,
                description="New model"
            )
        """
        cls._ensure_initialized()

        # Set defaults
        kwargs.setdefault("name", name)
        kwargs.setdefault("capabilities", [])
        kwargs.setdefault("parameters", {})

        cls._models[name] = ModelInfo(**kwargs)

    @classmethod
    def get_model(cls, name: str) -> Optional[ModelInfo]:
        """
        Get model information by name.

        Args:
            name: Model identifier

        Returns:
            ModelInfo or None if not found
        """
        cls._ensure_initialized()
        return cls._models.get(name)

    @classmethod
    def get(cls, name: str) -> Optional[ModelInfo]:
        """Alias for get_model."""
        return cls.get_model(name)

    @classmethod
    def list_models(cls, model_type: Optional[ModelType] = None,
                    tier: Optional[ModelTier] = None) -> List[ModelInfo]:
        """
        List all registered models with optional filtering.

        Args:
            model_type: Filter by model type
            tier: Filter by tier

        Returns:
            List of matching ModelInfo objects
        """
        cls._ensure_initialized()

        models = list(cls._models.values())

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        if tier:
            models = [m for m in models if m.tier == tier]

        return models

    @classmethod
    def list(cls, **filters) -> List[ModelInfo]:
        """Alias for list_models with flexible filtering."""
        return cls.list_models(
            model_type=filters.get("model_type"),
            tier=filters.get("tier")
        )

    @classmethod
    def find_by_capability(cls, capability: str) -> List[ModelInfo]:
        """
        Find models that have a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of models with that capability
        """
        cls._ensure_initialized()
        return [
            m for m in cls._models.values()
            if capability in m.capabilities
        ]

    @classmethod
    def get_cheapest(cls, model_type: ModelType) -> Optional[ModelInfo]:
        """Get the cheapest model of a given type."""
        cls._ensure_initialized()
        models = cls.list_models(model_type=model_type)
        if not models:
            return None
        return min(models, key=lambda m: m.price_per_image)

    @classmethod
    def get_best_quality(cls, model_type: ModelType) -> Optional[ModelInfo]:
        """Get the highest quality model of a given type."""
        cls._ensure_initialized()
        tier_priority = {
            ModelTier.ULTRA: 4,
            ModelTier.PRO: 3,
            ModelTier.STANDARD: 2,
            ModelTier.FAST: 1
        }
        models = cls.list_models(model_type=model_type)
        if not models:
            return None
        return max(models, key=lambda m: tier_priority.get(m.tier, 0))

    @classmethod
    def model_names(cls) -> List[str]:
        """Get list of all registered model names."""
        cls._ensure_initialized()
        return list(cls._models.keys())

    @classmethod
    def add_model(cls, name: str, model_info: ModelInfo) -> None:
        """Alias for register_model for extensibility."""
        cls.register_model(name, model_info)


# =============================================================================
# Convenience Functions
# =============================================================================

def get_model(name: str) -> Optional[ModelInfo]:
    """Get a model by name."""
    return ModelRegistry.get_model(name)


def list_models(model_type: Optional[ModelType] = None,
                tier: Optional[ModelTier] = None) -> List[ModelInfo]:
    """List all models with optional filtering."""
    return ModelRegistry.list_models(model_type, tier)


def find_models_by_capability(capability: str) -> List[ModelInfo]:
    """Find models with a specific capability."""
    return ModelRegistry.find_by_capability(capability)


def get_generation_models() -> List[ModelInfo]:
    """Get all text-to-image generation models."""
    return ModelRegistry.list_models(model_type=ModelType.TEXT_TO_IMAGE)


def get_edit_models() -> List[ModelInfo]:
    """Get all image editing models."""
    return ModelRegistry.list_models(model_type=ModelType.IMAGE_EDIT)


def select_best_model(
    task: str,
    prefer_quality: bool = False,
    prefer_speed: bool = False,
    max_price: Optional[float] = None
) -> Optional[ModelInfo]:
    """
    Intelligently select the best model for a task.

    Args:
        task: Description of the task
        prefer_quality: Prefer higher quality over cost
        prefer_speed: Prefer faster models
        max_price: Maximum price per image

    Returns:
        Best matching ModelInfo or None
    """
    task_lower = task.lower()

    # Determine model type from task
    if any(t in task_lower for t in ["generate", "create", "draw", "make"]):
        model_type = ModelType.TEXT_TO_IMAGE
    elif any(t in task_lower for t in ["edit", "modify", "change"]):
        model_type = ModelType.IMAGE_EDIT
    elif any(t in task_lower for t in ["upscale", "enlarge", "enhance"]):
        model_type = ModelType.UPSCALE
    elif any(t in task_lower for t in ["analyze", "ocr", "describe"]):
        model_type = ModelType.ANALYSIS
    else:
        model_type = ModelType.TEXT_TO_IMAGE  # default

    models = ModelRegistry.list_models(model_type=model_type)

    if not models:
        return None

    # Filter by price
    if max_price is not None:
        models = [m for m in models if m.price_per_image <= max_price]

    if not models:
        return None

    # Sort by preference
    if prefer_quality:
        return ModelRegistry.get_best_quality(model_type)
    elif prefer_speed:
        return min(models, key=lambda m: m.average_time_seconds)
    else:
        # Balance: consider both price and quality
        tier_priority = {
            ModelTier.ULTRA: 4,
            ModelTier.PRO: 3,
            ModelTier.STANDARD: 2,
            ModelTier.FAST: 1
        }
        return max(models, key=lambda m: tier_priority.get(m.tier, 0) / (m.price_per_image + 0.01))


# Initialize on import
ModelRegistry._ensure_initialized()
