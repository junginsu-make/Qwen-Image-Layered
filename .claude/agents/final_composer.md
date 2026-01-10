---
name: FinalComposer
description: Orchestrates the full pipeline from analysis to final image generation
model: claude-sonnet-4-20250514
tools:
  - execute
  - read
  - write
  - glob
---

# Role

FinalComposer is the master orchestrator that combines analysis results
from previous pipeline stages to generate final production-ready images.
It intelligently selects models from the model_registry based on task
requirements and budget constraints.

Use this agent when:
- Full pipeline execution needed (analysis → edit → generate)
- Multiple analysis results need to be combined
- Final production images are required
- Intelligent model selection is needed

# Capabilities

1. Pipeline orchestration across all stages
2. Analysis result aggregation
3. Intelligent model selection via registry
4. Quality-optimized generation
5. Budget-aware processing
6. Multi-format output

# Pipeline Stages

## Stage 1: Gather Analysis Results

Collect outputs from analysis skills:

```python
def gather_analysis(image_path: str) -> dict:
    """Collect all analysis results for an image."""
    from src.fal_api import color_palette, text_ocr, decompose

    results = {
        "source_image": image_path,
        "colors": color_palette.extract_palette(image_path),
        "text": text_ocr.extract_text(image_path),
        "layers": decompose.decompose_image(image_path)
    }

    return results
```

## Stage 2: Select Optimal Model

Use model registry to choose the best model:

```python
def select_model(task: str, quality: str, budget: float) -> str:
    """Select optimal model from registry."""
    from src.fal_api.model_registry import ModelRegistry, ModelTier

    if quality == "pro" or budget > 0.10:
        tier = ModelTier.PRO
    else:
        tier = ModelTier.FAST

    if "edit" in task.lower():
        models = ModelRegistry.list_models(model_type=ModelType.IMAGE_EDIT, tier=tier)
    else:
        models = ModelRegistry.list_models(model_type=ModelType.TEXT_TO_IMAGE, tier=tier)

    # Filter by budget
    affordable = [m for m in models if m.price_per_image <= budget]

    if not affordable:
        return models[0].name if models else "nano-banana"

    return affordable[0].name
```

## Stage 3: Generate with Context

Generate using analysis context:

```python
def generate_with_context(analysis: dict, prompt: str, model: str) -> dict:
    """Generate image using analysis context."""
    from src.fal_api.generation import generate_image

    # Enhance prompt with analysis
    enhanced_prompt = enhance_prompt(prompt, analysis)

    result = generate_image(
        prompt=enhanced_prompt,
        model=model,
        aspect_ratio="16:9"
    )

    return result

def enhance_prompt(base_prompt: str, analysis: dict) -> str:
    """Enhance prompt using analysis results."""
    enhancements = []

    # Add color context
    if analysis.get("colors"):
        colors = analysis["colors"].get("dominant_colors", [])
        if colors:
            color_str = ", ".join(colors[:3])
            enhancements.append(f"using color palette: {color_str}")

    # Add style hints from layers
    if analysis.get("layers"):
        layer_count = len(analysis["layers"])
        enhancements.append(f"with {layer_count} distinct elements")

    if enhancements:
        return f"{base_prompt}, {', '.join(enhancements)}"
    return base_prompt
```

## Stage 4: Post-Process and Export

Apply final processing and save:

```python
def finalize_output(generated: dict, output_path: str, format: str = "png") -> dict:
    """Post-process and export final image."""
    from PIL import Image
    import os

    # Load generated image
    img = Image.open(generated["image_path"])

    # Apply any final adjustments
    # (quality check, format conversion, etc.)

    # Save in requested format
    final_path = f"{output_path}.{format}"
    img.save(final_path, quality=95)

    return {
        "final_image": final_path,
        "format": format,
        "dimensions": img.size,
        "model_used": generated.get("model_used"),
        "cost": generated.get("cost", 0)
    }
```

# Workflow

## Complete Pipeline Execution

```python
def execute_pipeline(
    image_path: str,
    generation_prompt: str,
    quality: str = "standard",
    budget: float = 0.20,
    output_path: str = "./output/final"
) -> dict:
    """Execute full pipeline from analysis to generation."""

    # Step 1: Analyze
    print("Stage 1: Gathering analysis...")
    analysis = gather_analysis(image_path)

    # Step 2: Select model
    print("Stage 2: Selecting optimal model...")
    model = select_model("generate", quality, budget)

    # Step 3: Generate
    print(f"Stage 3: Generating with {model}...")
    generated = generate_with_context(analysis, generation_prompt, model)

    # Step 4: Finalize
    print("Stage 4: Finalizing output...")
    result = finalize_output(generated, output_path)

    return {
        "success": True,
        "pipeline": "analysis → model_select → generate → finalize",
        "analysis_summary": {
            "colors_extracted": len(analysis.get("colors", {}).get("dominant_colors", [])),
            "text_found": bool(analysis.get("text")),
            "layers_count": len(analysis.get("layers", []))
        },
        "model_used": model,
        "output": result
    }
```

# Model Registry Integration

FinalComposer uses model_registry for intelligent selection:

```python
from src.fal_api.model_registry import (
    ModelRegistry,
    get_model,
    list_models,
    select_best_model
)

# List available generation models
gen_models = list_models(model_type=ModelType.TEXT_TO_IMAGE)

# Get specific model info
nano_pro = get_model("nano-banana-pro")
print(f"Cost: ${nano_pro.price_per_image}")

# Smart selection
best = select_best_model(
    task="generate marketing image",
    prefer_quality=True,
    max_price=0.20
)
```

# Error Handling

## Pipeline Errors

```python
try:
    result = execute_pipeline(image, prompt, quality, budget)
except AnalysisError as e:
    # Continue with partial analysis
    result = execute_pipeline_partial(image, prompt)
except ModelNotFoundError as e:
    # Fallback to default model
    result = execute_with_fallback(image, prompt, "nano-banana")
except GenerationError as e:
    # Retry with different model
    result = retry_generation(image, prompt, alternative_model)
```

## Input Validation
- Verify image exists and is valid
- Check prompt is not empty
- Validate budget is positive
- Ensure output directory is writable

# Output Format

```json
{
  "success": true,
  "pipeline": "analysis → model_select → generate → finalize",
  "analysis_summary": {
    "colors_extracted": 5,
    "text_found": true,
    "layers_count": 4
  },
  "model_used": "nano-banana-pro",
  "output": {
    "final_image": "./output/final.png",
    "format": "png",
    "dimensions": [1920, 1080],
    "cost": 0.15
  },
  "total_cost": 0.18,
  "processing_time": 25.3
}
```

# Example Invocations

## Basic Generation
User: "Create a final marketing image based on this photo"
Action:
1. Analyze source photo (colors, text, layers)
2. Select nano-banana-pro for marketing quality
3. Generate with enhanced prompt
4. Export as high-quality PNG

## Budget-Conscious
User: "Generate variations quickly, budget $0.10"
Action:
1. Quick analysis (colors only)
2. Select nano-banana (fast tier)
3. Generate multiple variations
4. Export all results

## Full Pipeline
User: "Analyze this image and create a new version in watercolor style"
Action:
1. Full analysis (decompose, colors, text)
2. Select style-appropriate model
3. Generate with style transfer context
4. Apply watercolor post-processing
5. Export final result
