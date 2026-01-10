# quality-check

Vision AI-powered quality validation for generated images.

## Description

Uses Vision LLMs (GPT-5.2, Claude Sonnet 4.5) to assess image quality, detect artifacts, and validate results. Ensures output meets quality standards before delivery.

**Features:**
- Overall quality scoring
- Artifact detection
- Prompt alignment check
- Layer validation
- Improvement suggestions

## Triggers

Activate this skill when user mentions:
- "품질 검사", "quality check"
- "이미지 검증", "validate image"
- "결과 확인", "check result"
- "아티팩트", "artifacts"
- "품질 점수", "quality score"

## Usage

```python
from src.fal_api.quality_validator import (
    validate_output, rate_generation, detect_artifacts,
    QualityValidator, QualityScore
)

# Validate generated image
score = validate_output("generated.png", task="generation")
print(f"Quality: {score.overall:.0%}")
print(f"Level: {score.level.value}")
print(f"Issues: {score.issues}")

# Check prompt alignment
score = rate_generation(
    "generated.png",
    prompt="A sunset over mountains with purple sky"
)
print(f"Prompt match: {score.prompt_alignment:.0%}")

# Detect artifacts
artifacts = detect_artifacts("image.png")
for artifact in artifacts:
    print(f"Found: {artifact['type']} at {artifact['location']}")

# Validate layer decomposition
validator = QualityValidator()
result = validator.validate_layers(
    ["layer1.png", "layer2.png", "layer3.png"],
    expected_count=3
)
print(f"Valid: {result.is_valid}")
```

## Quality Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Clarity | 25% | Sharpness, focus quality |
| Composition | 20% | Framing, balance |
| Color | 20% | Accuracy, no banding |
| Technical | 20% | No artifacts, proper exposure |
| Aesthetic | 15% | Overall visual appeal |

## Quality Levels

| Level | Score | Action |
|-------|-------|--------|
| Excellent | 90%+ | Ready for use |
| Good | 75-89% | Minor improvements optional |
| Acceptable | 50-74% | May need adjustments |
| Poor | 30-49% | Recommend regeneration |
| Unacceptable | <30% | Must regenerate |

## Artifact Types Detected

| Artifact | Severity | Common Cause |
|----------|----------|--------------|
| Blur | Low-Medium | Motion, focus issues |
| Noise | Low | Low light, compression |
| Distortion | Medium | Model limitations |
| Color banding | Low | Gradient compression |
| Aliasing | Low | Resolution mismatch |
| Halo | Medium | Edge processing |
| Anatomical errors | High | AI generation artifacts |

## LLM Models Used

| Task | Model | Provider |
|------|-------|----------|
| Quality assessment | gpt-5.2 | OpenAI |
| Prompt alignment | gpt-5.2 | OpenAI |
| Fallback analysis | Rule-based | Local |

## Integration

This skill integrates with:
- `nano-banana-generate` - Post-generation validation
- `nano-banana-edit` - Edit quality check
- `image-decompose` - Layer quality validation
- `error-recovery` - Trigger regeneration on low quality
