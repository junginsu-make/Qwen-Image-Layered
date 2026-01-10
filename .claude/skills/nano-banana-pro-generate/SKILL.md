---
name: nano-banana-pro-generate
description: High-quality text-to-image generation using Nano Banana Pro (Gemini 3 Pro)
---

# Triggers

Keywords:
- high quality generate
- premium image
- professional image
- 4K image
- best quality
- pro generate

Korean Keywords:
- 고품질 생성
- 고급 이미지
- 프로 생성
- 4K 이미지
- 최고 품질
- 전문가 수준

Patterns:
- "generate high quality {prompt}"
- "create professional {prompt}"
- "make 4K image of {prompt}"
- "{prompt} 고품질로 생성"
- "{prompt} 프로 품질로"

# Inputs

- prompt (string): Detailed text description of the image [required]
- aspect_ratio (string): Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4) [optional, default: 1:1]
- resolution (string): Output resolution (2k, 4k) [optional, default: 2k]
- num_images (integer): Number of images to generate (1-4) [optional, default: 1]
- output_dir (string): Output directory path [optional, default: ./output]

# Outputs

- generated_images (list): List of generated image paths
- model_used (string): Model identifier (nano-banana-pro)
- generation_time (float): Time taken in seconds
- resolution_used (string): Actual resolution used
- cost (float): Estimated cost in USD

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.generation import generate_image
result = generate_image(
    prompt='{prompt}',
    model='nano-banana-pro',
    aspect_ratio='{aspect_ratio}',
    resolution='{resolution}',
    num_images={num_images},
    output_dir='{output_dir}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate prompt is not empty (recommend detailed prompts)
3. Ensure resolution is 2k or 4k
4. Verify output directory is writable

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env file
- Empty prompt: Return error with detailed prompt examples
- Invalid resolution: Default to 2k with warning
- API timeout: Retry up to 3 times with exponential backoff
- 4K request: Warn about higher cost ($0.30)

# API Reference

Uses Fal AI endpoint:
- Model: fal-ai/nano-banana-pro
- Base: Google Gemini 3 Pro
- Cost: $0.15 per image (2K), $0.30 per image (4K)
- Speed: ~15 seconds per image
- Max resolution: 4K
- Best for: Final production, marketing, professional work

# Key Features

1. **Perfect Text Rendering**: Flawless typography in images
2. **Character Consistency**: Same character across multiple images
3. **Semantic Understanding**: Complex prompt interpretation
4. **4K Output**: Ultra-high resolution for print
5. **Infographic Quality**: Charts, diagrams without errors

# Example Usage

User: "Generate a high quality product shot with text"
Action: Execute with prompt="professional product photography...", resolution="4k"

User: "프로 품질로 인포그래픽 만들어줘"
Action: Execute with prompt="infographic about...", resolution="2k"

User: "Create marketing banner with perfect text"
Action: Execute with prompt="marketing banner...", resolution="4k"

# When to Use

Use nano-banana-pro-generate when:
- Text must be perfectly rendered
- Character consistency is needed
- Final production quality required
- 4K output is needed
- Infographics or diagrams

For quick drafts, use: nano-banana-generate
