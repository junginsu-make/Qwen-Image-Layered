"""
Text to Layer Module - Generate RGBA layers from text descriptions using Fal AI.
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


class TextToLayerGenerator:
    """Generate image layers from text prompts."""

    MODEL_ID = "fal-ai/flux/schnell"

    def __init__(self):
        """Initialize the generator."""
        self.api_key = os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY environment variable not set")

    def generate_layer(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: str = "realistic",
        transparent_bg: bool = True,
        output_path: str = None
    ) -> dict:
        """
        Generate a new layer from text description.

        Args:
            prompt: Text description of desired content
            width: Layer width in pixels
            height: Layer height in pixels
            style: Generation style (realistic, artistic, flat)
            transparent_bg: Generate with transparent background
            output_path: Output file path

        Returns:
            dict with generated layer info
        """
        # Validate dimensions
        width = max(64, min(2048, width))
        height = max(64, min(2048, height))

        # Prepare output path
        if not output_path:
            safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:20])
            output_path = f"./output/generated_{safe_name}.png"

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            # Build enhanced prompt
            enhanced_prompt = self._build_prompt(prompt, style, transparent_bg)

            # Call Fal AI
            result = fal_client.subscribe(
                self.MODEL_ID,
                arguments={
                    "prompt": enhanced_prompt,
                    "image_size": {
                        "width": width,
                        "height": height
                    },
                    "num_inference_steps": 4,
                    "num_images": 1
                }
            )

            # Download and process result
            if "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                self._download_image(image_url, output_path)

                # Post-process for transparency if needed
                if transparent_bg:
                    self._add_transparency(output_path)

            # Get final dimensions
            with Image.open(output_path) as img:
                final_dims = {"width": img.width, "height": img.height}
                has_transparency = img.mode == "RGBA"

            return {
                "success": True,
                "layer_path": output_path,
                "dimensions": final_dims,
                "has_transparency": has_transparency,
                "prompt_used": enhanced_prompt
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _build_prompt(self, prompt: str, style: str, transparent_bg: bool) -> str:
        """Build enhanced prompt for generation."""
        style_additions = {
            "realistic": "photorealistic, high quality, detailed",
            "artistic": "artistic, creative, stylized",
            "flat": "flat design, minimalist, vector style"
        }

        enhanced = prompt

        if style in style_additions:
            enhanced += f", {style_additions[style]}"

        if transparent_bg:
            enhanced += ", on transparent background, PNG with alpha channel, isolated subject"

        return enhanced

    def _download_image(self, url: str, output_path: str):
        """Download image from URL."""
        import requests
        response = requests.get(url)
        with open(output_path, "wb") as f:
            f.write(response.content)

    def _add_transparency(self, image_path: str):
        """Add transparency to image by removing background."""
        try:
            with Image.open(image_path) as img:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Simple background removal based on edge colors
                data = img.getdata()
                new_data = []

                # Sample corner pixels for background color
                width, height = img.size
                corners = [
                    data[0],                    # top-left
                    data[width-1],              # top-right
                    data[(height-1)*width],     # bottom-left
                    data[-1]                    # bottom-right
                ]

                # Average background color
                bg_color = tuple(
                    sum(c[i] for c in corners) // 4
                    for i in range(3)
                )

                # Make similar colors transparent
                threshold = 30
                for pixel in data:
                    if all(abs(pixel[i] - bg_color[i]) < threshold for i in range(3)):
                        new_data.append((pixel[0], pixel[1], pixel[2], 0))
                    else:
                        new_data.append(pixel)

                img.putdata(new_data)
                img.save(image_path, "PNG")

        except Exception:
            pass  # Keep original if transparency fails


def generate_layer(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    style: str = "realistic",
    transparent_bg: bool = True,
    output_path: str = None
) -> dict:
    """
    Convenience function for generating layers from text.
    """
    generator = TextToLayerGenerator()
    return generator.generate_layer(prompt, width, height, style, transparent_bg, output_path)


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        result = generate_layer(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2))
