"""
Font Match Module - Identify fonts from images using AI.
"""

import os
from pathlib import Path
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Common font characteristics database
FONT_DATABASE = {
    "sans-serif": [
        {"name": "Arial", "weight": "Regular", "width": "Normal"},
        {"name": "Helvetica", "weight": "Regular", "width": "Normal"},
        {"name": "Roboto", "weight": "Regular", "width": "Normal"},
        {"name": "Open Sans", "weight": "Regular", "width": "Normal"},
        {"name": "Montserrat", "weight": "Regular", "width": "Normal"},
        {"name": "Lato", "weight": "Regular", "width": "Normal"},
        {"name": "Proxima Nova", "weight": "Regular", "width": "Normal"},
        {"name": "Gotham", "weight": "Regular", "width": "Normal"},
    ],
    "serif": [
        {"name": "Times New Roman", "weight": "Regular", "width": "Normal"},
        {"name": "Georgia", "weight": "Regular", "width": "Normal"},
        {"name": "Garamond", "weight": "Regular", "width": "Normal"},
        {"name": "Merriweather", "weight": "Regular", "width": "Normal"},
        {"name": "Playfair Display", "weight": "Regular", "width": "Normal"},
    ],
    "monospace": [
        {"name": "Courier New", "weight": "Regular", "width": "Normal"},
        {"name": "Monaco", "weight": "Regular", "width": "Normal"},
        {"name": "Consolas", "weight": "Regular", "width": "Normal"},
        {"name": "Fira Code", "weight": "Regular", "width": "Normal"},
    ],
    "display": [
        {"name": "Impact", "weight": "Bold", "width": "Condensed"},
        {"name": "Bebas Neue", "weight": "Bold", "width": "Condensed"},
        {"name": "Oswald", "weight": "Bold", "width": "Condensed"},
    ],
    "script": [
        {"name": "Brush Script", "weight": "Regular", "width": "Normal"},
        {"name": "Pacifico", "weight": "Regular", "width": "Normal"},
        {"name": "Dancing Script", "weight": "Regular", "width": "Normal"},
    ]
}


class FontMatcher:
    """Identify fonts from images."""

    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")

    def identify_font(
        self,
        image_path: str,
        region: dict = None,
        include_similar: bool = True,
        max_results: int = 5,
        filter_free: bool = False
    ) -> dict:
        """
        Identify fonts in an image.

        Args:
            image_path: Path to image with text
            region: Specific region {x, y, width, height}
            include_similar: Include similar alternatives
            max_results: Maximum fonts to return
            filter_free: Only show free fonts

        Returns:
            dict with font identification result
        """
        try:
            # Analyze image characteristics
            characteristics = self._analyze_characteristics(image_path, region)

            # Match fonts based on characteristics
            matches = self._match_fonts(characteristics, max_results, filter_free)

            if not matches:
                return {
                    "success": False,
                    "error": "Could not identify font. Try with clearer text."
                }

            primary_match = matches[0]
            similar_fonts = matches[1:] if include_similar else []

            return {
                "success": True,
                "primary_match": primary_match,
                "similar_fonts": similar_fonts,
                "detected_characteristics": characteristics
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_characteristics(self, image_path: str, region: dict = None) -> dict:
        """Analyze font characteristics from image."""
        try:
            with Image.open(image_path) as img:
                # Crop to region if specified
                if region:
                    x = region.get("x", 0)
                    y = region.get("y", 0)
                    w = region.get("width", img.width)
                    h = region.get("height", img.height)
                    img = img.crop((x, y, x + w, y + h))

                # Convert to grayscale for analysis
                if img.mode != "L":
                    gray = img.convert("L")
                else:
                    gray = img

                # Analyze contrast (serif detection heuristic)
                pixels = list(gray.getdata())
                avg_brightness = sum(pixels) / len(pixels)
                variance = sum((p - avg_brightness) ** 2 for p in pixels) / len(pixels)

                # Estimate characteristics
                has_serif = variance > 3000  # High variance may indicate serifs
                is_bold = avg_brightness < 128  # Darker = potentially bolder
                is_condensed = img.width < img.height * 0.5

                # Try AI analysis if available
                ai_result = self._analyze_with_ai(image_path)
                if ai_result:
                    return ai_result

                return {
                    "serif": has_serif,
                    "weight": "Bold" if is_bold else "Regular",
                    "width": "Condensed" if is_condensed else "Normal",
                    "style": "Normal"
                }

        except Exception:
            return {
                "serif": False,
                "weight": "Regular",
                "width": "Normal",
                "style": "Normal"
            }

    def _analyze_with_ai(self, image_path: str) -> dict:
        """Use AI to analyze font characteristics."""
        try:
            import fal_client

            image_url = fal_client.upload_file(image_path)

            result = fal_client.subscribe(
                "fal-ai/llava-next",
                arguments={
                    "image_url": image_url,
                    "prompt": """Analyze the font in this image. Respond with only these characteristics in JSON format:
{
  "serif": true or false,
  "weight": "Light", "Regular", "Medium", "Bold", or "Black",
  "width": "Condensed", "Normal", or "Extended",
  "style": "Normal", "Italic", or "Oblique"
}"""
                }
            )

            import json
            output = result.get("output", "{}")
            # Try to parse JSON from response
            try:
                # Find JSON in response
                start = output.find("{")
                end = output.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(output[start:end])
            except json.JSONDecodeError:
                pass

        except Exception:
            pass

        return None

    def _match_fonts(self, characteristics: dict, max_results: int, filter_free: bool) -> list:
        """Match fonts based on characteristics."""
        results = []

        # Determine font category
        is_serif = characteristics.get("serif", False)
        weight = characteristics.get("weight", "Regular")
        width = characteristics.get("width", "Normal")

        # Select font category
        if is_serif:
            category = "serif"
        else:
            category = "sans-serif"

        # Get fonts from database
        fonts = FONT_DATABASE.get(category, FONT_DATABASE["sans-serif"])

        # Free fonts (from Google Fonts, etc.)
        free_fonts = {
            "Roboto", "Open Sans", "Montserrat", "Lato",
            "Merriweather", "Playfair Display", "Oswald",
            "Fira Code", "Dancing Script", "Pacifico"
        }

        for font_info in fonts:
            if filter_free and font_info["name"] not in free_fonts:
                continue

            # Calculate confidence based on characteristic match
            confidence = 0.7  # Base confidence

            if font_info.get("weight", "Regular") == weight:
                confidence += 0.1
            if font_info.get("width", "Normal") == width:
                confidence += 0.1

            source = "Google Fonts" if font_info["name"] in free_fonts else "Adobe Fonts"

            results.append({
                "name": font_info["name"],
                "style": weight,
                "confidence": round(confidence, 2),
                "source": source
            })

        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)

        return results[:max_results]


def identify_font(
    image_path: str,
    region: dict = None,
    include_similar: bool = True,
    max_results: int = 5,
    filter_free: bool = False
) -> dict:
    """Convenience function for font identification."""
    matcher = FontMatcher()
    return matcher.identify_font(
        image_path, region, include_similar, max_results, filter_free
    )


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        result = identify_font(sys.argv[1])
        print(json.dumps(result, indent=2))
