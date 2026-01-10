"""
Text Remove Module - Remove text from images using AI inpainting.
"""

import os
from pathlib import Path
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class TextRemover:
    """Remove text from images using AI inpainting."""

    INPAINT_METHODS = ["ai", "telea", "ns"]

    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")

    def remove_text(
        self,
        image_path: str,
        mask_path: str = None,
        auto_detect: bool = True,
        inpaint_method: str = "ai",
        preserve_quality: bool = True,
        output_path: str = None
    ) -> dict:
        """
        Remove text from an image.

        Args:
            image_path: Path to input image
            mask_path: Custom mask for text areas
            auto_detect: Auto-detect text regions
            inpaint_method: ai, telea, or ns
            preserve_quality: Maintain image quality
            output_path: Output file path

        Returns:
            dict with result info
        """
        if inpaint_method not in self.INPAINT_METHODS:
            inpaint_method = "ai"

        try:
            # Detect text regions if auto_detect
            text_detected = []
            if auto_detect and not mask_path:
                text_detected = self._detect_text_regions(image_path)

            if not text_detected and not mask_path:
                return {
                    "success": True,
                    "output_path": image_path,
                    "regions_removed": 0,
                    "message": "No text detected in image"
                }

            # Prepare output path
            if not output_path:
                path = Path(image_path)
                output_path = str(path.parent / f"{path.stem}_no_text{path.suffix}")

            # Apply inpainting
            if inpaint_method == "ai":
                result = self._inpaint_with_ai(image_path, mask_path, text_detected, output_path)
            else:
                result = self._inpaint_with_opencv(image_path, mask_path, text_detected, inpaint_method, output_path)

            return {
                "success": True,
                "output_path": output_path,
                "regions_removed": len(text_detected),
                "text_detected": [t["text"] for t in text_detected] if text_detected else [],
                "inpaint_method_used": inpaint_method
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _detect_text_regions(self, image_path: str) -> list:
        """Detect text regions using OCR."""
        try:
            from .text_ocr import extract_text
            result = extract_text(image_path, output_format="structured")
            if result.get("success") and result.get("blocks"):
                return result["blocks"]
        except Exception:
            pass
        return []

    def _inpaint_with_ai(self, image_path: str, mask_path: str, text_regions: list, output_path: str):
        """Inpaint using Fal AI."""
        try:
            import fal_client

            # Upload image
            image_url = fal_client.upload_file(image_path)

            # Create or upload mask
            if mask_path:
                mask_url = fal_client.upload_file(mask_path)
            else:
                # Create mask from text regions
                mask_url = self._create_mask_url(image_path, text_regions)

            # Call inpainting API
            result = fal_client.subscribe(
                "fal-ai/inpaint",
                arguments={
                    "image_url": image_url,
                    "mask_url": mask_url,
                    "prompt": "clean background, seamless fill"
                }
            )

            # Download result
            if "image" in result:
                self._download_image(result["image"]["url"], output_path)
            else:
                # Fallback: copy original
                import shutil
                shutil.copy(image_path, output_path)

        except Exception:
            # Fallback to OpenCV
            self._inpaint_with_opencv(image_path, mask_path, text_regions, "telea", output_path)

    def _inpaint_with_opencv(self, image_path: str, mask_path: str, text_regions: list, method: str, output_path: str):
        """Inpaint using OpenCV."""
        try:
            import cv2
            import numpy as np

            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")

            # Create or load mask
            if mask_path:
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            else:
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                for region in text_regions:
                    bbox = region.get("bbox", {})
                    x = bbox.get("x", 0)
                    y = bbox.get("y", 0)
                    w = bbox.get("width", 0)
                    h = bbox.get("height", 0)
                    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

            # Apply inpainting
            if method == "telea":
                result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            else:  # ns
                result = cv2.inpaint(img, mask, 3, cv2.INPAINT_NS)

            cv2.imwrite(output_path, result)

        except ImportError:
            # If OpenCV not available, copy original
            import shutil
            shutil.copy(image_path, output_path)

    def _create_mask_url(self, image_path: str, text_regions: list) -> str:
        """Create mask image and upload."""
        import fal_client

        with Image.open(image_path) as img:
            mask = Image.new("L", img.size, 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)

            for region in text_regions:
                bbox = region.get("bbox", {})
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                w = bbox.get("width", 0)
                h = bbox.get("height", 0)
                draw.rectangle([x, y, x + w, y + h], fill=255)

            mask_path = "/tmp/text_mask.png"
            mask.save(mask_path)
            return fal_client.upload_file(mask_path)

    def _download_image(self, url: str, output_path: str):
        """Download image from URL."""
        import requests
        response = requests.get(url)
        with open(output_path, "wb") as f:
            f.write(response.content)


def remove_text(
    image_path: str,
    mask_path: str = None,
    auto_detect: bool = True,
    inpaint_method: str = "ai",
    preserve_quality: bool = True,
    output_path: str = None
) -> dict:
    """Convenience function for removing text."""
    remover = TextRemover()
    return remover.remove_text(
        image_path, mask_path, auto_detect,
        inpaint_method, preserve_quality, output_path
    )


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        result = remove_text(sys.argv[1])
        print(json.dumps(result, indent=2))
