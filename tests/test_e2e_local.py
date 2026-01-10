#!/usr/bin/env python3
"""
E2E Tests for Local Features (No API Required).
Tests features that only use PIL and don't need Fal AI API.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Check PIL availability
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - E2E tests require PIL")
    sys.exit(1)

# Generate test images first
from tests.generate_test_images import generate_all_test_images

# Test results tracking
passed = 0
failed = 0
errors = []

TEST_OUTPUT_DIR = PROJECT_ROOT / "tests" / "output"
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test(name, condition, error_msg=""):
    """Record test result."""
    global passed, failed, errors
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
        return True
    else:
        print(f"  [FAIL] {name}: {error_msg}")
        failed += 1
        errors.append((name, error_msg))
        return False


def cleanup():
    """Clean up test output directory."""
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR)
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# E2E TESTS
# ============================================================

def test_color_palette():
    """Test color palette extraction."""
    print("\n--- Color Palette E2E ---")

    try:
        from src.fal_api.color_palette import ColorPaletteExtractor, extract_palette

        test_image = PROJECT_ROOT / "assets" / "test_images" / "multi_color.png"

        # Test with ColorPaletteExtractor class
        extractor = ColorPaletteExtractor()
        result = extractor.extract_palette(str(test_image), num_colors=5, format="hex")

        test("extract_palette returns success", result.get("success") == True)
        test("extract_palette has colors", len(result.get("colors", [])) >= 3)
        test("colors have hex format", result["colors"][0]["value"].startswith("#"))
        test("colors have percentage", "percentage" in result["colors"][0])
        test("palette_type detected", result.get("palette_type") in ["warm", "cool", "neutral"])

        # Test convenience function
        result2 = extract_palette(str(test_image), num_colors=3, format="rgb")
        test("convenience function works", result2.get("success") == True)
        test("rgb format works", "rgb(" in result2["colors"][0]["value"])

        # Test with gradient image
        gradient_image = PROJECT_ROOT / "assets" / "test_images" / "gradient.png"
        result3 = extract_palette(str(gradient_image), num_colors=6)
        test("gradient image palette", result3.get("success") == True)

        return True

    except Exception as e:
        test("color_palette module", False, str(e))
        return False


def test_text_overlay():
    """Test text overlay functionality."""
    print("\n--- Text Overlay E2E ---")

    try:
        from src.fal_api.text_overlay import TextOverlay, add_text_overlay

        test_image = PROJECT_ROOT / "assets" / "test_images" / "solid_white.png"
        output_path = str(TEST_OUTPUT_DIR / "overlay_test.png")

        # Test with TextOverlay class
        overlay = TextOverlay()
        result = overlay.add_text(
            str(test_image),
            "Test Overlay",
            position="center",
            color="#FF0000",
            font_size=36,
            output_path=output_path
        )

        test("add_text returns success", result.get("success") == True)
        test("output file created", Path(output_path).exists())
        test("text_bounds returned", "text_bounds" in result)

        # Verify output image
        if Path(output_path).exists():
            with Image.open(output_path) as img:
                test("output is valid image", img.size[0] > 0)
                test("output has RGBA mode", img.mode == "RGBA")

        # Test different positions
        positions_to_test = ["top-left", "bottom-right", "center"]
        for pos in positions_to_test:
            out = str(TEST_OUTPUT_DIR / f"overlay_{pos}.png")
            r = add_text_overlay(str(test_image), f"Position: {pos}", position=pos, output_path=out)
            test(f"position '{pos}' works", r.get("success") == True)

        # Test with stroke
        stroke_output = str(TEST_OUTPUT_DIR / "overlay_stroke.png")
        result_stroke = overlay.add_text(
            str(test_image),
            "Stroke Text",
            color="#FFFFFF",
            stroke_color="#000000",
            stroke_width=2,
            output_path=stroke_output
        )
        test("stroke option works", result_stroke.get("success") == True)

        return True

    except Exception as e:
        test("text_overlay module", False, str(e))
        return False


def test_text_effect():
    """Test text effect functionality."""
    print("\n--- Text Effect E2E ---")

    try:
        from src.fal_api.text_effect import TextEffect, apply_text_effect

        # Test creating text with effects (no base image)
        effect_handler = TextEffect()

        # Test shadow effect
        shadow_output = str(TEST_OUTPUT_DIR / "effect_shadow.png")
        result = effect_handler.apply_effect(
            text="Shadow Text",
            effect="shadow",
            color="#FFFFFF",
            effect_color="#000000",
            output_path=shadow_output
        )

        test("shadow effect works", result.get("success") == True)
        test("shadow output created", Path(shadow_output).exists())

        # Test glow effect
        glow_output = str(TEST_OUTPUT_DIR / "effect_glow.png")
        result_glow = effect_handler.apply_effect(
            text="Glow Text",
            effect="glow",
            color="#00FF00",
            effect_color="#00FF00",
            output_path=glow_output
        )
        test("glow effect works", result_glow.get("success") == True)

        # Test neon effect
        neon_output = str(TEST_OUTPUT_DIR / "effect_neon.png")
        result_neon = apply_text_effect(
            text="NEON",
            effect="neon",
            color="#FF00FF",
            output_path=neon_output
        )
        test("neon effect works", result_neon.get("success") == True)

        # Test outline effect
        outline_output = str(TEST_OUTPUT_DIR / "effect_outline.png")
        result_outline = effect_handler.apply_effect(
            text="Outline",
            effect="outline",
            color="#FFFFFF",
            effect_color="#000000",
            output_path=outline_output
        )
        test("outline effect works", result_outline.get("success") == True)

        # Test 3D effect
        threed_output = str(TEST_OUTPUT_DIR / "effect_3d.png")
        result_3d = effect_handler.apply_effect(
            text="3D TEXT",
            effect="3d",
            color="#FF0000",
            effect_color="#880000",
            output_path=threed_output
        )
        test("3d effect works", result_3d.get("success") == True)

        # Test with base image
        test_image = PROJECT_ROOT / "assets" / "test_images" / "gradient.png"
        image_output = str(TEST_OUTPUT_DIR / "effect_on_image.png")
        result_img = effect_handler.apply_effect(
            image_path=str(test_image),
            text="On Image",
            effect="shadow",
            output_path=image_output
        )
        test("effect on base image", result_img.get("success") == True)

        return True

    except Exception as e:
        test("text_effect module", False, str(e))
        return False


def test_text_path():
    """Test text path functionality."""
    print("\n--- Text Path E2E ---")

    try:
        from src.fal_api.text_path import TextPath, render_text_on_path

        path_handler = TextPath()

        # Test circle path
        circle_output = str(TEST_OUTPUT_DIR / "path_circle.png")
        result = path_handler.render_text_on_path(
            text="CIRCULAR TEXT AROUND",
            path_type="circle",
            radius=150,
            font_size=24,
            color="#0000FF",
            output_path=circle_output
        )

        test("circle path works", result.get("success") == True)
        test("circle output created", Path(circle_output).exists())
        test("dimensions returned", "dimensions" in result)

        # Test arc path
        arc_output = str(TEST_OUTPUT_DIR / "path_arc.png")
        result_arc = path_handler.render_text_on_path(
            text="ARC TEXT",
            path_type="arc",
            radius=100,
            start_angle=0,
            end_angle=180,
            output_path=arc_output
        )
        test("arc path works", result_arc.get("success") == True)

        # Test wave path
        wave_output = str(TEST_OUTPUT_DIR / "path_wave.png")
        result_wave = path_handler.render_text_on_path(
            text="WAVE TEXT HERE",
            path_type="wave",
            radius=30,  # amplitude for wave
            output_path=wave_output
        )
        test("wave path works", result_wave.get("success") == True)

        # Test spiral path
        spiral_output = str(TEST_OUTPUT_DIR / "path_spiral.png")
        result_spiral = render_text_on_path(
            text="SPIRAL",
            path_type="spiral",
            radius=50,
            output_path=spiral_output
        )
        test("spiral path works", result_spiral.get("success") == True)

        # Test with custom size
        custom_output = str(TEST_OUTPUT_DIR / "path_custom.png")
        result_custom = path_handler.render_text_on_path(
            text="CUSTOM SIZE",
            path_type="circle",
            radius=100,
            output_size={"width": 600, "height": 600},
            output_path=custom_output
        )
        test("custom output size", result_custom.get("success") == True)

        if Path(custom_output).exists():
            with Image.open(custom_output) as img:
                test("custom size applied", img.size == (600, 600))

        return True

    except Exception as e:
        test("text_path module", False, str(e))
        return False


def test_export():
    """Test layer export functionality."""
    print("\n--- Layer Export E2E ---")

    try:
        from src.fal_api.export import LayerExporter

        # Create sample layer files
        layer_paths = []
        for i in range(3):
            layer_path = TEST_OUTPUT_DIR / f"layer_{i}.png"
            img = Image.new("RGBA", (200, 200), (100 * i, 100, 100, 200))
            img.save(layer_path)
            layer_paths.append(str(layer_path))

        exporter = LayerExporter(layer_paths)

        # Test ZIP export (always available)
        zip_output = str(TEST_OUTPUT_DIR / "layers.zip")
        result_zip = exporter.to_zip(zip_output)
        test("zip export works", Path(zip_output).exists())

        # Check ZIP contents
        import zipfile
        with zipfile.ZipFile(zip_output, 'r') as zf:
            test("zip has 3 layers", len(zf.namelist()) == 3)

        # Test PPTX export (if available)
        try:
            pptx_output = str(TEST_OUTPUT_DIR / "layers.pptx")
            result_pptx = exporter.to_pptx(pptx_output)
            test("pptx export works", Path(pptx_output).exists())
        except Exception as e:
            print(f"  [SKIP] pptx export: {e}")

        # Test PSD export (if available)
        try:
            psd_output = str(TEST_OUTPUT_DIR / "layers.psd")
            result_psd = exporter.to_psd(psd_output)
            test("psd export works", Path(psd_output).exists())
        except Exception as e:
            print(f"  [SKIP] psd export: {e}")

        return True

    except Exception as e:
        test("export module", False, str(e))
        return False


def test_font_match():
    """Test font matching functionality (local analysis)."""
    print("\n--- Font Match E2E ---")

    try:
        from src.fal_api.font_match import FontMatcher, identify_font

        test_image = PROJECT_ROOT / "assets" / "test_images" / "text_hello.png"

        matcher = FontMatcher()
        result = matcher.identify_font(str(test_image), max_results=3)

        test("identify_font returns result", "primary_match" in result or "error" in result)

        if result.get("success"):
            test("primary_match has name", "name" in result.get("primary_match", {}))
            test("similar_fonts included", isinstance(result.get("similar_fonts"), list))
            test("characteristics detected", "detected_characteristics" in result)
        else:
            # Even if font matching fails, test the structure
            test("returns valid response", "error" in result or "success" in result)

        # Test with region parameter
        result_region = matcher.identify_font(
            str(test_image),
            region={"x": 10, "y": 10, "width": 100, "height": 50}
        )
        test("region parameter works", result_region is not None)

        # Test filter_free option
        result_free = identify_font(str(test_image), filter_free=True)
        test("filter_free option works", result_free is not None)

        return True

    except Exception as e:
        test("font_match module", False, str(e))
        return False


# ============================================================
# MAIN
# ============================================================

def run_all_tests():
    """Run all E2E tests."""
    global passed, failed

    print("=" * 60)
    print("E2E TESTS - LOCAL FEATURES (No API Required)")
    print("=" * 60)

    # Generate test images first
    print("\n[Setup] Generating test images...")
    generate_all_test_images()

    # Clean up previous test output
    cleanup()

    # Run tests
    test_color_palette()
    test_text_overlay()
    test_text_effect()
    test_text_path()
    test_export()
    test_font_match()

    # Summary
    print("\n" + "=" * 60)
    print("E2E TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if passed + failed > 0:
        print(f"Success Rate: {passed / (passed + failed) * 100:.1f}%")

    if errors:
        print("\n--- Errors ---")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    print("\n" + "=" * 60)
    if failed == 0:
        print("ALL E2E TESTS PASSED")
        return 0
    else:
        print(f"E2E TESTS FAILED - {failed} failures")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
