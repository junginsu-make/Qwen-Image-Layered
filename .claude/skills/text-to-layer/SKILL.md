---
name: text-to-layer
description: Generate new image layers from text descriptions using AI
---

# Triggers

Keywords:
- generate layer
- create layer
- add layer from text
- make layer
- text to layer

Korean Keywords:
- 레이어 생성
- 레이어 추가
- 텍스트로 레이어
- 레이어 만들어
- 그려줘

Patterns:
- "generate a layer of {description}"
- "create layer with {description}"
- "add a {description} layer"
- "{description} 레이어를 생성"
- "{description}을 새 레이어로 만들어"

# Inputs

- prompt (string): Text description of desired layer content [required]
- width (integer): Layer width in pixels [optional, default: 1024]
- height (integer): Layer height in pixels [optional, default: 1024]
- style (string): Generation style (realistic, artistic, flat) [optional, default: realistic]
- transparent_bg (boolean): Generate with transparent background [optional, default: true]
- output_path (string): Output file path [optional, default: auto-generated]

# Outputs

- layer_path (string): Path to generated RGBA layer
- dimensions (object): {width, height} of generated layer
- has_transparency (boolean): Whether layer has transparent areas
- prompt_used (string): Final prompt sent to API

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_to_layer import generate_layer
result = generate_layer(
    prompt='{prompt}',
    width={width},
    height={height},
    style='{style}',
    transparent_bg={transparent_bg},
    output_path='{output_path}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate prompt is not empty
3. Ensure dimensions are reasonable (64-2048px)
4. Verify style is supported

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env
- Empty prompt: Ask user for description
- Invalid dimensions: Clamp to valid range with warning
- Generation failure: Retry up to 2 times
- NSFW content: Return error without generating

# API Reference

Uses Fal AI Flux model for generation:
- Model: fal-ai/flux/schnell or fal-ai/flux/dev
- Cost: ~$0.03 per image
- Supports transparent PNG output
- Processing time: 5-20 seconds

# Transparency Handling

For transparent backgrounds:
1. Add "on transparent background, PNG" to prompt
2. Use model that supports alpha channel
3. Post-process to clean edges if needed
4. Save as RGBA PNG

# Example Usage

User: "Generate a layer with a red sports car"
Action: Execute with prompt="red sports car", transparent_bg=true

User: "빨간 장미꽃 레이어를 만들어줘"
Action: Execute with prompt="red rose flower", transparent_bg=true

User: "Create a 512x512 layer with golden sparkles"
Action: Execute with prompt="golden sparkles", width=512, height=512

User: "Add a cartoon sun layer"
Action: Execute with prompt="cartoon sun", style=artistic
