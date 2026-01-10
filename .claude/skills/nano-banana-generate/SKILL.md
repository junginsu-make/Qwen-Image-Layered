---
name: nano-banana-generate
description: Fast text-to-image generation using Nano Banana (Gemini 2.5 Flash)
---

# Triggers

Keywords:
- generate image
- create image
- text to image
- draw
- make image
- quick generate

Korean Keywords:
- 이미지 생성
- 그림 그려
- 만들어줘
- 생성해줘
- 빠른 생성

Patterns:
- "generate {prompt}"
- "create an image of {prompt}"
- "draw {prompt}"
- "{prompt} 그려줘"
- "{prompt} 생성해줘"

# Inputs

- prompt (string): Text description of the image to generate [required]
- aspect_ratio (string): Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4) [optional, default: 1:1]
- num_images (integer): Number of images to generate (1-4) [optional, default: 1]
- output_dir (string): Output directory path [optional, default: ./output]

# Outputs

- generated_images (list): List of generated image paths
- model_used (string): Model identifier (nano-banana)
- generation_time (float): Time taken in seconds
- cost (float): Estimated cost in USD

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.generation import generate_image
result = generate_image(
    prompt='{prompt}',
    model='nano-banana',
    aspect_ratio='{aspect_ratio}',
    num_images={num_images},
    output_dir='{output_dir}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate prompt is not empty
3. Ensure aspect_ratio is valid
4. Verify output directory is writable

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env file
- Empty prompt: Return error with example prompts
- Invalid aspect ratio: Default to 1:1 with warning
- API timeout: Retry up to 3 times with exponential backoff
- Generation failed: Return error with API message

# API Reference

Uses Fal AI endpoint:
- Model: fal-ai/nano-banana
- Base: Google Gemini 2.5 Flash Image
- Cost: $0.039 per image
- Speed: ~5 seconds per image
- Max resolution: 2K
- Best for: Quick iterations, drafts, simple prompts

# Example Usage

User: "Generate an image of a sunset over mountains"
Action: Execute with prompt="a sunset over mountains", aspect_ratio="16:9"

User: "고양이 그림 그려줘"
Action: Execute with prompt="a cat", aspect_ratio="1:1"

User: "Create 3 variations of a logo design"
Action: Execute with prompt="logo design", num_images=3

# When to Use

Use nano-banana-generate when:
- Fast results are needed
- Budget is limited
- Simple or draft images required
- Iterating on concepts

For higher quality, use: nano-banana-pro-generate
