---
name: text-translate
description: Translate extracted text or text in images to different languages
---

# Triggers

Keywords:
- translate text
- translate image
- language translation
- convert language

Korean Keywords:
- 번역
- 텍스트 번역
- 이미지 번역
- 언어 변환

Patterns:
- "translate {image} to {language}"
- "translate text from {source} to {target}"
- "{image}를 {language}로 번역"
- "이 텍스트를 {language}로 변환"

# Inputs

- text (string): Text to translate [required if no image]
- image_path (string): Image containing text [required if no text]
- source_lang (string): Source language code [optional, default: auto]
- target_lang (string): Target language code [required]
- preserve_formatting (boolean): Keep original formatting [optional, default: true]

# Outputs

- original_text (string): Original text (extracted if from image)
- translated_text (string): Translated result
- source_language (string): Detected/specified source language
- target_language (string): Target language used
- confidence (float): Translation confidence score

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_translate import translate_text
result = translate_text(
    text='{text}',
    image_path='{image_path}',
    source_lang='{source_lang}',
    target_lang='{target_lang}',
    preserve_formatting={preserve_formatting}
)
print(result)
"
```

# Validation

Before execution:
1. Ensure either text or image_path is provided
2. Validate target_lang is a supported language
3. If image provided, verify it exists and is readable

# Error Handling

- No text provided: Prompt for text or image
- Unsupported language: List available languages
- Translation API failure: Retry with fallback service
- Empty source text: Return error message

# Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| en | English | ko | Korean |
| ja | Japanese | zh | Chinese |
| es | Spanish | fr | French |
| de | German | pt | Portuguese |
| it | Italian | ru | Russian |

# Example Usage

User: "Translate this image to English"
Action: Extract text via OCR, translate to English

User: "이 텍스트를 일본어로 번역해줘"
Action: Execute with target_lang=ja

User: "Translate from Korean to English: 안녕하세요"
Action: Execute with text provided, source_lang=ko, target_lang=en
