---
name: font-match
description: Identify and match fonts from images using AI recognition
---

# Triggers

Keywords:
- identify font
- what font
- font match
- recognize font
- find font
- font detection

Korean Keywords:
- 폰트 찾기
- 글꼴 인식
- 폰트 매칭
- 서체 확인
- 폰트 뭐야

Patterns:
- "what font is this"
- "identify the font in {image}"
- "find font similar to {image}"
- "이 폰트 뭐야"
- "{image}의 폰트 찾아줘"

# Inputs

- image_path (string): Path to image with text [required]
- region (object): Specific region {x, y, width, height} [optional]
- include_similar (boolean): Include similar alternatives [optional, default: true]
- max_results (integer): Maximum fonts to return [optional, default: 5]
- filter_free (boolean): Only show free fonts [optional, default: false]

# Outputs

- primary_match (object): Best matching font
  - name (string): Font family name
  - style (string): Weight and style (Bold, Italic, etc.)
  - confidence (float): Match confidence 0.0-1.0
  - source (string): Where to get font (Google Fonts, Adobe, etc.)
- similar_fonts (array): Alternative similar fonts
- detected_characteristics (object):
  - serif (boolean): Has serifs
  - weight (string): Light, Regular, Bold, etc.
  - width (string): Condensed, Normal, Extended
  - style (string): Normal, Italic, Oblique

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.font_match import identify_font
result = identify_font(
    '{image_path}',
    include_similar={include_similar},
    max_results={max_results},
    filter_free={filter_free}
)
print(result)
"
```

# Validation

Before execution:
1. Validate image_path exists
2. Check image contains readable text
3. Verify region is within image bounds if provided
4. Ensure API access for font matching

# Error Handling

- No text detected: Prompt to select region with text
- Low quality image: Suggest higher resolution
- No matches found: Return closest approximations
- API failure: Fall back to local font database

# Output Example

```json
{
  "primary_match": {
    "name": "Montserrat",
    "style": "Bold",
    "confidence": 0.92,
    "source": "Google Fonts"
  },
  "similar_fonts": [
    {"name": "Gotham", "style": "Bold", "confidence": 0.85},
    {"name": "Proxima Nova", "style": "Bold", "confidence": 0.82}
  ],
  "detected_characteristics": {
    "serif": false,
    "weight": "Bold",
    "width": "Normal",
    "style": "Normal"
  }
}
```

# Example Usage

User: "What font is used in this logo?"
Action: Execute with image_path=<logo>, include_similar=true

User: "이 이미지의 폰트 찾아줘"
Action: Execute with include_similar=true

User: "Find free alternatives to this font"
Action: Execute with filter_free=true, max_results=10
