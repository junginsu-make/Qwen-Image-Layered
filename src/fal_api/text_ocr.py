"""
Text OCR Module - Extract text from images using OCR.
"""

import os
from pathlib import Path
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class TextExtractor:
    """Extract text from images using OCR."""

    SUPPORTED_LANGUAGES = ["auto", "en", "ko", "ja", "zh", "es", "fr", "de"]

    def __init__(self):
        """Initialize the text extractor."""
        pass

    def extract_text(
        self,
        image_path: str,
        language: str = "auto",
        output_format: str = "text",
        confidence_threshold: float = 0.5
    ) -> dict:
        """
        Extract text from an image.

        Args:
            image_path: Path to input image
            language: Language code (auto, en, ko, ja, zh, etc.)
            output_format: text, json, or structured
            confidence_threshold: Minimum confidence 0.0-1.0

        Returns:
            dict with extracted text info
        """
        # Validate inputs
        if language not in self.SUPPORTED_LANGUAGES:
            language = "auto"

        confidence_threshold = max(0.0, min(1.0, confidence_threshold))

        try:
            # Try using pytesseract if available
            try:
                import pytesseract
                return self._extract_with_tesseract(
                    image_path, language, output_format, confidence_threshold
                )
            except ImportError:
                pass

            # Fallback: Use Fal AI OCR if available
            try:
                import fal_client
                return self._extract_with_fal(
                    image_path, language, output_format, confidence_threshold
                )
            except Exception:
                pass

            # Last resort: Return placeholder
            return {
                "success": False,
                "error": "OCR engine not available. Install pytesseract or configure FAL_KEY."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _extract_with_tesseract(
        self,
        image_path: str,
        language: str,
        output_format: str,
        confidence_threshold: float
    ) -> dict:
        """Extract text using Tesseract OCR."""
        import pytesseract
        from PIL import Image

        # Map language codes
        lang_map = {
            "auto": "eng",
            "en": "eng",
            "ko": "kor",
            "ja": "jpn",
            "zh": "chi_sim",
            "es": "spa",
            "fr": "fra",
            "de": "deu"
        }

        tesseract_lang = lang_map.get(language, "eng")

        with Image.open(image_path) as img:
            # Get detailed data
            data = pytesseract.image_to_data(
                img,
                lang=tesseract_lang,
                output_type=pytesseract.Output.DICT
            )

            # Process results
            blocks = []
            full_text = []

            for i in range(len(data["text"])):
                conf = float(data["conf"][i]) / 100.0
                text = data["text"][i].strip()

                if text and conf >= confidence_threshold:
                    blocks.append({
                        "text": text,
                        "confidence": round(conf, 2),
                        "bbox": {
                            "x": data["left"][i],
                            "y": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i]
                        }
                    })
                    full_text.append(text)

            extracted_text = " ".join(full_text)

            return {
                "success": True,
                "extracted_text": extracted_text,
                "blocks": blocks if output_format != "text" else None,
                "language_detected": language,
                "total_characters": len(extracted_text),
                "confidence_avg": sum(b["confidence"] for b in blocks) / len(blocks) if blocks else 0
            }

    def _extract_with_fal(
        self,
        image_path: str,
        language: str,
        output_format: str,
        confidence_threshold: float
    ) -> dict:
        """Extract text using Fal AI."""
        import fal_client

        # Upload image
        image_url = fal_client.upload_file(image_path)

        # Use vision model for OCR
        result = fal_client.subscribe(
            "fal-ai/llava-next",
            arguments={
                "image_url": image_url,
                "prompt": "Extract all text from this image. Return only the text content."
            }
        )

        extracted_text = result.get("output", "")

        return {
            "success": True,
            "extracted_text": extracted_text,
            "blocks": None,
            "language_detected": language,
            "total_characters": len(extracted_text),
            "method": "fal_ai"
        }


def extract_text(
    image_path: str,
    language: str = "auto",
    output_format: str = "text",
    confidence_threshold: float = 0.5
) -> dict:
    """
    Convenience function for text extraction.
    """
    extractor = TextExtractor()
    return extractor.extract_text(image_path, language, output_format, confidence_threshold)


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        result = extract_text(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
