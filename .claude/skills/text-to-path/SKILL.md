---
name: text-to-path
description: Arrange text along curved paths, circles, or custom shapes
---

# Triggers

Keywords:
- curved text
- text on path
- circular text
- arc text
- wave text
- text along curve

Korean Keywords:
- 곡선 텍스트
- 원형 텍스트
- 패스 따라 글자
- 경로 텍스트
- 휘어진 글자

Patterns:
- "put text on a {shape} path"
- "make text follow {shape}"
- "create {shape} text '{content}'"
- "'{content}'를 {shape} 형태로"
- "원형으로 텍스트 배치"

# Inputs

- text (string): Text content to render [required]
- path_type (string): Path shape type [required]
- radius (integer): Radius for circular paths [optional, default: 200]
- start_angle (float): Starting angle in degrees [optional, default: 0]
- end_angle (float): Ending angle in degrees [optional, default: 360]
- direction (string): clockwise or counterclockwise [optional, default: clockwise]
- font (string): Font family [optional, default: Arial]
- font_size (integer): Font size [optional, default: 36]
- color (string): Text color [optional, default: #000000]
- output_size (object): {width, height} of output [optional, default: auto]

# Path Types

| Type | Description |
|------|-------------|
| circle | Full circular path |
| arc | Partial circular arc |
| wave | Sinusoidal wave pattern |
| spiral | Spiral from center outward |
| custom | SVG path definition |
| bezier | Bezier curve path |

# Outputs

- output_path (string): Path to generated image
- dimensions (object): {width, height} of output
- path_used (string): Path type applied
- text_length (integer): Characters rendered

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_path import render_text_on_path
result = render_text_on_path(
    text='{text}',
    path_type='{path_type}',
    radius={radius},
    start_angle={start_angle},
    end_angle={end_angle},
    font='{font}',
    font_size={font_size},
    color='{color}'
)
print(result)
"
```

# Validation

Before execution:
1. Ensure text is not empty
2. Validate path_type is supported
3. Check angles are valid (0-360)
4. Verify radius is positive

# Error Handling

- Invalid path type: List available types
- Text too long: Adjust font size or warn
- Invalid angles: Normalize to valid range
- Rendering failure: Fall back to simple arc

# Example Usage

User: "Create circular text 'PREMIUM QUALITY'"
Action: Execute with text="PREMIUM QUALITY", path_type=circle

User: "'SALE' 텍스트를 아치형으로 만들어줘"
Action: Execute with text="SALE", path_type=arc, start_angle=180, end_angle=360

User: "Make wavy text 'Ocean Waves'"
Action: Execute with text="Ocean Waves", path_type=wave
