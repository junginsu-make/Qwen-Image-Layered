"""
Color Palette Module - Extract and analyze color palettes from images.
"""

import colorsys
from pathlib import Path
from PIL import Image
from collections import Counter


# Color name mapping (approximate)
COLOR_NAMES = {
    (0, 0, 0): "Black",
    (255, 255, 255): "White",
    (255, 0, 0): "Red",
    (0, 255, 0): "Lime",
    (0, 0, 255): "Blue",
    (255, 255, 0): "Yellow",
    (0, 255, 255): "Cyan",
    (255, 0, 255): "Magenta",
    (128, 128, 128): "Gray",
    (128, 0, 0): "Maroon",
    (128, 128, 0): "Olive",
    (0, 128, 0): "Green",
    (128, 0, 128): "Purple",
    (0, 128, 128): "Teal",
    (0, 0, 128): "Navy",
    (255, 165, 0): "Orange",
    (255, 192, 203): "Pink",
    (165, 42, 42): "Brown",
    (245, 245, 220): "Beige",
    (64, 224, 208): "Turquoise"
}


class ColorPaletteExtractor:
    """Extract color palettes from images."""

    def __init__(self):
        pass

    def extract_palette(
        self,
        image_path: str,
        num_colors: int = 5,
        format: str = "hex",
        include_names: bool = True
    ) -> dict:
        """
        Extract dominant colors from an image.

        Args:
            image_path: Path to input image
            num_colors: Number of colors to extract (3-12)
            format: Output format (hex, rgb, hsl)
            include_names: Include color names

        Returns:
            dict with color palette info
        """
        # Validate num_colors
        num_colors = max(3, min(12, num_colors))

        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode == "RGBA":
                    # Ignore transparent pixels
                    img_rgb = Image.new("RGB", img.size, (255, 255, 255))
                    img_rgb.paste(img, mask=img.split()[3])
                    img = img_rgb
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize for faster processing
                img = img.resize((150, 150))

                # Get all pixels
                pixels = list(img.getdata())

                # Quantize colors
                colors = self._quantize_colors(pixels, num_colors)

                # Format results
                result_colors = []
                total_pixels = len(pixels)

                for color, count in colors:
                    r, g, b = color
                    percentage = (count / total_pixels) * 100

                    color_info = {
                        "value": self._format_color((r, g, b), format),
                        "percentage": round(percentage, 1)
                    }

                    if include_names:
                        color_info["name"] = self._get_color_name((r, g, b))

                    result_colors.append(color_info)

                # Determine palette type
                palette_type = self._analyze_palette_type(colors)
                harmony = self._analyze_harmony(colors)

                return {
                    "success": True,
                    "colors": result_colors,
                    "dominant_color": result_colors[0] if result_colors else None,
                    "palette_type": palette_type,
                    "harmony": harmony,
                    "total_colors": len(result_colors)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _quantize_colors(self, pixels: list, num_colors: int) -> list:
        """Quantize pixels to dominant colors."""
        # Simple quantization by rounding to nearest 32
        def quantize(c):
            return tuple((v // 32) * 32 for v in c)

        quantized = [quantize(p) for p in pixels]
        counter = Counter(quantized)
        return counter.most_common(num_colors)

    def _format_color(self, rgb: tuple, format: str) -> str:
        """Format color in requested format."""
        r, g, b = rgb

        if format == "hex":
            return f"#{r:02X}{g:02X}{b:02X}"
        elif format == "rgb":
            return f"rgb({r}, {g}, {b})"
        elif format == "hsl":
            h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
            return f"hsl({int(h*360)}, {int(s*100)}%, {int(l*100)}%)"
        else:
            return f"#{r:02X}{g:02X}{b:02X}"

    def _get_color_name(self, rgb: tuple) -> str:
        """Get approximate color name."""
        # Find nearest named color
        min_dist = float('inf')
        nearest_name = "Unknown"

        for named_rgb, name in COLOR_NAMES.items():
            dist = sum((a - b) ** 2 for a, b in zip(rgb, named_rgb))
            if dist < min_dist:
                min_dist = dist
                nearest_name = name

        return nearest_name

    def _analyze_palette_type(self, colors: list) -> str:
        """Analyze if palette is warm, cool, etc."""
        if not colors:
            return "unknown"

        warm_count = 0
        cool_count = 0

        for (r, g, b), _ in colors:
            if r > b:
                warm_count += 1
            else:
                cool_count += 1

        if warm_count > cool_count * 1.5:
            return "warm"
        elif cool_count > warm_count * 1.5:
            return "cool"
        else:
            return "neutral"

    def _analyze_harmony(self, colors: list) -> str:
        """Analyze color harmony type."""
        if len(colors) < 2:
            return "monochromatic"

        # Get hues
        hues = []
        for (r, g, b), _ in colors:
            h, _, _ = colorsys.rgb_to_hls(r/255, g/255, b/255)
            hues.append(h * 360)

        # Analyze hue relationships
        hue_diffs = []
        for i in range(len(hues) - 1):
            diff = abs(hues[i+1] - hues[i])
            if diff > 180:
                diff = 360 - diff
            hue_diffs.append(diff)

        avg_diff = sum(hue_diffs) / len(hue_diffs) if hue_diffs else 0

        if avg_diff < 30:
            return "analogous"
        elif 150 < avg_diff < 210:
            return "complementary"
        elif 90 < avg_diff < 150:
            return "triadic"
        else:
            return "mixed"


def extract_palette(
    image_path: str,
    num_colors: int = 5,
    format: str = "hex",
    include_names: bool = True
) -> dict:
    """
    Convenience function for extracting color palette.
    """
    extractor = ColorPaletteExtractor()
    return extractor.extract_palette(image_path, num_colors, format, include_names)


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        result = extract_palette(sys.argv[1], num_colors=6)
        print(json.dumps(result, indent=2))
