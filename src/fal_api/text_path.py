"""
Text to Path Module - Arrange text along curved paths.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class TextPath:
    """Arrange text along curved paths."""

    PATH_TYPES = ["circle", "arc", "wave", "spiral", "bezier"]

    def __init__(self):
        pass

    def render_text_on_path(
        self,
        text: str,
        path_type: str = "circle",
        radius: int = 200,
        start_angle: float = 0,
        end_angle: float = 360,
        direction: str = "clockwise",
        font: str = "Arial",
        font_size: int = 36,
        color: str = "#000000",
        output_size: dict = None,
        output_path: str = None
    ) -> dict:
        """
        Render text along a path.

        Args:
            text: Text to render
            path_type: circle, arc, wave, spiral
            radius: Radius for circular paths
            start_angle: Starting angle in degrees
            end_angle: Ending angle in degrees
            direction: clockwise or counterclockwise
            font: Font family
            font_size: Font size
            color: Text color
            output_size: {width, height}
            output_path: Output file path

        Returns:
            dict with result info
        """
        if not text:
            return {
                "success": False,
                "error": "Text content is required"
            }

        if path_type not in self.PATH_TYPES:
            path_type = "circle"

        try:
            # Calculate image size
            if output_size:
                width = output_size.get("width", radius * 2 + 100)
                height = output_size.get("height", radius * 2 + 100)
            else:
                width = radius * 2 + 100
                height = radius * 2 + 100

            # Create image
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            # Load font
            try:
                pil_font = ImageFont.truetype(font, font_size)
            except OSError:
                pil_font = ImageFont.load_default()

            # Parse color
            text_color = self._parse_color(color)

            # Render based on path type
            if path_type == "circle":
                img = self._render_circle(
                    img, text, radius, start_angle, end_angle,
                    direction, pil_font, text_color
                )
            elif path_type == "arc":
                img = self._render_arc(
                    img, text, radius, start_angle, end_angle,
                    direction, pil_font, text_color
                )
            elif path_type == "wave":
                img = self._render_wave(
                    img, text, radius, pil_font, text_color
                )
            elif path_type == "spiral":
                img = self._render_spiral(
                    img, text, radius, pil_font, text_color
                )
            else:
                img = self._render_circle(
                    img, text, radius, start_angle, end_angle,
                    direction, pil_font, text_color
                )

            # Save result
            if not output_path:
                safe_text = "".join(c if c.isalnum() else "_" for c in text[:10])
                output_path = f"./output/text_path_{safe_text}.png"

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path)

            return {
                "success": True,
                "output_path": output_path,
                "dimensions": {"width": width, "height": height},
                "path_used": path_type,
                "text_length": len(text)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_color(self, color: str) -> tuple:
        """Parse hex color to RGBA."""
        color = color.lstrip("#")
        if len(color) == 6:
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            return (*rgb, 255)
        return (0, 0, 0, 255)

    def _render_circle(self, img, text, radius, start_angle, end_angle, direction, font, color):
        """Render text in a circle."""
        draw = ImageDraw.Draw(img)
        cx, cy = img.width // 2, img.height // 2

        # Calculate angle per character
        angle_range = end_angle - start_angle
        if len(text) > 1:
            angle_step = angle_range / (len(text) - 1)
        else:
            angle_step = 0

        for i, char in enumerate(text):
            if direction == "counterclockwise":
                angle = math.radians(start_angle + i * angle_step)
            else:
                angle = math.radians(start_angle - i * angle_step)

            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)

            # Create rotated character
            char_img = self._render_rotated_char(char, font, color, -math.degrees(angle) + 90)

            # Paste character
            paste_x = int(x - char_img.width // 2)
            paste_y = int(y - char_img.height // 2)
            img.paste(char_img, (paste_x, paste_y), char_img)

        return img

    def _render_arc(self, img, text, radius, start_angle, end_angle, direction, font, color):
        """Render text along an arc."""
        return self._render_circle(img, text, radius, start_angle, end_angle, direction, font, color)

    def _render_wave(self, img, text, amplitude, font, color):
        """Render text in a wave pattern."""
        draw = ImageDraw.Draw(img)
        cx, cy = img.width // 2, img.height // 2

        # Calculate text width
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        char_width = text_width / len(text) if text else 20

        start_x = cx - text_width // 2

        for i, char in enumerate(text):
            x = start_x + i * char_width
            y = cy + amplitude * math.sin(i * 0.5)
            draw.text((x, y), char, font=font, fill=color)

        return img

    def _render_spiral(self, img, text, start_radius, font, color):
        """Render text in a spiral."""
        draw = ImageDraw.Draw(img)
        cx, cy = img.width // 2, img.height // 2

        for i, char in enumerate(text):
            angle = math.radians(i * 30)
            radius = start_radius + i * 5
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            draw.text((x, y), char, font=font, fill=color)

        return img

    def _render_rotated_char(self, char, font, color, angle):
        """Render a single rotated character."""
        # Create temporary image for character
        temp = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp)
        draw.text((30, 30), char, font=font, fill=color)

        # Rotate
        rotated = temp.rotate(angle, expand=True, resample=Image.BICUBIC)
        return rotated


def render_text_on_path(
    text: str,
    path_type: str = "circle",
    radius: int = 200,
    start_angle: float = 0,
    end_angle: float = 360,
    font: str = "Arial",
    font_size: int = 36,
    color: str = "#000000",
    output_path: str = None,
    **kwargs
) -> dict:
    """Convenience function for rendering text on path."""
    tp = TextPath()
    return tp.render_text_on_path(
        text, path_type, radius, start_angle, end_angle,
        font=font, font_size=font_size, color=color,
        output_path=output_path, **kwargs
    )


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        result = render_text_on_path(sys.argv[1], path_type="circle")
        print(json.dumps(result, indent=2))
