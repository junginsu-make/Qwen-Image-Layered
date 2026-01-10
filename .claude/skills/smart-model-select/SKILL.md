# smart-model-select

Intelligent AI model selection for optimal cost-quality balance.

## Description

Automatically selects the best AI model based on task complexity, budget constraints, and quality requirements. Reduces costs by 50-70% while maintaining quality.

**Features:**
- Task complexity assessment
- Budget-aware selection
- Cost-quality optimization
- Alternative suggestions

## Triggers

Activate this skill when user mentions:
- "모델 선택", "select model"
- "최적 모델", "best model"
- "비용 절감", "cost saving"
- "예산 맞춰", "within budget"
- "저렴하게", "cheaper"

## Usage

```python
from src.fal_api.model_selector import (
    select_model, assess_complexity, calculate_cost_quality_score,
    ModelSelector, TaskComplexity
)

# Select optimal model
result = select_model(
    task="Generate product photo for e-commerce",
    budget=0.10,
    prefer_quality=True
)

print(f"Model: {result['model']}")
print(f"Cost: ${result['cost']}")
print(f"Reason: {result['reason']}")

# Assess complexity
complexity = assess_complexity("Create detailed artwork")
print(f"Complexity: {complexity.value}")  # HIGH

# Get budget options
selector = ModelSelector()
options = selector.get_budget_options(
    task="Generate images",
    min_budget=0.01,
    max_budget=0.20
)
for opt in options:
    print(f"{opt['model']}: ${opt['cost']} ({opt['reason']})")
```

## Model Selection Matrix

| Complexity | Quality Pref | Model | Cost |
|------------|--------------|-------|------|
| LOW | Speed | flux-schnell | $0.003 |
| LOW | Normal | nano-banana | $0.039 |
| MEDIUM | Normal | nano-banana | $0.039 |
| MEDIUM | Quality | flux-dev | $0.025 |
| HIGH | Quality | nano-banana-pro | $0.15 |
| HIGH | Premium | nano-banana-pro (4K) | $0.30 |

## Complexity Indicators

**LOW Complexity:**
- "simple", "quick", "preview", "draft"
- Icons, logos, basic illustrations

**MEDIUM Complexity:**
- "standard", "product", "illustration"
- Regular photos, social media content

**HIGH Complexity:**
- "detailed", "professional", "4k", "commercial"
- Artwork, commercial photography, print-ready

## Cost Savings Example

| Scenario | Without Optimizer | With Optimizer | Savings |
|----------|------------------|----------------|---------|
| Simple icons (10x) | $1.50 | $0.30 | 80% |
| Product photos (5x) | $0.75 | $0.20 | 73% |
| Artwork (3x) | $0.45 | $0.45 | 0% (quality needed) |

## Integration

This skill integrates with:
- `intelligent-router` - Combined with intent routing
- `nano-banana-generate` - Model selection before generation
- `cost-tracking` - Budget monitoring
