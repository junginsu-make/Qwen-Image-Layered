---
name: smart-upscale
description: AI-powered image upscaling using Fal AI models
---

# Triggers

Keywords:
- upscale
- enlarge
- enhance resolution
- increase size
- make bigger
- higher resolution

Korean Keywords:
- 업스케일
- 확대
- 해상도 높이기
- 고화질
- 크게 만들어

Patterns:
- "upscale {image} to {scale}x"
- "enhance {image} resolution"
- "{image} 해상도를 {scale}배로"
- "이미지를 {scale}배 확대"

# Inputs

- image_path (string): Path to input image or layer file [required]
- scale_factor (integer): Upscaling factor (2x or 4x) [optional, default: 2]
- output_path (string): Output file path [optional, default: auto-generated]
- model (string): Upscaler model (standard, creative, ultra) [optional, default: standard]

# Outputs

- upscaled_path (string): Path to upscaled image
- original_size (object): {width, height} of original
- new_size (object): {width, height} of upscaled
- scale_applied (integer): Actual scale factor used

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.upscale import upscale_image
result = upscale_image(
    '{image_path}',
    scale_factor={scale_factor},
    output_path='{output_path}',
    model='{model}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate image_path exists and is valid image format
3. Ensure scale_factor is 2 or 4
4. Verify sufficient disk space for output

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env file
- Invalid image: Return error with supported formats (PNG, JPG, WebP)
- Scale factor invalid: Default to 2x with warning
- API timeout: Retry up to 3 times with exponential backoff
- Output too large: Warn if result exceeds 8192px

# API Reference

Uses Fal AI upscaler endpoint:
- Model: fal-ai/clarity-upscaler or fal-ai/real-esrgan
- Cost: ~$0.02 per image
- Max input: 4096px
- Processing time: 5-15 seconds

# Example Usage

User: "Upscale this image to 4x resolution"
Action: Execute with image_path=<provided>, scale_factor=4

User: "이 레이어를 고화질로 확대해줘"
Action: Execute with image_path=<provided>, scale_factor=2 (default)

User: "Enhance layer_1.png to higher resolution"
Action: Execute with image_path=layer_1.png, scale_factor=2
