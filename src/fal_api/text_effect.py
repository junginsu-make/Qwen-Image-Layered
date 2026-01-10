"""
Text Effect Module - Apply visual effects to text.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class TextEffect:
    """Apply visual effects to text."""

    EFFECTS = ["shadow", "glow", "neon", "outline", "gradient", "3d", "emboss", "blur"]

    def __init__(self):
        pass

    def apply_effect(
        self,
        image_path: str = None,
        text: str = None,
        effect: str = "shadow",
        color: str = "#FFFFFF",
        effect_color: str = "#000000",
        intensity: float = 0.8,
        blur: int = 5,
        offset_x: int = 3,
        offset_y: int = 3,
        font_size: int = 72,
        output_path: str = None
    ) -> dict:
        """
        Apply visual effect to text.

        Args:
            image_path: Base image path (optional)
            text: Text to render with effect
            effect: Effect type
            color: Main text color
            effect_color: Effect color (shadow, glow, etc.)
            intensity: Effect strength 0.0-1.0
            blur: Blur radius for soft effects
            offset_x, offset_y: Offset for shadows
            font_size: Font size
            output_path: Output file path

        Returns:
            dict with result info
        """
        if effect not in self.EFFECTS:
            return {
                "success": False,
                "error": f"Unknown effect. Available: {self.EFFECTS}"
            }

        try:
            # Create or load base image
            if image_path:
                img = Image.open(image_path).convert("RGBA")
            elif text:
                # Create new image for text
                img = Image.new("RGBA", (800, 200), (0, 0, 0, 0))
            else:
                return {
                    "success": False,
                    "error": "Either image_path or text must be provided"
                }

            if text:
                # Apply the selected effect
                if effect == "shadow":
                    img = self._apply_shadow(
                        img, text, color, effect_color, blur, offset_x, offset_y, font_size
                    )
                elif effect == "glow":
                    img = self._apply_glow(img, text, color, effect_color, blur, font_size)
                elif effect == "neon":
                    img = self._apply_neon(img, text, color, blur, font_size)
                elif effect == "outline":
                    img = self._apply_outline(img, text, color, effect_color, font_size)
                elif effect == "3d":
                    img = self._apply_3d(img, text, color, effect_color, font_size)
                else:
                    img = self._apply_shadow(
                        img, text, color, effect_color, blur, offset_x, offset_y, font_size
                    )

            # Save result
            if not output_path:
                if image_path:
                    path = Path(image_path)
                    output_path = str(path.parent / f"{path.stem}_{effect}{path.suffix}")
                else:
                    output_path = f"./output/text_{effect}.png"

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path)

            return {
                "success": True,
                "output_path": output_path,
                "effect_applied": effect,
                "effect_params": {
                    "color": color,
                    "effect_color": effect_color,
                    "intensity": intensity,
                    "blur": blur
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_font(self, size: int):
        """Get a font, fallback to default if needed."""
        try:
            return ImageFont.truetype("Arial", size)
        except OSError:
            return ImageFont.load_default()

    def _parse_color(self, color: str) -> tuple:
        """Parse hex color to RGBA."""
        color = color.lstrip("#")
        if len(color) == 6:
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            return (*rgb, 255)
        return (255, 255, 255, 255)

    def _apply_shadow(self, img, text, color, shadow_color, blur, ox, oy, font_size):
        """Apply drop shadow effect."""
        font = self._get_font(font_size)
        text_color = self._parse_color(color)
        shadow_rgba = self._parse_color(shadow_color)

        # Create shadow layer
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (img.width - (bbox[2] - bbox[0])) // 2
        y = (img.height - (bbox[3] - bbox[1])) // 2

        draw.text((x + ox, y + oy), text, font=font, fill=shadow_rgba)
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))

        # Draw main text
        draw = ImageDraw.Draw(shadow)
        draw.text((x, y), text, font=font, fill=text_color)

        return Image.alpha_composite(img, shadow)

    def _apply_glow(self, img, text, color, glow_color, blur, font_size):
        """Apply glow effect."""
        font = self._get_font(font_size)
        text_color = self._parse_color(color)
        glow_rgba = self._parse_color(glow_color)

        # Create glow layer
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)

        bbox = draw.textbbox((0, 0), text, font=font)
        x = (img.width - (bbox[2] - bbox[0])) // 2
        y = (img.height - (bbox[3] - bbox[1])) // 2

        # Draw glow (multiple passes)
        for i in range(3):
            draw.text((x, y), text, font=font, fill=glow_rgba)

        glow = glow.filter(ImageFilter.GaussianBlur(blur * 2))

        # Draw main text
        draw = ImageDraw.Draw(glow)
        draw.text((x, y), text, font=font, fill=text_color)

        return Image.alpha_composite(img, glow)

    def _apply_neon(self, img, text, color, blur, font_size):
        """Apply neon glow effect."""
        # Neon uses bright glow with the same color
        glow_color = color
        return self._apply_glow(img, text, color, glow_color, blur * 2, font_size)

    def _apply_outline(self, img, text, color, outline_color, font_size):
        """Apply outline/stroke effect."""
        font = self._get_font(font_size)
        text_color = self._parse_color(color)
        outline_rgba = self._parse_color(outline_color)

        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        bbox = draw.textbbox((0, 0), text, font=font)
        x = (img.width - (bbox[2] - bbox[0])) // 2
        y = (img.height - (bbox[3] - bbox[1])) // 2

        # Draw outline
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                draw.text((x + dx, y + dy), text, font=font, fill=outline_rgba)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

        return Image.alpha_composite(img, layer)

    def _apply_3d(self, img, text, color, depth_color, font_size):
        """Apply 3D extrusion effect."""
        font = self._get_font(font_size)
        text_color = self._parse_color(color)
        depth_rgba = self._parse_color(depth_color)

        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        bbox = draw.textbbox((0, 0), text, font=font)
        x = (img.width - (bbox[2] - bbox[0])) // 2
        y = (img.height - (bbox[3] - bbox[1])) // 2

        # Draw depth layers
        for i in range(10, 0, -1):
            draw.text((x + i, y + i), text, font=font, fill=depth_rgba)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

        return Image.alpha_composite(img, layer)


def apply_text_effect(
    image_path: str = None,
    text: str = None,
    effect: str = "shadow",
    color: str = "#FFFFFF",
    intensity: float = 0.8,
    blur: int = 5,
    output_path: str = None,
    **kwargs
) -> dict:
    """Convenience function for applying text effects."""
    te = TextEffect()
    return te.apply_effect(
        image_path, text, effect, color,
        intensity=intensity, blur=blur,
        output_path=output_path, **kwargs
    )


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 2:
        result = apply_text_effect(text=sys.argv[1], effect=sys.argv[2])
        print(json.dumps(result, indent=2))
