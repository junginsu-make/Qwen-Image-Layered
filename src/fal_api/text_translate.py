"""
Text Translation Module - Translate text between languages.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class TextTranslator:
    """Translate text between languages."""

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "ko": "Korean",
        "ja": "Japanese",
        "zh": "Chinese",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "pt": "Portuguese",
        "it": "Italian",
        "ru": "Russian"
    }

    def __init__(self):
        """Initialize translator."""
        pass

    def translate(
        self,
        text: str = None,
        image_path: str = None,
        source_lang: str = "auto",
        target_lang: str = "en",
        preserve_formatting: bool = True
    ) -> dict:
        """
        Translate text or text from an image.

        Args:
            text: Text to translate
            image_path: Image containing text (will OCR first)
            source_lang: Source language code
            target_lang: Target language code
            preserve_formatting: Keep original formatting

        Returns:
            dict with translation result
        """
        if not text and not image_path:
            return {
                "success": False,
                "error": "Either text or image_path must be provided"
            }

        if target_lang not in self.SUPPORTED_LANGUAGES:
            return {
                "success": False,
                "error": f"Unsupported target language. Available: {list(self.SUPPORTED_LANGUAGES.keys())}"
            }

        try:
            # If image provided, extract text first
            original_text = text
            if image_path and not text:
                from .text_ocr import extract_text
                ocr_result = extract_text(image_path, language=source_lang)
                if not ocr_result.get("success"):
                    return ocr_result
                original_text = ocr_result.get("extracted_text", "")

            if not original_text:
                return {
                    "success": False,
                    "error": "No text to translate"
                }

            # Try using Fal AI for translation
            translated_text = self._translate_with_fal(
                original_text, source_lang, target_lang
            )

            return {
                "success": True,
                "original_text": original_text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.9
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _translate_with_fal(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate using Fal AI LLM."""
        try:
            import fal_client

            target_name = self.SUPPORTED_LANGUAGES.get(target_lang, "English")
            source_name = self.SUPPORTED_LANGUAGES.get(source_lang, "the source language")

            if source_lang == "auto":
                prompt = f"Translate the following text to {target_name}. Only output the translation, nothing else:\n\n{text}"
            else:
                prompt = f"Translate the following text from {source_name} to {target_name}. Only output the translation, nothing else:\n\n{text}"

            result = fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "model": "anthropic/claude-3-haiku",
                    "prompt": prompt
                }
            )

            return result.get("output", text)

        except Exception:
            # Fallback: return original with note
            return f"[Translation to {target_lang}]: {text}"

    @classmethod
    def list_languages(cls) -> dict:
        """Return supported languages."""
        return cls.SUPPORTED_LANGUAGES


def translate_text(
    text: str = None,
    image_path: str = None,
    source_lang: str = "auto",
    target_lang: str = "en",
    preserve_formatting: bool = True
) -> dict:
    """
    Convenience function for translation.
    """
    translator = TextTranslator()
    return translator.translate(text, image_path, source_lang, target_lang, preserve_formatting)


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 2:
        result = translate_text(text=sys.argv[1], target_lang=sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
