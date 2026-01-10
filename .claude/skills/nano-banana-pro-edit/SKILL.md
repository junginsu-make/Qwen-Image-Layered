---
name: nano-banana-pro-edit
description: Advanced semantic image editing using Nano Banana Pro (Gemini 3 Pro)
---

# Triggers

Keywords:
- advanced edit
- professional edit
- precise edit
- semantic edit
- pro edit
- complex edit

Korean Keywords:
- 고급 편집
- 정밀 편집
- 프로 편집
- 전문가 편집
- 세밀한 수정

Patterns:
- "advanced edit {image}: {prompt}"
- "professionally edit {image}"
- "precisely modify {image}"
- "{image} 고급 편집: {prompt}"
- "{image} 정밀 수정해줘"

# Inputs

- image_path (string): Path to the input image [required]
- prompt (string): Detailed description of the desired edit [required]
- resolution (string): Output resolution (2k, 4k) [optional, default: 2k]
- output_path (string): Output file path [optional, default: auto-generated]

# Outputs

- edited_image (string): Path to the edited image
- model_used (string): Model identifier (nano-banana-pro-edit)
- resolution_used (string): Output resolution
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
    model='nano-banana-pro-edit',
    resolution='{resolution}',
    output_path='{output_path}'
)
print(result)
"
```

# Validation

Before execution:
1. Check FAL_KEY environment variable exists
2. Validate image_path exists and is valid image
3. Validate prompt is detailed and specific
4. Ensure resolution is 2k or 4k

# Error Handling

- Missing FAL_KEY: Prompt user to configure .env file
- Invalid image: Return error with supported formats
- Vague prompt: Suggest more specific edit description
- API timeout: Retry up to 3 times with exponential backoff
- 4K request: Warn about higher cost ($0.30)

# API Reference

Uses Fal AI endpoint:
- Model: fal-ai/nano-banana-pro/edit
- Base: Google Gemini 3 Pro
- Cost: $0.15 per edit (2K), $0.30 per edit (4K)
- Speed: ~20 seconds per edit
- Max resolution: 4K output
- Best for: Professional edits, complex modifications

# Advanced Capabilities

1. **Semantic Understanding**: Understands object relationships
2. **Context Awareness**: Considers surrounding elements
3. **Lighting Adjustment**: Realistic lighting changes
4. **Composition Aware**: Maintains visual balance
5. **Style Preservation**: Keeps original aesthetic
6. **Complex Modifications**: Multi-element changes

# Example Usage

User: "Professionally edit to change the lighting to golden hour"
Action: Execute with prompt="change lighting to warm golden hour sunset lighting, maintaining shadows and reflections", resolution="4k"

User: "정밀하게 편집해서 배경은 유지하면서 인물만 다른 포즈로"
Action: Execute with prompt="change person pose while maintaining exact background and lighting", resolution="2k"

User: "Advanced edit: make this look like a vintage photograph"
Action: Execute with prompt="transform into authentic vintage photograph with film grain, faded colors, and period-appropriate styling", resolution="2k"

# When to Use

Use nano-banana-pro-edit when:
- Complex semantic edits needed
- Professional quality required
- Lighting/composition changes
- Context-aware modifications
- Final production edits

For simple quick edits, use: nano-banana-edit

# Integration with Analysis

Best results when combined with:
1. color-palette: Extract colors before editing
2. text-extract: Preserve text during edits
3. image-decompose: Edit specific layers
4. QualityChecker: Validate edit results
