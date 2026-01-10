#!/usr/bin/env python3
"""
빠른 API 테스트 - 핵심 기능만 테스트

사용법:
    pip install fal-client Pillow python-dotenv requests
    python scripts/quick_test.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    print("❌ FAL_KEY not set!")
    print("   Create .env file with: FAL_KEY=your-key")
    sys.exit(1)

print("🔑 API Key loaded")

# Test 1: fal_client
print("\n📦 Testing fal_client...")
try:
    import fal_client
    print("   ✅ fal_client imported")
except ImportError:
    print("   ❌ fal_client not installed")
    print("   Run: pip install fal-client")
    sys.exit(1)

# Test 2: Simple image generation
print("\n🎨 Testing image generation...")
try:
    result = fal_client.subscribe(
        "fal-ai/fast-sdxl",
        arguments={
            "prompt": "a cute cat, digital art",
            "image_size": "square",
            "num_images": 1,
        }
    )

    if result and "images" in result:
        url = result["images"][0]["url"]
        print(f"   ✅ Generated: {url[:60]}...")

        # Save image
        import requests
        output_dir = PROJECT_ROOT / "output"
        output_dir.mkdir(exist_ok=True)

        img_data = requests.get(url).content
        img_path = output_dir / "quick_test_result.png"
        with open(img_path, 'wb') as f:
            f.write(img_data)
        print(f"   ✅ Saved: {img_path}")
    else:
        print(f"   ❌ Unexpected result: {result}")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Background removal
print("\n✂️ Testing background removal...")
try:
    from PIL import Image

    # Create test image
    test_img = Image.new('RGBA', (256, 256), (100, 150, 200, 255))
    test_path = PROJECT_ROOT / "output" / "test_input.png"
    test_img.save(test_path)

    # Upload
    uploaded_url = fal_client.upload_file(str(test_path))
    print(f"   ✅ Uploaded: {uploaded_url[:50]}...")

    # Remove background
    result = fal_client.subscribe(
        "fal-ai/imageutils/rembg",
        arguments={"image_url": uploaded_url}
    )

    if result and "image" in result:
        print(f"   ✅ Background removed successfully")
    else:
        print(f"   ⚠️ Result: {result}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 40)
print("✅ 테스트 완료!")
print(f"📁 결과 위치: {PROJECT_ROOT / 'output'}")
print("=" * 40)
