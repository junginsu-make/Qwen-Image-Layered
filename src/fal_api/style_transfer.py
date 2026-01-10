"""
Style Transfer Module - Apply artistic styles to images using Fal AI.
"""

import os
from pathlib import Path
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    fal_client = None
    FAL_AVAILABLE = False


class StyleTransfer:
    """Apply artistic styles to images."""

    STYLES = {
        "watercolor": "a watercolor painting style",
        "oil_painting": "an oil painting style with rich textures",
        "sketch": "a pencil sketch drawing style",
        "cartoon": "a cartoon style with bold outlines",
        "anime": "a Japanese anime style",
        "impressionist": "an impressionist painting like Monet",
        "pop_art": "a pop art style like Andy Warhol",
        "pixel_art": "a retro pixel art style"
    }

    MODEL_ID = "fal-ai/flux/dev"

    def __init__(self):
        """Initialize style transfer."""
        self.api_key = os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY environment variable not set")

    def apply_style(
        self,
        image_path: str,
        style: str,
        intensity: float = 0.8,
        preserve_colors: bool = False,
        output_path: str = None
    ) -> dict:
        """
        Apply artistic style to an image.

        Args:
            image_path: Path to input image
            style: Style name from STYLES
            intensity: Style strength 0.0-1.0
            preserve_colors: Keep original colors
            output_path: Output file path

        Returns:
            dict with styled image info
        """
        # Validate style
        if style not in self.STYLES:
            return {
                "success": False,
                "error": f"Unknown style. Available: {list(self.STYLES.keys())}"
            }

        # Clamp intensity
        intensity = max(0.0, min(1.0, intensity))

        # Prepare output path
        if not output_path:
            path = Path(image_path)
            output_path = str(path.parent / f"{path.stem}_{style}{path.suffix}")

        try:
            # Build prompt
            style_prompt = self.STYLES[style]
            prompt = f"Transform this image into {style_prompt}, style strength {intensity}"

            if preserve_colors:
                prompt += ", preserve original colors"

            # Upload image
            image_url = fal_client.upload_file(image_path)

            # Call Fal AI for style transfer
            result = fal_client.subscribe(
                self.MODEL_ID,
                arguments={
                    "prompt": prompt,
                    "image_url": image_url,
                    "strength": intensity,
                    "num_inference_steps": 28
                }
            )

            # Save result
            if "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                self._download_image(image_url, output_path)

            # Preserve alpha channel if input has it
            self._preserve_alpha(image_path, output_path)

            return {
                "success": True,
                "styled_path": output_path,
                "style_applied": style,
                "intensity_used": intensity,
                "preserved_alpha": self._has_alpha(image_path)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _download_image(self, url: str, output_path: str):
        """Download image from URL."""
        import requests
        response = requests.get(url)
        with open(output_path, "wb") as f:
            f.write(response.content)

    def _has_alpha(self, image_path: str) -> bool:
        """Check if image has alpha channel."""
        with Image.open(image_path) as img:
            return img.mode == "RGBA"

    def _preserve_alpha(self, original_path: str, styled_path: str):
        """Preserve alpha channel from original to styled image."""
        with Image.open(original_path) as original:
            if original.mode != "RGBA":
                return

            with Image.open(styled_path) as styled:
                styled_rgba = styled.convert("RGBA")
                # Copy alpha channel
                r, g, b, _ = styled_rgba.split()
                _, _, _, a = original.split()
                result = Image.merge("RGBA", (r, g, b, a))
                result.save(styled_path)

    @classmethod
    def list_styles(cls) -> list:
        """Return list of available styles."""
        return list(cls.STYLES.keys())


def apply_style(
    image_path: str,
    style: str,
    intensity: float = 0.8,
    preserve_colors: bool = False,
    output_path: str = None
) -> dict:
    """
    Convenience function for style transfer.
    """
    transfer = StyleTransfer()
    return transfer.apply_style(image_path, style, intensity, preserve_colors, output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        result = apply_style(sys.argv[1], sys.argv[2])
        print(result)
    else:
        print(f"Available styles: {StyleTransfer.list_styles()}")
