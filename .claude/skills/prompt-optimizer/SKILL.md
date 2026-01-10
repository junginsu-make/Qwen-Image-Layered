# prompt-optimizer

AI-powered prompt enhancement for better image generation.

## Description

Uses LLMs (Claude, GPT, Gemini) to enhance vague prompts into detailed, effective prompts that produce better image generation results.

**Features:**
- Prompt enhancement (vague → detailed)
- Quality scoring (0-1)
- Variation generation
- Style inference

## Triggers

Activate this skill when user mentions:
- "프롬프트 개선", "prompt improve"
- "프롬프트 최적화", "optimize prompt"
- "더 좋은 프롬프트", "better prompt"
- "프롬프트 점수", "score prompt"
- "프롬프트 변형", "variations"

## Usage

```python
from src.fal_api.prompt_optimizer import (
    enhance_prompt, generate_variations, score_prompt,
    PromptOptimizer, PromptStyle
)

# Enhance a vague prompt
original = "pretty flower"
enhanced = enhance_prompt(original)
# Returns: "A beautiful flower with delicate petals, soft natural lighting,
#           vibrant colors, high quality, detailed"

# With specific style
enhanced = enhance_prompt(
    "sunset landscape",
    style=PromptStyle.CINEMATIC
)

# Score prompt quality (0-1)
score = score_prompt("A breathtaking mountain view at golden hour")
print(f"Quality: {score:.0%}")  # Quality: 85%

# Generate variations
variations = generate_variations("forest scene", count=3)
for v in variations:
    print(v)
```

## LLM Models Used

| Task | Model | Provider | Cost |
|------|-------|----------|------|
| Enhancement | gemini-3-flash | Google | ~$0.001 |
| Scoring | Rule-based | Local | Free |
| Variations | gemini-3-flash | Google | ~$0.001 |

## Example Transformations

| Before | After |
|--------|-------|
| "nice car" | "A sleek sports car with glossy finish, dramatic lighting, professional automotive photography, high detail" |
| "cute dog" | "An adorable dog with expressive eyes, soft fur texture, natural outdoor lighting, warm tones, detailed portrait" |
| "pretty sunset" | "A breathtaking sunset with vibrant orange and purple sky, dramatic cloud formations, golden hour lighting, landscape photography" |

## Quality Score Breakdown

| Component | Weight | Description |
|-----------|--------|-------------|
| Word count | 30% | Optimal: 5-30 words |
| Quality keywords | 25% | "detailed", "high quality", etc. |
| Style keywords | 25% | Artistic style specification |
| Composition | 20% | Layout/framing guidance |

## Integration

This skill integrates with:
- `nano-banana-generate` - Enhanced prompts for generation
- `nano-banana-pro-generate` - Premium generation
- `text-to-layer` - Layer generation from text
