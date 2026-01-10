---
name: text-effect
description: Apply visual effects to text layers (shadow, glow, neon, 3D)
---

# Triggers

Keywords:
- text effect
- text shadow
- glow text
- neon text
- 3d text
- text style

Korean Keywords:
- 텍스트 효과
- 그림자 효과
- 네온 효과
- 글자 효과
- 효과 적용

Patterns:
- "add {effect} effect to text"
- "make text {effect}"
- "apply {effect} to '{text}'"
- "텍스트에 {effect} 효과 적용"
- "네온 스타일로 만들어줘"

# Inputs

- image_path (string): Image with text or base image [required]
- text (string): Text to render with effect [required if no existing text]
- effect (string): Effect type to apply [required]
- color (string): Primary effect color [optional, default: #FFFFFF]
- intensity (float): Effect strength 0.0-1.0 [optional, default: 0.8]
- blur (integer): Blur radius for soft effects [optional, default: 5]
- offset_x (integer): Horizontal offset for shadows [optional, default: 3]
- offset_y (integer): Vertical offset for shadows [optional, default: 3]

# Supported Effects

| Effect | Description |
|--------|-------------|
| shadow | Drop shadow behind text |
| glow | Soft outer glow |
| neon | Bright neon light effect |
| outline | Solid outline/stroke |
| gradient | Gradient fill text |
| 3d | 3D extrusion effect |
| emboss | Raised embossed look |
| blur | Soft blurred text |

# Outputs

- output_path (string): Path to image with effect applied
- effect_applied (string): Effect type used
- effect_params (object): Parameters used for effect

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_effect import apply_text_effect
result = apply_text_effect(
    '{image_path}',
    text='{text}',
    effect='{effect}',
    color='{color}',
    intensity={intensity},
    blur={blur}
)
print(result)
"
```

# Validation

Before execution:
1. Validate effect is in supported list
2. Check intensity is 0.0-1.0
3. Verify color is valid hex
4. Ensure image or text is provided

# Error Handling

- Unknown effect: List available effects
- Invalid parameters: Use defaults with warning
- Rendering failure: Try simpler effect version
- Memory limit: Reduce blur/intensity

# Example Usage

User: "Add drop shadow to this text"
Action: Execute with effect=shadow

User: "네온 효과로 'OPEN' 텍스트 만들어줘"
Action: Execute with text="OPEN", effect=neon, color=#00FFFF

User: "Make the title glow in blue"
Action: Execute with effect=glow, color=#0066FF
