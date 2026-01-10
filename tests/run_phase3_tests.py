#!/usr/bin/env python3
"""
Phase 3: Final Generation System - TDD Tests

Tests for:
1. Model Registry (extensible architecture for any Fal AI model)
2. Nano Banana Skills (4 skills)
3. FinalComposer SubAgent
4. Full pipeline integration
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
passed = 0
failed = 0
errors = []


def parse_yaml_frontmatter(content):
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    frontmatter = content[3:end].strip()
    result = {}
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def test(name, condition, msg=""):
    global passed, failed, errors
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}: {msg}")
        failed += 1
        errors.append((name, msg))


SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"
AGENTS_DIR = PROJECT_ROOT / ".claude" / "agents"
SRC_DIR = PROJECT_ROOT / "src" / "fal_api"


# =============================================================================
# SECTION 1: Model Registry Tests (Extensibility)
# =============================================================================
print("=" * 70)
print("MODEL REGISTRY - EXTENSIBILITY ARCHITECTURE")
print("=" * 70)

# Test: Model Registry file exists
registry_file = SRC_DIR / "model_registry.py"
test("model_registry.py exists", registry_file.exists())

if registry_file.exists():
    content = registry_file.read_text()

    # Test: ModelRegistry class exists
    test("ModelRegistry class defined", "class ModelRegistry" in content)

    # Test: Register model method
    test("register_model method exists", "def register_model" in content or "def register" in content)

    # Test: Get model method
    test("get_model method exists", "def get_model" in content or "def get" in content)

    # Test: List models method
    test("list_models method exists", "def list_models" in content or "def list" in content)

    # Test: Built-in Nano Banana models registered
    test("nano-banana model defined", "nano-banana" in content.lower())
    test("nano-banana-pro model defined", "nano-banana-pro" in content.lower())

    # Test: Extensible for future models (has add capability)
    test("extensible architecture",
         "register" in content.lower() or "add_model" in content.lower())

    # Test: Model info structure (endpoint, pricing, capabilities)
    test("model endpoint field", "endpoint" in content.lower())
    test("model pricing field", "price" in content.lower() or "cost" in content.lower())
    test("model capabilities field", "capabilities" in content.lower() or "features" in content.lower())

print()


# =============================================================================
# SECTION 2: Nano Banana Generate Skill
# =============================================================================
print("=" * 70)
print("SKILL: nano-banana-generate (Fast Text-to-Image)")
print("=" * 70)

skill_dir = SKILLS_DIR / "nano-banana-generate"
skill_file = skill_dir / "SKILL.md"
test("nano-banana-generate directory exists", skill_dir.exists())
test("SKILL.md exists", skill_file.exists())

if skill_file.exists():
    content = skill_file.read_text()
    fm = parse_yaml_frontmatter(content)

    # Basic structure
    test("name matches", fm.get("name") == "nano-banana-generate")
    test("has description", "description" in fm)

    # Triggers
    test("has generate keyword", "generate" in content.lower())
    test("has text-to-image keyword", "text" in content.lower() and "image" in content.lower())
    test("Korean triggers", any(t in content for t in ["생성", "만들어", "그려"]))

    # Inputs
    test("has prompt input", "prompt" in content.lower())
    test("has size/resolution input", any(t in content.lower() for t in ["size", "resolution", "width", "height"]))

    # Outputs
    test("has output path", "output" in content.lower())
    test("has image result", "image" in content.lower())

    # API reference
    test("references fal-ai/nano-banana", "fal-ai/nano-banana" in content)
    test("has pricing info", "$" in content or "cost" in content.lower())

print()


# =============================================================================
# SECTION 3: Nano Banana Pro Generate Skill
# =============================================================================
print("=" * 70)
print("SKILL: nano-banana-pro-generate (High-Quality Generation)")
print("=" * 70)

skill_dir = SKILLS_DIR / "nano-banana-pro-generate"
skill_file = skill_dir / "SKILL.md"
test("nano-banana-pro-generate directory exists", skill_dir.exists())
test("SKILL.md exists", skill_file.exists())

if skill_file.exists():
    content = skill_file.read_text()
    fm = parse_yaml_frontmatter(content)

    # Basic structure
    test("name matches", fm.get("name") == "nano-banana-pro-generate")

    # Pro features
    test("mentions high quality", any(t in content.lower() for t in ["high quality", "고품질", "premium", "pro"]))
    test("mentions 4K resolution", any(t in content.lower() for t in ["4k", "2k", "high resolution"]))
    test("mentions text rendering", "text" in content.lower())
    test("mentions character consistency", any(t in content.lower() for t in ["character", "consistent", "캐릭터"]))

    # Triggers
    test("Korean triggers", any(t in content for t in ["고품질 생성", "프로", "고급"]))

    # API reference
    test("references fal-ai/nano-banana-pro", "fal-ai/nano-banana-pro" in content)
    test("has higher pricing", "0.15" in content or "higher" in content.lower())

print()


# =============================================================================
# SECTION 4: Nano Banana Edit Skill
# =============================================================================
print("=" * 70)
print("SKILL: nano-banana-edit (Image Editing)")
print("=" * 70)

skill_dir = SKILLS_DIR / "nano-banana-edit"
skill_file = skill_dir / "SKILL.md"
test("nano-banana-edit directory exists", skill_dir.exists())
test("SKILL.md exists", skill_file.exists())

if skill_file.exists():
    content = skill_file.read_text()
    fm = parse_yaml_frontmatter(content)

    # Basic structure
    test("name matches", fm.get("name") == "nano-banana-edit")

    # Edit features
    test("has edit keyword", "edit" in content.lower())
    test("has input image param", any(t in content.lower() for t in ["input_image", "image_path", "source"]))
    test("has edit prompt", "prompt" in content.lower())

    # Triggers
    test("Korean triggers", any(t in content for t in ["편집", "수정", "변경"]))

    # API reference
    test("references fal-ai/nano-banana/edit", "nano-banana/edit" in content or "nano-banana" in content and "edit" in content)

print()


# =============================================================================
# SECTION 5: Nano Banana Pro Edit Skill
# =============================================================================
print("=" * 70)
print("SKILL: nano-banana-pro-edit (Advanced Editing)")
print("=" * 70)

skill_dir = SKILLS_DIR / "nano-banana-pro-edit"
skill_file = skill_dir / "SKILL.md"
test("nano-banana-pro-edit directory exists", skill_dir.exists())
test("SKILL.md exists", skill_file.exists())

if skill_file.exists():
    content = skill_file.read_text()
    fm = parse_yaml_frontmatter(content)

    # Basic structure
    test("name matches", fm.get("name") == "nano-banana-pro-edit")

    # Pro edit features
    test("mentions advanced editing", any(t in content.lower() for t in ["advanced", "고급", "professional"]))
    test("mentions semantic understanding", any(t in content.lower() for t in ["semantic", "context", "relationship"]))

    # Triggers
    test("Korean triggers", any(t in content for t in ["고급 편집", "프로 편집", "정밀 편집"]))

    # API reference
    test("references fal-ai/nano-banana-pro/edit", "nano-banana-pro" in content and "edit" in content)

print()


# =============================================================================
# SECTION 6: FinalComposer SubAgent
# =============================================================================
print("=" * 70)
print("SUBAGENT: FinalComposer")
print("=" * 70)

agent_file = AGENTS_DIR / "final_composer.md"
test("final_composer.md exists", agent_file.exists())

if agent_file.exists():
    content = agent_file.read_text()
    fm = parse_yaml_frontmatter(content)

    # Basic structure
    test("name is FinalComposer", fm.get("name") == "FinalComposer")
    test("has description", "description" in fm)
    test("has model specified", "model" in fm)
    test("has tools specified", "tools" in fm)

    # Role and capabilities
    test("orchestrates full pipeline", any(t in content.lower() for t in ["pipeline", "orchestrat", "workflow"]))
    test("uses analysis results", any(t in content.lower() for t in ["analysis", "분석", "result"]))
    test("generates final output", any(t in content.lower() for t in ["final", "output", "generate"]))

    # Integration with Nano Banana
    test("references nano-banana", "nano-banana" in content.lower())
    test("references model registry", any(t in content.lower() for t in ["registry", "model_registry", "select model"]))

    # Workflow steps
    test("has analysis step", any(t in content.lower() for t in ["step 1", "analyze", "분석"]))
    test("has generation step", any(t in content.lower() for t in ["generate", "create", "생성"]))
    test("has output step", any(t in content.lower() for t in ["output", "save", "export"]))

    # Error handling
    test("has error handling", "error" in content.lower())

print()


# =============================================================================
# SECTION 7: Generation Module (Python)
# =============================================================================
print("=" * 70)
print("PYTHON MODULE: generation.py")
print("=" * 70)

gen_file = SRC_DIR / "generation.py"
test("generation.py exists", gen_file.exists())

if gen_file.exists():
    content = gen_file.read_text()

    # Core functions
    test("generate_image function", "def generate_image" in content)
    test("edit_image function", "def edit_image" in content)

    # Model selection
    test("supports nano-banana", "nano-banana" in content.lower())
    test("supports nano-banana-pro", "nano-banana-pro" in content.lower())
    test("model parameter", "model" in content.lower())

    # Parameters
    test("prompt parameter", "prompt" in content)
    test("resolution/size parameter", any(t in content.lower() for t in ["resolution", "size", "width", "height"]))

    # Fal AI integration
    test("fal import or usage", "fal" in content.lower())

    # Error handling
    test("has error handling", "try" in content or "except" in content or "error" in content.lower())

    # Return structure
    test("returns result dict", "return" in content and ("{" in content or "dict" in content.lower()))

print()


# =============================================================================
# SECTION 8: Pipeline Integration
# =============================================================================
print("=" * 70)
print("PIPELINE INTEGRATION TESTS")
print("=" * 70)

# Test: Full pipeline flow exists
pipeline_test_file = PROJECT_ROOT / "tests" / "test_pipeline_integration.py"
test("test_pipeline_integration.py exists", pipeline_test_file.exists())

if pipeline_test_file.exists():
    content = pipeline_test_file.read_text()

    # Pipeline stages
    test("tests analysis stage", any(t in content.lower() for t in ["decompose", "analysis", "extract"]))
    test("tests editing stage", any(t in content.lower() for t in ["edit", "transform", "modify"]))
    test("tests generation stage", any(t in content.lower() for t in ["generate", "create", "nano"]))

    # Data flow
    test("tests data passing", any(t in content.lower() for t in ["result", "output", "input"]))

    # Model selection
    test("tests model selection", any(t in content.lower() for t in ["model", "registry", "select"]))

# Test: Model registry integration
if registry_file.exists():
    content = registry_file.read_text()

    # Future model extensibility
    future_models = ["flux", "stable-diffusion", "imagen", "dalle"]
    extensible = any(m in content.lower() for m in future_models) or "add" in content.lower() or "register" in content.lower()
    test("extensible for future models", extensible)

print()


# =============================================================================
# SECTION 9: Skill Trigger Completeness
# =============================================================================
print("=" * 70)
print("TRIGGER COMPLETENESS")
print("=" * 70)

# Check all 4 nano banana skills have proper triggers
nano_skills = [
    "nano-banana-generate",
    "nano-banana-pro-generate",
    "nano-banana-edit",
    "nano-banana-pro-edit"
]

for skill_name in nano_skills:
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if skill_file.exists():
        content = skill_file.read_text()

        # English triggers
        has_english = any(t in content.lower() for t in ["trigger", "keyword", "pattern"])
        test(f"{skill_name}: has English triggers", has_english)

        # Korean triggers
        has_korean = any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in content)
        test(f"{skill_name}: has Korean triggers", has_korean)

print()


# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("PHASE 3 TDD TEST SUMMARY")
print("=" * 70)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")

if errors:
    print()
    print("FAILURES:")
    for name, msg in errors:
        print(f"  - {name}: {msg}")
    print()
    print("RED PHASE: Implement the above to pass tests")
    sys.exit(1)
else:
    print()
    print("ALL PHASE 3 TESTS PASSED!")
    print("GREEN PHASE COMPLETE")
    sys.exit(0)
