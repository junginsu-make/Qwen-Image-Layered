"""
Fal AI integration for Qwen-Image-Layered.
Provides cloud-based image layer decomposition and processing.
"""

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

__all__ = [
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
]
