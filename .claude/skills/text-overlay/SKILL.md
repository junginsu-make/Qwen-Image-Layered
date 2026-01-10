---
name: text-overlay
description: Add text overlays to images with customizable styling
---

# Triggers

Keywords:
- add text
- text overlay
- watermark
- caption
- write on image

Korean Keywords:
- 텍스트 추가
- 글자 넣기
- 워터마크
- 캡션 추가
- 이미지에 글씨

Patterns:
- "add text '{content}' to {image}"
- "put watermark on {image}"
- "write '{content}' on {image}"
- "{image}에 '{content}' 텍스트 추가"
- "워터마크 넣어줘"

# Inputs

- image_path (string): Path to input image [required]
- text (string): Text content to add [required]
- position (string): Placement (center, top, bottom, top-left, etc.) [optional, default: center]
- x (integer): Custom X position in pixels [optional]
- y (integer): Custom Y position in pixels [optional]
- font (string): Font family name [optional, default: Arial]
- font_size (integer): Font size in pixels [optional, default: 48]
- color (string): Text color as hex [optional, default: #FFFFFF]
- opacity (float): Text opacity 0.0-1.0 [optional, default: 1.0]
- stroke_color (string): Outline color [optional]
- stroke_width (integer): Outline width [optional, default: 0]

# Outputs

- output_path (string): Path to image with text overlay
- text_bounds (object): {x, y, width, height} of text area
- applied_styles (object): Final style values used

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_overlay import add_text_overlay
result = add_text_overlay(
    '{image_path}',
    text='{text}',
    position='{position}',
    font='{font}',
    font_size={font_size},
    color='{color}',
    opacity={opacity}
)
print(result)
"
```

# Validation

Before execution:
1. Validate image_path exists
2. Ensure text is not empty
3. Verify color is valid hex format
4. Check opacity is 0.0-1.0
5. Validate font is available or use fallback

# Error Handling

- Image not found: Return error with path
- Empty text: Prompt for text content
- Invalid color: Default to white with warning
- Font not found: Fall back to system default
- Position out of bounds: Clamp to image edges

# Position Presets

| Position | Description |
|----------|-------------|
| center | Center of image |
| top | Top center |
| bottom | Bottom center |
| top-left | Top left corner |
| top-right | Top right corner |
| bottom-left | Bottom left corner |
| bottom-right | Bottom right corner |

# Example Usage

User: "Add 'Copyright 2024' watermark to this image"
Action: Execute with text="Copyright 2024", position=bottom-right, opacity=0.5

User: "이미지 가운데에 '샘플' 텍스트 넣어줘"
Action: Execute with text="샘플", position=center

User: "Put red title 'SALE' at the top"
Action: Execute with text="SALE", position=top, color=#FF0000
