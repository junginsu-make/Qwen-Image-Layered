#!/usr/bin/env python3
"""
실제 Fal AI API 테스트 스크립트
로컬 환경에서 실행하세요.

사용법:
    pip install fal-client Pillow python-pptx python-dotenv requests
    python scripts/real_api_test.py
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    print("[WARN] python-dotenv not installed, using environment variables directly")

# Check API key
FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    print("[ERROR] FAL_KEY not set. Create .env file with FAL_KEY=your-key")
    sys.exit(1)

print("=" * 60)
print("FAL AI 실제 API 테스트")
print("=" * 60)
print(f"API Key: {FAL_KEY[:20]}...")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)


def test_section(name):
    """Print test section header."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print("=" * 60)


def test_result(name, success, message=""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} - {name}")
    if message:
        print(f"         {message}")
    return success


# =============================================================================
# Test 1: Fal Client Import
# =============================================================================
test_section("1. Fal Client Import")

try:
    import fal_client
    test_result("fal_client import", True)
    FAL_AVAILABLE = True
except ImportError as e:
    test_result("fal_client import", False, str(e))
    print("\n[FIX] pip install fal-client")
    FAL_AVAILABLE = False


# =============================================================================
# Test 2: Pillow Import
# =============================================================================
test_section("2. Pillow Import")

try:
    from PIL import Image
    test_result("Pillow import", True)
    PIL_AVAILABLE = True
except ImportError as e:
    test_result("Pillow import", False, str(e))
    print("\n[FIX] pip install Pillow")
    PIL_AVAILABLE = False


# =============================================================================
# Test 3: Create Test Image
# =============================================================================
test_section("3. Create Test Image")

TEST_IMAGE_PATH = PROJECT_ROOT / "output" / "test_image.png"
TEST_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

if PIL_AVAILABLE:
    try:
        # Create a simple test image (gradient with shapes)
        img = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
        pixels = img.load()

        # Create gradient background
        for y in range(512):
            for x in range(512):
                r = int(255 * x / 512)
                g = int(255 * y / 512)
                b = 128
                pixels[x, y] = (r, g, b, 255)

        # Add a simple rectangle
        for y in range(150, 350):
            for x in range(150, 350):
                pixels[x, y] = (255, 100, 100, 255)

        img.save(TEST_IMAGE_PATH)
        test_result("Create test image", True, str(TEST_IMAGE_PATH))
    except Exception as e:
        test_result("Create test image", False, str(e))
else:
    test_result("Create test image", False, "Pillow not available")


# =============================================================================
# Test 4: Image Generation (Nano Banana)
# =============================================================================
test_section("4. Image Generation (text-to-image)")

GENERATED_IMAGE_PATH = PROJECT_ROOT / "output" / "generated_test.png"

if FAL_AVAILABLE:
    try:
        print("  Calling fal-ai/fast-sdxl (text-to-image)...")
        start_time = time.time()

        result = fal_client.subscribe(
            "fal-ai/fast-sdxl",
            arguments={
                "prompt": "a beautiful sunset over mountains, digital art",
                "image_size": "square",
                "num_images": 1,
            }
        )

        elapsed = time.time() - start_time

        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0]["url"]
            test_result("Image generation", True, f"Time: {elapsed:.1f}s")
            print(f"         URL: {image_url[:80]}...")

            # Download and save image
            import requests
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(GENERATED_IMAGE_PATH, 'wb') as f:
                    f.write(img_response.content)
                test_result("Save generated image", True, str(GENERATED_IMAGE_PATH))
        else:
            test_result("Image generation", False, f"No images in result: {result}")

    except Exception as e:
        test_result("Image generation", False, str(e))
else:
    test_result("Image generation", False, "fal_client not available")


# =============================================================================
# Test 5: Image Layer Decomposition
# =============================================================================
test_section("5. Image Layer Decomposition")

if FAL_AVAILABLE and TEST_IMAGE_PATH.exists():
    try:
        print("  Uploading test image...")
        uploaded_url = fal_client.upload_file(str(TEST_IMAGE_PATH))
        test_result("Upload image", True, uploaded_url[:60] + "...")

        print("  Calling layer decomposition API...")
        start_time = time.time()

        # Try the decomposition model
        result = fal_client.subscribe(
            "fal-ai/imageutils/rembg",  # Background removal as simpler test
            arguments={
                "image_url": uploaded_url,
            }
        )

        elapsed = time.time() - start_time

        if result and "image" in result:
            test_result("Background removal", True, f"Time: {elapsed:.1f}s")

            # Save result
            import requests
            img_url = result["image"]["url"]
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                output_path = PROJECT_ROOT / "output" / "bg_removed.png"
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                test_result("Save result", True, str(output_path))
        else:
            test_result("Background removal", False, f"Unexpected result: {result}")

    except Exception as e:
        test_result("Layer decomposition", False, str(e))
else:
    test_result("Layer decomposition", False, "Prerequisites not met")


# =============================================================================
# Test 6: Export Functions
# =============================================================================
test_section("6. Export Functions (PPTX)")

try:
    from python_pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    try:
        from pptx import Presentation
        PPTX_AVAILABLE = True
    except ImportError:
        PPTX_AVAILABLE = False

if PPTX_AVAILABLE and PIL_AVAILABLE:
    try:
        from pptx import Presentation
        from pptx.util import Inches

        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank slide

        # Add test image if exists
        if TEST_IMAGE_PATH.exists():
            slide.shapes.add_picture(str(TEST_IMAGE_PATH), Inches(1), Inches(1), Inches(4), Inches(4))

        pptx_path = PROJECT_ROOT / "output" / "test_export.pptx"
        prs.save(str(pptx_path))
        test_result("PPTX export", True, str(pptx_path))

    except Exception as e:
        test_result("PPTX export", False, str(e))
else:
    test_result("PPTX export", False, "python-pptx not installed")
    print("\n[FIX] pip install python-pptx")


# =============================================================================
# Test 7: Project Modules Import
# =============================================================================
test_section("7. Project Module Imports")

modules_to_test = [
    ("decompose", "src.fal_api.decompose"),
    ("export", "src.fal_api.export"),
    ("generation", "src.fal_api.generation"),
    ("model_registry", "src.fal_api.model_registry"),
    ("logging_config", "src.fal_api.logging_config"),
    ("cost_tracker", "src.fal_api.cost_tracker"),
    ("health_check", "src.fal_api.health_check"),
    ("llm_client", "src.fal_api.llm_client"),
    ("prompt_optimizer", "src.fal_api.prompt_optimizer"),
    ("intelligent_router", "src.fal_api.intelligent_router"),
]

for name, module_path in modules_to_test:
    try:
        __import__(module_path)
        test_result(f"Import {name}", True)
    except Exception as e:
        test_result(f"Import {name}", False, str(e)[:50])


# =============================================================================
# Test 8: Health Check System
# =============================================================================
test_section("8. Health Check System")

try:
    from src.fal_api.health_check import run_health_check, get_health_report

    results = run_health_check()
    test_result("Run health check", True)

    print("\n  Health Report:")
    for check, data in results.items():
        if check != "overall_status":
            status = data.get("status", "unknown")
            icon = "✅" if status == "ok" else "⚠️" if status == "warning" else "❌"
            print(f"    {icon} {check}: {status}")

    overall = results.get("overall_status", "unknown")
    test_result(f"Overall status: {overall}", overall in ["ok", "warning"])

except Exception as e:
    test_result("Health check", False, str(e))


# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
print(f"\nOutput directory: {PROJECT_ROOT / 'output'}")
print("\n생성된 파일들:")
for f in (PROJECT_ROOT / "output").glob("*"):
    print(f"  - {f.name}")
print("\n" + "=" * 60)
