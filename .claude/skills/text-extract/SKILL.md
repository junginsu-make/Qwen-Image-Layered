---
name: text-extract
description: Extract text from images using OCR (Optical Character Recognition)
---

# Triggers

Keywords:
- extract text
- OCR
- read text
- text recognition
- get text from image

Korean Keywords:
- 텍스트 추출
- OCR
- 글자 인식
- 문자 추출
- 이미지에서 텍스트

Patterns:
- "extract text from {image}"
- "OCR this {image}"
- "read the text in {image}"
- "{image}에서 텍스트 추출"
- "이 이미지의 글자 인식해줘"

# Inputs

- image_path (string): Path to input image [required]
- language (string): Primary language for OCR (auto, en, ko, ja, zh) [optional, default: auto]
- output_format (string): Output format (text, json, structured) [optional, default: text]
- confidence_threshold (float): Minimum confidence 0.0-1.0 [optional, default: 0.5]

# Outputs

- extracted_text (string): Full extracted text content
- blocks (array): Text blocks with positions
  - text (string): Block text content
  - confidence (float): OCR confidence score
  - bbox (object): Bounding box {x, y, width, height}
- language_detected (string): Detected language code
- total_characters (integer): Character count

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_ocr import extract_text
result = extract_text(
    '{image_path}',
    language='{language}',
    output_format='{output_format}',
    confidence_threshold={confidence_threshold}
)
print(result)
"
```

# Validation

Before execution:
1. Validate image_path exists and is readable
2. Check language code is supported
3. Verify confidence_threshold is 0.0-1.0
4. Ensure image has sufficient resolution for OCR

# Error Handling

- Image not found: Return clear error with path
- Low quality image: Warn and attempt with enhanced preprocessing
- No text detected: Return empty result with message
- Unsupported language: Fall back to auto-detect
- API timeout: Retry up to 3 times

# Supported Languages

| Code | Language |
|------|----------|
| auto | Auto-detect |
| en | English |
| ko | Korean |
| ja | Japanese |
| zh | Chinese |
| es | Spanish |
| fr | French |
| de | German |

# Example Usage

User: "Extract text from this screenshot"
Action: Execute with image_path=<provided>, language=auto

User: "이 이미지에서 한글 텍스트 추출해줘"
Action: Execute with language=ko

User: "OCR this document and give me JSON"
Action: Execute with output_format=json
