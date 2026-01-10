"""
Text Overlay Module - Add text overlays to images.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class TextOverlay:
    """Add text overlays to images."""

    POSITIONS = {
        "center": (0.5, 0.5),
        "top": (0.5, 0.1),
        "bottom": (0.5, 0.9),
        "top-left": (0.1, 0.1),
        "top-right": (0.9, 0.1),
        "bottom-left": (0.1, 0.9),
        "bottom-right": (0.9, 0.9),
        "left": (0.1, 0.5),
        "right": (0.9, 0.5)
    }

    def __init__(self):
        pass

    def add_text(
        self,
        image_path: str,
        text: str,
        position: str = "center",
        x: int = None,
        y: int = None,
        font: str = "Arial",
        font_size: int = 48,
        color: str = "#FFFFFF",
        opacity: float = 1.0,
        stroke_color: str = None,
        stroke_width: int = 0,
        output_path: str = None
    ) -> dict:
        """
        Add text overlay to an image.

        Args:
            image_path: Path to input image
            text: Text content to add
            position: Preset position or custom x,y
            x, y: Custom position in pixels
            font: Font family name
            font_size: Font size in pixels
            color: Text color as hex
            opacity: Text opacity 0.0-1.0
            stroke_color: Outline color
            stroke_width: Outline width
            output_path: Output file path

        Returns:
            dict with result info
        """
        if not text:
            return {
                "success": False,
                "error": "Text content is required"
            }

        try:
            # Parse color
            text_color = self._parse_color(color)
            text_color = (*text_color, int(opacity * 255))

            # Load image
            with Image.open(image_path) as img:
                # Convert to RGBA for transparency support
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Create overlay
                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)

                # Load font
                try:
                    pil_font = ImageFont.truetype(font, font_size)
                except OSError:
                    pil_font = ImageFont.load_default()

                # Get text size
                bbox = draw.textbbox((0, 0), text, font=pil_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Calculate position
                if x is not None and y is not None:
                    pos_x, pos_y = x, y
                elif position in self.POSITIONS:
                    rel_x, rel_y = self.POSITIONS[position]
                    pos_x = int(img.width * rel_x - text_width / 2)
                    pos_y = int(img.height * rel_y - text_height / 2)
                else:
                    pos_x = (img.width - text_width) // 2
                    pos_y = (img.height - text_height) // 2

                # Draw stroke/outline if specified
                if stroke_color and stroke_width > 0:
                    stroke_rgb = self._parse_color(stroke_color)
                    stroke_rgba = (*stroke_rgb, int(opacity * 255))
                    for dx in range(-stroke_width, stroke_width + 1):
                        for dy in range(-stroke_width, stroke_width + 1):
                            if dx * dx + dy * dy <= stroke_width * stroke_width:
                                draw.text(
                                    (pos_x + dx, pos_y + dy),
                                    text,
                                    font=pil_font,
                                    fill=stroke_rgba
                                )

                # Draw main text
                draw.text((pos_x, pos_y), text, font=pil_font, fill=text_color)

                # Composite
                result = Image.alpha_composite(img, overlay)

                # Prepare output path
                if not output_path:
                    path = Path(image_path)
                    output_path = str(path.parent / f"{path.stem}_text{path.suffix}")

                result.save(output_path)

                return {
                    "success": True,
                    "output_path": output_path,
                    "text_bounds": {
                        "x": pos_x,
                        "y": pos_y,
                        "width": text_width,
                        "height": text_height
                    },
                    "applied_styles": {
                        "font": font,
                        "font_size": font_size,
                        "color": color,
                        "opacity": opacity
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_color(self, color: str) -> tuple:
        """Parse hex color to RGB tuple."""
        color = color.lstrip("#")
        if len(color) == 6:
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        return (255, 255, 255)


def add_text_overlay(
    image_path: str,
    text: str,
    position: str = "center",
    font: str = "Arial",
    font_size: int = 48,
    color: str = "#FFFFFF",
    opacity: float = 1.0,
    output_path: str = None,
    **kwargs
) -> dict:
    """
    Convenience function for adding text overlay.
    """
    overlay = TextOverlay()
    return overlay.add_text(
        image_path, text, position,
        font=font, font_size=font_size,
        color=color, opacity=opacity,
        output_path=output_path, **kwargs
    )


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 2:
        result = add_text_overlay(sys.argv[1], sys.argv[2])
        print(json.dumps(result, indent=2))
