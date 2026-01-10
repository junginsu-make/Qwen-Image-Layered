---
name: text-replace
description: Replace text in images while preserving style and background
---

# Triggers

Keywords:
- replace text
- change text
- swap text
- edit text in image
- text substitution

Korean Keywords:
- 텍스트 교체
- 글자 바꾸기
- 문자 변경
- 텍스트 수정
- 글씨 교체

Patterns:
- "replace '{old}' with '{new}' in {image}"
- "change text from '{old}' to '{new}'"
- "swap '{old}' to '{new}'"
- "{image}에서 '{old}'를 '{new}'로 바꿔"
- "'{old}' 텍스트를 '{new}'로 교체"

# Inputs

- image_path (string): Path to input image [required]
- old_text (string): Original text to find [required]
- new_text (string): Replacement text [required]
- match_style (boolean): Match original font style [optional, default: true]
- match_color (boolean): Match original text color [optional, default: true]
- font_override (string): Force specific font [optional]
- color_override (string): Force specific color [optional]

# Outputs

- output_path (string): Path to modified image
- replacements_made (integer): Number of replacements
- original_style (object): Detected original style
- matched_regions (array): Positions of replaced text

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_replace import replace_text
result = replace_text(
    '{image_path}',
    old_text='{old_text}',
    new_text='{new_text}',
    match_style={match_style},
    match_color={match_color}
)
print(result)
"
```

# Validation

Before execution:
1. Validate image_path exists
2. Ensure old_text is not empty
3. Verify new_text is provided
4. Check color_override is valid hex if provided

# Error Handling

- Text not found: Return original with message
- Style match failure: Use best approximation
- Font not available: Fall back to similar font
- Multiple matches: Replace all instances

# Process Flow

1. Detect text regions via OCR
2. Find regions matching old_text
3. Analyze original style (font, size, color)
4. Remove old text via inpainting
5. Render new text with matched style
6. Blend seamlessly with background

# Example Usage

User: "Replace 'SALE' with 'SOLD' in this banner"
Action: Execute with old_text="SALE", new_text="SOLD", match_style=true

User: "'Hello'를 '안녕'으로 바꿔줘"
Action: Execute with old_text="Hello", new_text="안녕"

User: "Change the price from $99 to $79"
Action: Execute with old_text="$99", new_text="$79", match_style=true
