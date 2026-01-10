#!/usr/bin/env python3
"""
Generate test images for E2E testing.
Creates various sample images without requiring external files.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - cannot generate test images")
    sys.exit(1)


OUTPUT_DIR = PROJECT_ROOT / "assets" / "test_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_solid_color_image(filename: str, color: tuple, size: tuple = (400, 300)):
    """Create a solid color image."""
    img = Image.new("RGB", size, color)
    path = OUTPUT_DIR / filename
    img.save(path)
    print(f"Created: {path}")
    return str(path)


def create_rgba_image(filename: str, size: tuple = (400, 300)):
    """Create an RGBA image with transparency."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a semi-transparent circle
    cx, cy = size[0] // 2, size[1] // 2
    radius = min(size) // 3
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(255, 100, 100, 200)
    )

    path = OUTPUT_DIR / filename
    img.save(path, "PNG")
    print(f"Created: {path}")
    return str(path)


def create_gradient_image(filename: str, size: tuple = (400, 300)):
    """Create a gradient image with multiple colors."""
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)

    for x in range(size[0]):
        r = int(255 * x / size[0])
        g = int(255 * (1 - x / size[0]))
        b = 128
        draw.line([(x, 0), (x, size[1])], fill=(r, g, b))

    path = OUTPUT_DIR / filename
    img.save(path)
    print(f"Created: {path}")
    return str(path)


def create_text_image(filename: str, text: str = "Hello World", size: tuple = (400, 200)):
    """Create an image with text for OCR testing."""
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to use a font, fallback to default
    try:
        font = ImageFont.truetype("Arial", 48)
    except OSError:
        font = ImageFont.load_default()

    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill=(0, 0, 0), font=font)

    path = OUTPUT_DIR / filename
    img.save(path)
    print(f"Created: {path}")
    return str(path)


def create_multi_color_image(filename: str, size: tuple = (400, 300)):
    """Create an image with multiple distinct colors for palette testing."""
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)

    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
    ]

    block_width = size[0] // 3
    block_height = size[1] // 2

    for i, color in enumerate(colors):
        x = (i % 3) * block_width
        y = (i // 3) * block_height
        draw.rectangle([x, y, x + block_width, y + block_height], fill=color)

    path = OUTPUT_DIR / filename
    img.save(path)
    print(f"Created: {path}")
    return str(path)


def create_layered_image(filename: str, size: tuple = (400, 300)):
    """Create an image that simulates multiple layers."""
    img = Image.new("RGBA", size, (200, 200, 200, 255))
    draw = ImageDraw.Draw(img)

    # Background pattern
    for i in range(0, size[0], 20):
        draw.line([(i, 0), (i, size[1])], fill=(180, 180, 180, 255), width=1)

    # Foreground shapes
    draw.ellipse([50, 50, 150, 150], fill=(255, 100, 100, 255))
    draw.rectangle([200, 100, 350, 200], fill=(100, 100, 255, 255))
    draw.polygon([(300, 50), (380, 150), (220, 150)], fill=(100, 255, 100, 255))

    path = OUTPUT_DIR / filename
    img.save(path, "PNG")
    print(f"Created: {path}")
    return str(path)


def generate_all_test_images():
    """Generate all test images."""
    print("=" * 60)
    print("GENERATING TEST IMAGES")
    print("=" * 60)

    images = {}

    # Basic images
    images["solid_red.png"] = create_solid_color_image("solid_red.png", (255, 0, 0))
    images["solid_blue.png"] = create_solid_color_image("solid_blue.png", (0, 0, 255))
    images["solid_white.png"] = create_solid_color_image("solid_white.png", (255, 255, 255))

    # RGBA with transparency
    images["transparent.png"] = create_rgba_image("transparent.png")

    # Gradient
    images["gradient.png"] = create_gradient_image("gradient.png")

    # Text images
    images["text_hello.png"] = create_text_image("text_hello.png", "Hello World")
    images["text_sample.png"] = create_text_image("text_sample.png", "Sample Text")

    # Multi-color for palette
    images["multi_color.png"] = create_multi_color_image("multi_color.png")

    # Layered image
    images["layered.png"] = create_layered_image("layered.png")

    print("\n" + "=" * 60)
    print(f"Generated {len(images)} test images in {OUTPUT_DIR}")
    print("=" * 60)

    return images


if __name__ == "__main__":
    generate_all_test_images()
