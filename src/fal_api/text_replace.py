"""
Text Replace Module - Replace text in images while preserving style.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class TextReplacer:
    """Replace text in images while preserving style."""

    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")

    def replace_text(
        self,
        image_path: str,
        old_text: str,
        new_text: str,
        match_style: bool = True,
        match_color: bool = True,
        font_override: str = None,
        color_override: str = None,
        output_path: str = None
    ) -> dict:
        """
        Replace text in an image.

        Args:
            image_path: Path to input image
            old_text: Original text to find
            new_text: Replacement text
            match_style: Match original font style
            match_color: Match original text color
            font_override: Force specific font
            color_override: Force specific color
            output_path: Output file path

        Returns:
            dict with result info
        """
        if not old_text:
            return {
                "success": False,
                "error": "old_text is required"
            }

        try:
            # Step 1: Find text regions matching old_text
            from .text_ocr import extract_text
            ocr_result = extract_text(image_path, output_format="structured")

            if not ocr_result.get("success"):
                return ocr_result

            # Find matching regions
            matching_regions = self._find_matching_regions(
                ocr_result.get("blocks", []), old_text
            )

            if not matching_regions:
                return {
                    "success": False,
                    "output_path": image_path,
                    "replacements_made": 0,
                    "message": f"Text '{old_text}' not found in image"
                }

            # Prepare output path
            if not output_path:
                path = Path(image_path)
                output_path = str(path.parent / f"{path.stem}_replaced{path.suffix}")

            # Step 2: Analyze original style
            original_style = self._analyze_style(image_path, matching_regions[0])

            # Step 3: Remove old text
            from .text_remove import remove_text
            temp_path = str(Path(output_path).parent / "temp_removed.png")

            # Create mask for matched regions
            remove_result = self._remove_regions(image_path, matching_regions, temp_path)

            # Step 4: Add new text with matched style
            final_result = self._add_replacement_text(
                temp_path if Path(temp_path).exists() else image_path,
                new_text,
                matching_regions,
                original_style,
                match_style,
                match_color,
                font_override,
                color_override,
                output_path
            )

            # Cleanup temp file
            if Path(temp_path).exists():
                Path(temp_path).unlink()

            return {
                "success": True,
                "output_path": output_path,
                "replacements_made": len(matching_regions),
                "original_style": original_style,
                "matched_regions": [r.get("bbox") for r in matching_regions]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _find_matching_regions(self, blocks: list, target_text: str) -> list:
        """Find text blocks matching target text."""
        matching = []
        target_lower = target_text.lower()

        for block in blocks:
            block_text = block.get("text", "").lower()
            if target_lower in block_text or block_text in target_lower:
                matching.append(block)

        return matching

    def _analyze_style(self, image_path: str, region: dict) -> dict:
        """Analyze text style in a region."""
        try:
            from .color_palette import extract_palette

            bbox = region.get("bbox", {})
            with Image.open(image_path) as img:
                # Crop region
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                w = bbox.get("width", 100)
                h = bbox.get("height", 50)

                cropped = img.crop((x, y, x + w, y + h))

                # Save temp and analyze colors
                temp_path = "/tmp/style_region.png"
                cropped.save(temp_path)

                palette_result = extract_palette(temp_path, num_colors=2)
                colors = palette_result.get("colors", [])

                dominant_color = colors[0]["value"] if colors else "#000000"

            return {
                "color": dominant_color,
                "font_size": max(12, h - 4),  # Estimate from height
                "font": "Arial"
            }

        except Exception:
            return {
                "color": "#000000",
                "font_size": 24,
                "font": "Arial"
            }

    def _remove_regions(self, image_path: str, regions: list, output_path: str):
        """Remove text regions from image."""
        try:
            import cv2
            import numpy as np

            img = cv2.imread(image_path)
            mask = np.zeros(img.shape[:2], dtype=np.uint8)

            for region in regions:
                bbox = region.get("bbox", {})
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                w = bbox.get("width", 0)
                h = bbox.get("height", 0)
                # Add padding
                cv2.rectangle(mask, (x-2, y-2), (x + w + 2, y + h + 2), 255, -1)

            result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            cv2.imwrite(output_path, result)
            return True

        except ImportError:
            import shutil
            shutil.copy(image_path, output_path)
            return False

    def _add_replacement_text(
        self,
        image_path: str,
        new_text: str,
        regions: list,
        original_style: dict,
        match_style: bool,
        match_color: bool,
        font_override: str,
        color_override: str,
        output_path: str
    ):
        """Add replacement text at region locations."""
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            draw = ImageDraw.Draw(img)

            # Determine style
            font_name = font_override if font_override else original_style.get("font", "Arial")
            font_size = original_style.get("font_size", 24) if match_style else 24
            color = color_override if color_override else (
                original_style.get("color", "#000000") if match_color else "#000000"
            )

            # Parse color
            color_tuple = self._parse_color(color)

            # Load font
            try:
                font = ImageFont.truetype(font_name, font_size)
            except OSError:
                font = ImageFont.load_default()

            # Draw new text at each region
            for region in regions:
                bbox = region.get("bbox", {})
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                draw.text((x, y), new_text, font=font, fill=color_tuple)

            img.save(output_path)

    def _parse_color(self, color: str) -> tuple:
        """Parse hex color to RGBA."""
        color = color.lstrip("#")
        if len(color) == 6:
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            return (*rgb, 255)
        return (0, 0, 0, 255)


def replace_text(
    image_path: str,
    old_text: str,
    new_text: str,
    match_style: bool = True,
    match_color: bool = True,
    font_override: str = None,
    color_override: str = None,
    output_path: str = None
) -> dict:
    """Convenience function for text replacement."""
    replacer = TextReplacer()
    return replacer.replace_text(
        image_path, old_text, new_text,
        match_style, match_color,
        font_override, color_override, output_path
    )


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 3:
        result = replace_text(sys.argv[1], sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
