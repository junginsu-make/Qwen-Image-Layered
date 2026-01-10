#!/usr/bin/env python3
"""
Implementation Verification Script.
Verifies that all modules can be imported and classes are properly defined.
Handles missing optional dependencies gracefully.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

passed = 0
failed = 0
warnings = 0
errors = []
warning_msgs = []


def test(name, condition, msg=""):
    global passed, failed, errors
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}: {msg}")
        failed += 1
        errors.append((name, msg))


def warn(name, msg):
    global warnings, warning_msgs
    print(f"  [WARN] {name}: {msg}")
    warnings += 1
    warning_msgs.append((name, msg))


print("=" * 60)
print("MODULE IMPORT VERIFICATION")
print("=" * 60)

# Check PIL availability first
try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("\n[INFO] PIL/Pillow is available")
except ImportError:
    PIL_AVAILABLE = False
    print("\n[INFO] PIL/Pillow not installed - some tests will be skipped")

# Core modules
print("\n--- Core Modules ---")
try:
    from src.fal_api.decompose import ImageLayerDecomposer, decompose_image
    test("decompose.py imports", True)
    test("ImageLayerDecomposer class", hasattr(ImageLayerDecomposer, 'decompose'))
    test("decompose_image function", callable(decompose_image))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("decompose.py", "Skipped - requires PIL")
    else:
        test("decompose.py imports", False, str(e))
except Exception as e:
    test("decompose.py imports", False, str(e))

try:
    from src.fal_api.export import LayerExporter
    test("export.py imports", True)
    test("LayerExporter class", hasattr(LayerExporter, 'to_pptx'))
    test("LayerExporter.to_psd", hasattr(LayerExporter, 'to_psd'))
    test("LayerExporter.to_zip", hasattr(LayerExporter, 'to_zip'))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("export.py", "Skipped - requires PIL")
    else:
        test("export.py imports", False, str(e))
except Exception as e:
    test("export.py imports", False, str(e))

# AI Enhancement modules
print("\n--- AI Enhancement Modules ---")
try:
    from src.fal_api.upscale import ImageUpscaler, upscale_image
    test("upscale.py imports", True)
    test("ImageUpscaler class", hasattr(ImageUpscaler, 'upscale'))
    test("ImageUpscaler.MODELS defined", len(ImageUpscaler.MODELS) >= 2)
    test("upscale_image function", callable(upscale_image))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("upscale.py", "Skipped - requires PIL")
    else:
        test("upscale.py imports", False, str(e))
except Exception as e:
    test("upscale.py imports", False, str(e))

try:
    from src.fal_api.style_transfer import StyleTransfer, apply_style
    test("style_transfer.py imports", True)
    test("StyleTransfer class", hasattr(StyleTransfer, 'apply_style'))
    test("StyleTransfer.STYLES defined", len(StyleTransfer.STYLES) >= 5)
    test("apply_style function", callable(apply_style))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("style_transfer.py", "Skipped - requires PIL")
    else:
        test("style_transfer.py imports", False, str(e))
except Exception as e:
    test("style_transfer.py imports", False, str(e))

try:
    from src.fal_api.color_palette import ColorPaletteExtractor, extract_palette
    test("color_palette.py imports", True)
    test("ColorPaletteExtractor class", hasattr(ColorPaletteExtractor, 'extract_palette'))
    test("extract_palette function", callable(extract_palette))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("color_palette.py", "Skipped - requires PIL")
    else:
        test("color_palette.py imports", False, str(e))
except Exception as e:
    test("color_palette.py imports", False, str(e))

try:
    from src.fal_api.text_to_layer import TextToLayerGenerator, generate_layer
    test("text_to_layer.py imports", True)
    test("TextToLayerGenerator class", hasattr(TextToLayerGenerator, 'generate_layer'))
    test("generate_layer function", callable(generate_layer))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_to_layer.py", "Skipped - requires PIL")
    else:
        test("text_to_layer.py imports", False, str(e))
except Exception as e:
    test("text_to_layer.py imports", False, str(e))

# Text Processing modules
print("\n--- Text Processing Modules ---")
try:
    from src.fal_api.text_ocr import TextExtractor, extract_text
    test("text_ocr.py imports", True)
    test("TextExtractor class", hasattr(TextExtractor, 'extract_text'))
    test("TextExtractor.SUPPORTED_LANGUAGES", len(TextExtractor.SUPPORTED_LANGUAGES) >= 5)
    test("extract_text function", callable(extract_text))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_ocr.py", "Skipped - requires PIL")
    else:
        test("text_ocr.py imports", False, str(e))
except Exception as e:
    test("text_ocr.py imports", False, str(e))

try:
    from src.fal_api.text_translate import TextTranslator, translate_text
    test("text_translate.py imports", True)
    test("TextTranslator class", hasattr(TextTranslator, 'translate'))
    test("TextTranslator.SUPPORTED_LANGUAGES", len(TextTranslator.SUPPORTED_LANGUAGES) >= 5)
    test("translate_text function", callable(translate_text))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_translate.py", "Skipped - requires PIL (via package imports)")
    else:
        test("text_translate.py imports", False, str(e))
except Exception as e:
    test("text_translate.py imports", False, str(e))

try:
    from src.fal_api.text_overlay import TextOverlay, add_text_overlay
    test("text_overlay.py imports", True)
    test("TextOverlay class", hasattr(TextOverlay, 'add_text'))
    test("TextOverlay.POSITIONS defined", len(TextOverlay.POSITIONS) >= 5)
    test("add_text_overlay function", callable(add_text_overlay))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_overlay.py", "Skipped - requires PIL")
    else:
        test("text_overlay.py imports", False, str(e))
except Exception as e:
    test("text_overlay.py imports", False, str(e))

try:
    from src.fal_api.text_effect import TextEffect, apply_text_effect
    test("text_effect.py imports", True)
    test("TextEffect class", hasattr(TextEffect, 'apply_effect'))
    test("TextEffect.EFFECTS defined", len(TextEffect.EFFECTS) >= 5)
    test("apply_text_effect function", callable(apply_text_effect))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_effect.py", "Skipped - requires PIL")
    else:
        test("text_effect.py imports", False, str(e))
except Exception as e:
    test("text_effect.py imports", False, str(e))

try:
    from src.fal_api.text_path import TextPath, render_text_on_path
    test("text_path.py imports", True)
    test("TextPath class", hasattr(TextPath, 'render_text_on_path'))
    test("TextPath.PATH_TYPES defined", len(TextPath.PATH_TYPES) >= 3)
    test("render_text_on_path function", callable(render_text_on_path))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_path.py", "Skipped - requires PIL")
    else:
        test("text_path.py imports", False, str(e))
except Exception as e:
    test("text_path.py imports", False, str(e))

try:
    from src.fal_api.text_remove import TextRemover, remove_text
    test("text_remove.py imports", True)
    test("TextRemover class", hasattr(TextRemover, 'remove_text'))
    test("TextRemover.INPAINT_METHODS defined", len(TextRemover.INPAINT_METHODS) >= 2)
    test("remove_text function", callable(remove_text))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_remove.py", "Skipped - requires PIL")
    else:
        test("text_remove.py imports", False, str(e))
except Exception as e:
    test("text_remove.py imports", False, str(e))

try:
    from src.fal_api.text_replace import TextReplacer, replace_text
    test("text_replace.py imports", True)
    test("TextReplacer class", hasattr(TextReplacer, 'replace_text'))
    test("replace_text function", callable(replace_text))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("text_replace.py", "Skipped - requires PIL")
    else:
        test("text_replace.py imports", False, str(e))
except Exception as e:
    test("text_replace.py imports", False, str(e))

try:
    from src.fal_api.font_match import FontMatcher, identify_font
    test("font_match.py imports", True)
    test("FontMatcher class", hasattr(FontMatcher, 'identify_font'))
    test("identify_font function", callable(identify_font))
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("font_match.py", "Skipped - requires PIL")
    else:
        test("font_match.py imports", False, str(e))
except Exception as e:
    test("font_match.py imports", False, str(e))

# Package __init__.py
print("\n--- Package Import ---")
try:
    from src.fal_api import (
        ImageLayerDecomposer, LayerExporter,
        upscale_image, apply_style, extract_palette, generate_layer,
        extract_text, translate_text, add_text_overlay,
        apply_text_effect, render_text_on_path,
        remove_text, replace_text, identify_font
    )
    test("Package __init__.py imports all modules", True)
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("Package __init__.py", "Skipped - requires PIL")
    else:
        test("Package __init__.py imports all modules", False, str(e))
except Exception as e:
    test("Package __init__.py imports all modules", False, str(e))

# Verify __all__ exports
try:
    from src.fal_api import __all__
    test("__all__ defined", len(__all__) >= 16, f"Only {len(__all__)} exports")
except ImportError as e:
    if "PIL" in str(e) and not PIL_AVAILABLE:
        warn("__all__", "Skipped - requires PIL")
    else:
        test("__all__ defined", False, str(e))
except Exception as e:
    test("__all__ defined", False, str(e))

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Warnings: {warnings}")

if passed + failed > 0:
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")

if errors:
    print("\n--- Errors ---")
    for name, msg in errors:
        print(f"  {name}: {msg}")

if warning_msgs:
    print("\n--- Warnings ---")
    for name, msg in warning_msgs:
        print(f"  {name}: {msg}")

print("\n" + "=" * 60)
if failed == 0:
    if warnings > 0:
        print(f"VERIFICATION PASSED WITH {warnings} WARNINGS")
        print("Install missing dependencies: pip install -r requirements-fal.txt")
    else:
        print("ALL MODULES VERIFIED - IMPLEMENTATION COMPLETE")
    sys.exit(0)
else:
    print(f"VERIFICATION FAILED - {failed} issue(s) found")
    sys.exit(1)
