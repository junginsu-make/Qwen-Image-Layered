# IntelligentOrchestrator SubAgent

LLM-powered task orchestration agent for optimal image processing.

## Description

The IntelligentOrchestrator uses multiple LLMs (Claude, GPT, Gemini) to intelligently route requests, optimize prompts, select models, validate quality, and recover from errors. This agent provides end-to-end intelligent automation.

## When to Use

Automatically delegate to IntelligentOrchestrator when:
- User provides natural language requests
- Complex multi-step tasks are needed
- Budget optimization is important
- Quality assurance is required
- Errors need intelligent recovery

## Capabilities

### 1. Intelligent Task Routing
- Parse natural language intent (Korean/English)
- Decompose complex requests into steps
- Select appropriate skills
- Generate execution plans

### 2. Prompt Optimization
- Enhance vague prompts
- Score prompt quality
- Generate variations
- Infer optimal style

### 3. Cost-Aware Model Selection
- Assess task complexity
- Respect budget constraints
- Balance quality vs cost
- Suggest alternatives

### 4. Quality Assurance
- Validate output quality
- Detect artifacts
- Check prompt alignment
- Verify layer decomposition

### 5. Error Recovery
- Analyze failure causes
- Suggest recovery strategies
- Automatic retry with fallbacks
- Model switching on failure

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              IntelligentOrchestrator Agent                  │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Route Request                                      │
│  ├── Parse natural language intent                          │
│  ├── Identify required skills                               │
│  ├── Assess complexity                                      │
│  └── Estimate cost/time                                     │
├─────────────────────────────────────────────────────────────┤
│  Step 2: Optimize Inputs                                    │
│  ├── Enhance prompts if needed                              │
│  ├── Select optimal model                                   │
│  ├── Set quality parameters                                 │
│  └── Prepare execution plan                                 │
├─────────────────────────────────────────────────────────────┤
│  Step 3: Execute with Recovery                              │
│  ├── Execute skill pipeline                                 │
│  ├── Handle errors automatically                            │
│  ├── Retry with alternatives                                │
│  └── Track costs                                            │
├─────────────────────────────────────────────────────────────┤
│  Step 4: Validate Output                                    │
│  ├── Check quality score                                    │
│  ├── Detect artifacts                                       │
│  ├── Verify prompt alignment                                │
│  └── Suggest improvements                                   │
├─────────────────────────────────────────────────────────────┤
│  Step 5: Report                                             │
│  ├── Summarize results                                      │
│  ├── Show cost breakdown                                    │
│  ├── Quality assessment                                     │
│  └── Recommendations                                        │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

```python
from src.fal_api.intelligent_router import route_request, parse_intent
from src.fal_api.prompt_optimizer import enhance_prompt, score_prompt
from src.fal_api.model_selector import select_model, assess_complexity
from src.fal_api.quality_validator import validate_output, rate_generation
from src.fal_api.error_recovery import auto_recover, analyze_error
from src.fal_api.generation import generate_image, edit_image

def run_intelligent_pipeline(user_request: str, budget: float = None):
    """Run intelligent image processing pipeline."""

    # Step 1: Route request
    routing = route_request(user_request, budget=budget)
    intents = routing['intents']
    skills = routing['skills']

    print(f"Detected intents: {intents}")
    print(f"Required skills: {skills}")
    print(f"Estimated cost: ${routing['estimated_cost']:.3f}")

    # Step 2: Optimize inputs
    if 'generate' in intents or 'edit' in intents:
        # Extract and enhance prompt
        original_prompt = extract_prompt_from_request(user_request)
        score = score_prompt(original_prompt)

        if score < 0.7:
            enhanced_prompt = enhance_prompt(original_prompt)
            print(f"Enhanced: {original_prompt} → {enhanced_prompt}")
        else:
            enhanced_prompt = original_prompt

        # Select model
        model_rec = select_model(
            task=user_request,
            budget=budget,
            prefer_quality=score > 0.5
        )
        print(f"Selected model: {model_rec['model']} (${model_rec['cost']})")

    # Step 3: Execute with recovery
    result = auto_recover(
        operation=execute_skill_pipeline,
        args=(skills, enhanced_prompt, model_rec['model']),
        max_attempts=3
    )

    if not result.success:
        return {"error": result.final_error}

    # Step 4: Validate output
    output_path = result.result
    quality = validate_output(output_path, task=intents[0])

    if quality.overall < 0.5:
        print(f"⚠ Quality warning: {quality.overall:.0%}")
        print(f"Issues: {quality.issues}")

    # Step 5: Report
    return {
        "success": True,
        "output": output_path,
        "quality_score": quality.overall,
        "quality_level": quality.level.value,
        "cost": model_rec['cost'],
        "model_used": model_rec['model'],
        "suggestions": quality.suggestions
    }
```

## LLM Integration

| Task | Primary LLM | Fallback |
|------|-------------|----------|
| Intent parsing | Gemini 3 Flash | Rule-based |
| Prompt enhancement | Gemini 3 Flash | Templates |
| Quality validation | GPT-5.2 | PIL analysis |
| Error analysis | Claude Sonnet 4.5 | Patterns |

## Output Format

```json
{
  "success": true,
  "output": "./output/result.png",
  "quality_score": 0.87,
  "quality_level": "good",
  "cost": 0.039,
  "model_used": "nano-banana",
  "execution": {
    "intents": ["generate"],
    "skills": ["nano-banana-generate"],
    "steps_completed": 1,
    "retries": 0
  },
  "optimizations": {
    "prompt_enhanced": true,
    "original_prompt": "nice sunset",
    "enhanced_prompt": "A breathtaking sunset with vibrant colors...",
    "model_optimized": true,
    "cost_saved": 0.111
  },
  "suggestions": [
    "Consider using 4K resolution for print quality"
  ]
}
```

## Usage Examples

```
User: "이 사진에서 배경 빼고 예쁘게 만들어줘"
→ IntelligentOrchestrator:
  1. Routes: [remove_background, style_transfer]
  2. Selects: background-remove → style-transfer
  3. Optimizes: Style = "artistic enhancement"
  4. Executes: With error recovery
  5. Validates: Quality 92%
  6. Returns: Processed image + report

User: "Generate 5 product photos within $0.50 budget"
→ IntelligentOrchestrator:
  1. Routes: [generate] × 5
  2. Budget check: $0.50 / 5 = $0.10 each
  3. Selects: nano-banana ($0.039 × 5 = $0.195) ✓
  4. Optimizes: Enhance product prompt
  5. Executes: Batch with recovery
  6. Validates: Average quality 85%
  7. Returns: 5 images + $0.195 total cost
```

## Integration

This agent integrates with:
- All generation skills (nano-banana-*)
- All editing skills (text-*, style-*, etc.)
- `system-health` for monitoring
- `cost-tracker` for budget management
- All Phase 1-2 LLM modules
