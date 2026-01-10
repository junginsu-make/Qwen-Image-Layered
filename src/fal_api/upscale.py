"""
Smart Upscale Module - AI-powered image upscaling using Fal AI.
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


class ImageUpscaler:
    """AI-powered image upscaler using Fal AI."""

    # Fal AI upscaler models
    MODELS = {
        "standard": "fal-ai/real-esrgan",
        "creative": "fal-ai/clarity-upscaler",
        "ultra": "fal-ai/aura-sr"
    }

    def __init__(self):
        """Initialize the upscaler."""
        self.api_key = os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY environment variable not set")

    def upscale(
        self,
        image_path: str,
        scale_factor: int = 2,
        model: str = "standard",
        output_path: str = None
    ) -> dict:
        """
        Upscale an image using AI.

        Args:
            image_path: Path to input image
            scale_factor: 2 or 4 (default: 2)
            model: standard, creative, or ultra (default: standard)
            output_path: Output file path (optional)

        Returns:
            dict with upscaled image info
        """
        # Validate inputs
        if scale_factor not in [2, 4]:
            scale_factor = 2

        if model not in self.MODELS:
            model = "standard"

        # Get original dimensions
        with Image.open(image_path) as img:
            original_size = {"width": img.width, "height": img.height}

        # Prepare output path
        if not output_path:
            path = Path(image_path)
            output_path = str(path.parent / f"{path.stem}_upscaled_{scale_factor}x{path.suffix}")

        # Call Fal AI API
        model_id = self.MODELS[model]

        try:
            result = fal_client.subscribe(
                model_id,
                arguments={
                    "image_url": self._get_image_url(image_path),
                    "scale": scale_factor
                }
            )

            # Download and save result
            if "image" in result:
                image_url = result["image"]["url"]
                self._download_image(image_url, output_path)

            new_size = {
                "width": original_size["width"] * scale_factor,
                "height": original_size["height"] * scale_factor
            }

            return {
                "success": True,
                "upscaled_path": output_path,
                "original_size": original_size,
                "new_size": new_size,
                "scale_applied": scale_factor,
                "model_used": model
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_image_url(self, image_path: str) -> str:
        """Convert local image to URL or return if already URL."""
        if image_path.startswith(("http://", "https://")):
            return image_path

        # Upload to Fal storage
        url = fal_client.upload_file(image_path)
        return url

    def _download_image(self, url: str, output_path: str):
        """Download image from URL and save locally."""
        import requests
        response = requests.get(url)
        with open(output_path, "wb") as f:
            f.write(response.content)


def upscale_image(
    image_path: str,
    scale_factor: int = 2,
    model: str = "standard",
    output_path: str = None
) -> dict:
    """
    Convenience function for upscaling images.

    Args:
        image_path: Path to input image
        scale_factor: 2 or 4
        model: standard, creative, or ultra
        output_path: Output path (optional)

    Returns:
        dict with result info
    """
    upscaler = ImageUpscaler()
    return upscaler.upscale(image_path, scale_factor, model, output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = upscale_image(sys.argv[1], scale_factor=2)
        print(result)
