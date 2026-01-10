"""
Fal AI integration for Qwen-Image-Layered.
Provides cloud-based image layer decomposition and processing.
"""

# Logging configuration (import first)
from .logging_config import (
    LoggerFactory, get_logger, configure_logging
)

# Cost tracking
from .cost_tracker import (
    CostTracker, CostEntry, OperationType,
    get_tracker, record_cost, get_total_cost, get_cost_report, set_budget_limit
)

# Path validation
from .path_validator import (
    PathValidator, validate_image, validate_output, ensure_dir,
    list_images, get_unique_path, safe_filename,
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_EXPORT_FORMATS
)

# Health check
from .health_check import (
    HealthChecker, CheckStatus,
    run_health_check, get_system_status, get_recent_errors,
    record_error, get_health_report, get_json_health_report
)

# Error handling (import first, no PIL dependency)
from .errors import (
    FalAPIError, APIKeyError, NetworkError, APITimeoutError,
    APIRateLimitError, ImageProcessingError, InvalidInputError,
    DependencyError, safe_result, error_result, handle_api_errors,
    retry_on_error, validate_api_key, validate_file_exists
)

# Model Registry (import before generation, no PIL dependency)
from .model_registry import (
    ModelRegistry, ModelInfo, ModelType, ModelTier,
    get_model, list_models, find_models_by_capability,
    get_generation_models, get_edit_models, select_best_model
)

# Core modules
from .decompose import ImageLayerDecomposer, decompose_image
from .export import LayerExporter

# AI Enhancement modules
from .upscale import ImageUpscaler, upscale_image
from .style_transfer import StyleTransfer, apply_style
from .color_palette import ColorPaletteExtractor, extract_palette
from .text_to_layer import TextToLayerGenerator, generate_layer

# Text Processing modules
from .text_ocr import TextExtractor, extract_text
from .text_translate import TextTranslator, translate_text
from .text_overlay import TextOverlay, add_text_overlay
from .text_effect import TextEffect, apply_text_effect
from .text_path import TextPath, render_text_on_path
from .text_remove import TextRemover, remove_text
from .text_replace import TextReplacer, replace_text
from .font_match import FontMatcher, identify_font

# Phase 3: Generation modules
from .generation import (
    generate_image, edit_image,
    batch_generate, batch_edit,
    get_available_models, recommend_model,
    quick_generate, pro_generate,
    quick_edit, pro_edit
)

__all__ = [
    # Logging
    'LoggerFactory',
    'get_logger',
    'configure_logging',
    # Cost Tracking
    'CostTracker',
    'CostEntry',
    'OperationType',
    'get_tracker',
    'record_cost',
    'get_total_cost',
    'get_cost_report',
    'set_budget_limit',
    # Path Validation
    'PathValidator',
    'validate_image',
    'validate_output',
    'ensure_dir',
    'list_images',
    'get_unique_path',
    'safe_filename',
    'SUPPORTED_IMAGE_FORMATS',
    'SUPPORTED_EXPORT_FORMATS',
    # Health Check
    'HealthChecker',
    'CheckStatus',
    'run_health_check',
    'get_system_status',
    'get_recent_errors',
    'record_error',
    'get_health_report',
    'get_json_health_report',
    # Error handling
    'FalAPIError',
    'APIKeyError',
    'NetworkError',
    'APITimeoutError',
    'APIRateLimitError',
    'ImageProcessingError',
    'InvalidInputError',
    'DependencyError',
    'safe_result',
    'error_result',
    'handle_api_errors',
    'retry_on_error',
    'validate_api_key',
    'validate_file_exists',
    # Model Registry
    'ModelRegistry',
    'ModelInfo',
    'ModelType',
    'ModelTier',
    'get_model',
    'list_models',
    'find_models_by_capability',
    'get_generation_models',
    'get_edit_models',
    'select_best_model',
    # Core
    'ImageLayerDecomposer',
    'decompose_image',
    'LayerExporter',
    # AI Enhancement
    'ImageUpscaler',
    'upscale_image',
    'StyleTransfer',
    'apply_style',
    'ColorPaletteExtractor',
    'extract_palette',
    'TextToLayerGenerator',
    'generate_layer',
    # Text Processing
    'TextExtractor',
    'extract_text',
    'TextTranslator',
    'translate_text',
    'TextOverlay',
    'add_text_overlay',
    'TextEffect',
    'apply_text_effect',
    'TextPath',
    'render_text_on_path',
    'TextRemover',
    'remove_text',
    'TextReplacer',
    'replace_text',
    'FontMatcher',
    'identify_font',
    # Phase 3: Generation
    'generate_image',
    'edit_image',
    'batch_generate',
    'batch_edit',
    'get_available_models',
    'recommend_model',
    'quick_generate',
    'pro_generate',
    'quick_edit',
    'pro_edit',
]
