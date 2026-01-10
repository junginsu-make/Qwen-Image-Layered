---
name: style-transfer
description: Apply artistic styles to images or layers using AI
---

# Triggers

Keywords:
- style transfer
- apply style
- transform style
- artistic style
- stylize

Korean Keywords:
- 스타일 변환
- 스타일 적용
- 수채화
- 유화
- 애니메이션 스타일

Patterns:
- "apply {style} style to {image}"
- "transform {image} to {style}"
- "make {image} look like {style}"
- "{image}를 {style} 스타일로 변환"
- "이 레이어를 {style}처럼"

# Inputs

- image_path (string): Path to input image or layer [required]
- style (string): Target style to apply [required]
- intensity (float): Style strength 0.0-1.0 [optional, default: 0.8]
- preserve_colors (boolean): Keep original colors [optional, default: false]
- output_path (string): Output file path [optional, default: auto-generated]

# Supported Styles

- watercolor: Soft, flowing watercolor painting effect
- oil_painting: Rich, textured oil painting style
- sketch: Pencil or charcoal sketch appearance
- cartoon: Bold outlines with flat colors
- anime: Japanese animation style
- impressionist: Monet-like impressionist style
- pop_art: Warhol-style pop art
- pixel_art: Retro pixel art style

# Outputs

- styled_path (string): Path to styled image
- style_applied (string): Name of style used
- intensity_used (float): Actual intensity applied
- preserved_alpha (boolean): Whether transparency was preserved

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.style_transfer import apply_style
result = apply_style(
    '{image_path}',
    style='{style}',
    intensity={intensity},
    preserve_colors={preserve_colors},
    output_path='{output_path}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate image_path exists and is readable
3. Verify style is in supported styles list
4. Ensure intensity is between 0.0 and 1.0

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env
- Invalid style: List available styles and ask user to choose
- Image not found: Return clear error with path
- API failure: Retry up to 3 times
- RGBA preservation: Ensure alpha channel is maintained for layers

# Layer Support

When applying to decomposed layers:
1. Preserve RGBA alpha channel
2. Apply style only to visible pixels
3. Maintain layer dimensions
4. Save as PNG to preserve transparency

# Example Usage

User: "Apply watercolor style to this image"
Action: Execute with style=watercolor, intensity=0.8

User: "이 레이어를 유화 스타일로 바꿔줘"
Action: Execute with style=oil_painting

User: "Make layer_2.png look like anime"
Action: Execute with image_path=layer_2.png, style=anime
