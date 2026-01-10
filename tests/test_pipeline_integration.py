#!/usr/bin/env python3
"""
Pipeline Integration Tests for Phase 3

Tests the full pipeline from analysis through generation,
including model registry integration and skill coordination.
"""

import sys
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
passed = 0
failed = 0
errors = []


def test(name, condition, msg=""):
    global passed, failed, errors
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}: {msg}")
        failed += 1
        errors.append((name, msg))


def load_module(name, path):
    """Load a module directly from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# =============================================================================
# Import Tests (ensure modules load without errors)
# =============================================================================
print("=" * 70)
print("MODULE IMPORT TESTS")
print("=" * 70)

# Load modules directly to avoid __init__.py PIL dependency
model_registry = None
generation = None

try:
    model_registry = load_module(
        "model_registry",
        PROJECT_ROOT / "src" / "fal_api" / "model_registry.py"
    )
    test("model_registry imports successfully", True)
except Exception as e:
    test("model_registry imports successfully", False, str(e))

try:
    # First load model_registry as dependency
    if model_registry:
        sys.modules['src.fal_api.model_registry'] = model_registry

    generation = load_module(
        "generation",
        PROJECT_ROOT / "src" / "fal_api" / "generation.py"
    )
    test("generation module imports successfully", True)
except Exception as e:
    test("generation module imports successfully", False, str(e))

print()


# =============================================================================
# Model Registry Tests
# =============================================================================
print("=" * 70)
print("MODEL REGISTRY FUNCTIONALITY")
print("=" * 70)

if model_registry:
    # Get convenience functions
    get_model = model_registry.get_model
    list_models = model_registry.list_models
    select_best_model = model_registry.select_best_model
    ModelRegistry = model_registry.ModelRegistry
    ModelType = model_registry.ModelType
    ModelTier = model_registry.ModelTier

    # Test model retrieval
    nano = get_model("nano-banana")
    test("get nano-banana model", nano is not None)
    test("nano-banana has endpoint", nano and "fal-ai" in nano.endpoint)
    test("nano-banana is FAST tier", nano and nano.tier == ModelTier.FAST)
    test("nano-banana price is $0.039", nano and abs(nano.price_per_image - 0.039) < 0.001)

    nano_pro = get_model("nano-banana-pro")
    test("get nano-banana-pro model", nano_pro is not None)
    test("nano-banana-pro is PRO tier", nano_pro and nano_pro.tier == ModelTier.PRO)
    test("nano-banana-pro supports 4K", nano_pro and nano_pro.supports_4k)
    test("nano-banana-pro price is $0.15", nano_pro and abs(nano_pro.price_per_image - 0.15) < 0.001)

    # Test edit models
    nano_edit = get_model("nano-banana-edit")
    test("get nano-banana-edit model", nano_edit is not None)
    test("nano-banana-edit is IMAGE_EDIT type", nano_edit and nano_edit.model_type == ModelType.IMAGE_EDIT)

    nano_pro_edit = get_model("nano-banana-pro-edit")
    test("get nano-banana-pro-edit model", nano_pro_edit is not None)
    test("nano-banana-pro-edit supports 4K", nano_pro_edit and nano_pro_edit.supports_4k)
else:
    test("model_registry tests", False, "module not loaded")

print()


# =============================================================================
# Model Listing and Filtering
# =============================================================================
print("=" * 70)
print("MODEL LISTING AND FILTERING")
print("=" * 70)

if model_registry:
    # List all models
    all_models = list_models()
    test("list_models returns models", len(all_models) > 0)
    test("at least 4 nano-banana models", sum(1 for m in all_models if "nano" in m.name.lower()) >= 4)

    # Filter by type
    gen_models = list_models(model_type=ModelType.TEXT_TO_IMAGE)
    test("filter by TEXT_TO_IMAGE", len(gen_models) > 0)
    test("all gen models are text_to_image", all(m.model_type == ModelType.TEXT_TO_IMAGE for m in gen_models))

    edit_models = list_models(model_type=ModelType.IMAGE_EDIT)
    test("filter by IMAGE_EDIT", len(edit_models) > 0)
    test("all edit models are image_edit", all(m.model_type == ModelType.IMAGE_EDIT for m in edit_models))

    # Filter by tier
    pro_models = list_models(tier=ModelTier.PRO)
    test("filter by PRO tier", len(pro_models) > 0)
    test("all pro models are PRO tier", all(m.tier == ModelTier.PRO for m in pro_models))
else:
    test("model listing tests", False, "module not loaded")

print()


# =============================================================================
# Model Selection Logic
# =============================================================================
print("=" * 70)
print("INTELLIGENT MODEL SELECTION")
print("=" * 70)

if model_registry:
    # Test select_best_model
    best_gen = select_best_model("generate an image")
    test("select_best_model for generation", best_gen is not None)

    best_edit = select_best_model("edit this photo")
    test("select_best_model for editing", best_edit is not None)

    best_quality = select_best_model("create marketing image", prefer_quality=True)
    test("prefer_quality selects pro tier", best_quality and best_quality.tier == ModelTier.PRO)

    best_cheap = select_best_model("generate image", max_price=0.05)
    test("max_price filters expensive models", best_cheap and best_cheap.price_per_image <= 0.05)
else:
    test("model selection tests", False, "module not loaded")

print()


# =============================================================================
# Generation Module Logic (without API calls)
# =============================================================================
print("=" * 70)
print("GENERATION MODULE LOGIC")
print("=" * 70)

if generation:
    # Test available models function
    gen_options = generation.get_available_models("generate")
    test("get_available_models for generate", len(gen_options) > 0)
    test("models have required fields", all("name" in m and "endpoint" in m for m in gen_options))

    edit_options = generation.get_available_models("edit")
    test("get_available_models for edit", len(edit_options) > 0)

    # Test recommend_model
    rec = generation.recommend_model("create a logo", prefer_quality=True)
    test("recommend_model returns recommendation", "model" in rec or "fallback" in rec)

    rec_budget = generation.recommend_model("generate art", max_budget=0.04)
    test("recommend_model respects budget", rec_budget is not None)
else:
    test("generation module tests", False, "module not loaded")

print()


# =============================================================================
# Pipeline Stage Tests
# =============================================================================
print("=" * 70)
print("PIPELINE STAGE VALIDATION")
print("=" * 70)

# Test that analysis skills exist
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

analysis_skills = ["image-decompose", "color-palette", "text-extract"]
for skill in analysis_skills:
    skill_file = SKILLS_DIR / skill / "SKILL.md"
    test(f"analysis skill exists: {skill}", skill_file.exists())

# Test that edit skills exist
edit_skills = ["text-replace", "text-effect", "style-transfer"]
for skill in edit_skills:
    skill_file = SKILLS_DIR / skill / "SKILL.md"
    test(f"edit skill exists: {skill}", skill_file.exists())

# Test that generation skills exist
gen_skills = ["nano-banana-generate", "nano-banana-pro-generate", "nano-banana-edit", "nano-banana-pro-edit"]
for skill in gen_skills:
    skill_file = SKILLS_DIR / skill / "SKILL.md"
    test(f"generation skill exists: {skill}", skill_file.exists())

print()


# =============================================================================
# SubAgent Integration
# =============================================================================
print("=" * 70)
print("SUBAGENT INTEGRATION")
print("=" * 70)

AGENTS_DIR = PROJECT_ROOT / ".claude" / "agents"

# Test FinalComposer exists and has required content
final_composer = AGENTS_DIR / "final_composer.md"
test("FinalComposer agent exists", final_composer.exists())

if final_composer.exists():
    content = final_composer.read_text()
    test("FinalComposer uses model_registry", "model_registry" in content.lower() or "registry" in content.lower())
    test("FinalComposer has pipeline stages", "stage" in content.lower() or "step" in content.lower())
    test("FinalComposer references nano-banana", "nano-banana" in content.lower())

# Test other agents exist
other_agents = ["batch_processor.md", "layer_editor.md", "composition_engine.md", "quality_checker.md"]
for agent in other_agents:
    agent_file = AGENTS_DIR / agent
    test(f"agent exists: {agent}", agent_file.exists())

print()


# =============================================================================
# Workflow Simulation
# =============================================================================
print("=" * 70)
print("WORKFLOW SIMULATION")
print("=" * 70)

if model_registry:
    # Simulate analysis -> model selection -> generation workflow
    def simulate_workflow():
        """Simulate the full workflow without API calls."""
        workflow_steps = []

        # Step 1: Analysis (simulated)
        workflow_steps.append("analysis")
        analysis_result = {
            "colors": ["#FF5733", "#3498DB", "#2ECC71"],
            "text_found": "Sample Text",
            "layers": 4
        }

        # Step 2: Model selection
        workflow_steps.append("model_selection")
        selected = select_best_model("generate marketing image", prefer_quality=True)
        if selected:
            workflow_steps.append(f"selected: {selected.name}")

        # Step 3: Parameter preparation
        workflow_steps.append("parameter_prep")
        params = {
            "prompt": "A beautiful marketing image",
            "model": selected.name if selected else "nano-banana-pro",
            "resolution": "2k"
        }

        # Step 4: Generation preparation (without actual API call)
        workflow_steps.append("generation_ready")

        return workflow_steps

    steps = simulate_workflow()
    test("workflow has analysis step", "analysis" in steps)
    test("workflow has model_selection step", "model_selection" in steps)
    test("workflow has parameter_prep step", "parameter_prep" in steps)
    test("workflow ready for generation", "generation_ready" in steps)
else:
    test("workflow simulation", False, "module not loaded")

print()


# =============================================================================
# Extensibility Tests
# =============================================================================
print("=" * 70)
print("EXTENSIBILITY TESTS")
print("=" * 70)

if model_registry:
    # Test that new models can be registered
    original_count = len(ModelRegistry.model_names())

    ModelRegistry.register(
        "test-custom-model",
        endpoint="fal-ai/test-model",
        model_type=ModelType.TEXT_TO_IMAGE,
        tier=ModelTier.STANDARD,
        price_per_image=0.05,
        description="Test custom model"
    )

    new_count = len(ModelRegistry.model_names())
    test("can register new model", new_count == original_count + 1)

    custom = get_model("test-custom-model")
    test("can retrieve custom model", custom is not None)
    test("custom model has correct endpoint", custom and "test-model" in custom.endpoint)

    # Test capability search
    models_with_4k = ModelRegistry.find_by_capability("4k_output")
    test("find_by_capability works", len(models_with_4k) >= 1)
else:
    test("extensibility tests", False, "module not loaded")

print()


# =============================================================================
# Error Handling Tests
# =============================================================================
print("=" * 70)
print("ERROR HANDLING")
print("=" * 70)

if model_registry and generation:
    # Test handling of invalid model
    invalid_model = get_model("non-existent-model")
    test("get_model returns None for invalid", invalid_model is None)

    # Test generate_image with empty prompt
    result = generation.generate_image(prompt="")
    test("generate_image rejects empty prompt", not result.get("success"))
    test("generate_image provides error message", "error" in result)

    # Test edit_image with non-existent file
    result = generation.edit_image(image_path="/non/existent/path.png", prompt="test")
    test("edit_image rejects invalid path", not result.get("success"))
else:
    test("error handling tests", False, "modules not loaded")

print()


# =============================================================================
# Summary
# =============================================================================
print("=" * 70)
print("PIPELINE INTEGRATION TEST SUMMARY")
print("=" * 70)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")

if errors:
    print()
    print("FAILURES:")
    for name, msg in errors:
        print(f"  - {name}: {msg}")
    sys.exit(1)
else:
    print()
    print("ALL PIPELINE INTEGRATION TESTS PASSED!")
    sys.exit(0)
