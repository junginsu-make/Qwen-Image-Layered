---
name: nano-banana-edit
description: Fast image editing with natural language prompts using Nano Banana
---

# Triggers

Keywords:
- edit image
- modify image
- change image
- quick edit
- alter image

Korean Keywords:
- 이미지 편집
- 사진 수정
- 변경해줘
- 바꿔줘
- 편집해줘

Patterns:
- "edit {image} to {change}"
- "change {object} in {image}"
- "modify {image}: {prompt}"
- "{image}에서 {object} 바꿔줘"
- "{image} 편집: {prompt}"

# Inputs

- image_path (string): Path to the input image [required]
- prompt (string): Description of the desired edit [required]
- output_path (string): Output file path [optional, default: auto-generated]

# Outputs

- edited_image (string): Path to the edited image
- model_used (string): Model identifier (nano-banana-edit)
- edit_time (float): Time taken in seconds
- cost (float): Estimated cost in USD

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.generation import edit_image
result = edit_image(
    image_path='{image_path}',
    prompt='{prompt}',
    model='nano-banana-edit',
    output_path='{output_path}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate image_path exists and is valid image
3. Validate prompt is not empty
4. Verify output directory is writable

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env file
- Invalid image: Return error with supported formats (PNG, JPG, WebP)
- Empty prompt: Return error with example edit prompts
- API timeout: Retry up to 3 times with exponential backoff
- Edit failed: Return error with API message

# API Reference

Uses Fal AI endpoint:
- Model: fal-ai/nano-banana/edit
- Base: Google Gemini 2.5 Flash Image
- Cost: $0.039 per edit
- Speed: ~8 seconds per edit
- Max input: 2K resolution
- Best for: Quick edits, simple modifications

# Supported Edits

1. **Object Modification**: Change colors, sizes, styles
2. **Background Changes**: Modify or replace backgrounds
3. **Style Transfer**: Apply artistic styles
4. **Add/Remove Elements**: Simple additions or removals
5. **Color Adjustments**: Change color schemes

# Example Usage

User: "Edit this image to make the sky purple"
Action: Execute with image_path=<provided>, prompt="change the sky to purple"

User: "이 사진에서 배경을 바꿔줘"
Action: Execute with image_path=<provided>, prompt="change the background to..."

User: "Make the car red instead of blue"
Action: Execute with image_path=<provided>, prompt="change the car color from blue to red"

# When to Use

Use nano-banana-edit when:
- Quick edits are needed
- Simple modifications required
- Budget is limited
- Iterating on edit concepts

For complex edits, use: nano-banana-pro-edit
