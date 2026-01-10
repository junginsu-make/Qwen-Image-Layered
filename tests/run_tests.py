#!/usr/bin/env python3
"""
Manual test runner for Qwen-Image-Layered Agent System.
Runs all validation tests without requiring pytest.
"""

import sys
import re
import traceback
from pathlib import Path
from typing import Callable, List, Tuple


PROJECT_ROOT = Path(__file__).parent.parent

# Test counters
passed = 0
failed = 0
errors = []


def test(name: str):
    """Decorator for test functions."""
    def decorator(func: Callable):
        def wrapper():
            global passed, failed, errors
            try:
                func()
                passed += 1
                print(f"  [PASS] {name}")
                return True
            except AssertionError as e:
                failed += 1
                errors.append((name, str(e)))
                print(f"  [FAIL] {name}: {e}")
                return False
            except Exception as e:
                failed += 1
                errors.append((name, f"Error: {e}"))
                print(f"  [ERROR] {name}: {e}")
                return False
        wrapper.__name__ = name
        return wrapper
    return decorator


def parse_yaml_frontmatter(content: str) -> dict:
    """Simple YAML frontmatter parser."""
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
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                # Parse list
                items = value[1:-1].split(",")
                result[key] = [item.strip() for item in items]
            else:
                result[key] = value
    return result


# Proper emoji pattern that excludes Korean, CJK, and box-drawing characters
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    "\U00002600-\U000026FF"  # misc symbols (sun, cloud, etc)
    "\U00002700-\U000027BF"  # dingbats
    "]+",
    flags=re.UNICODE
)


# ============= SKILLS TESTS =============

print("\n" + "="*60)
print("SKILLS UNIT TESTS")
print("="*60)

SKILLS = [
    "image-decompose", "layer-export", "quick-edit", "background-remove",
    "smart-upscale", "style-transfer", "color-palette", "text-to-layer",
    "text-extract", "text-translate", "text-overlay", "text-effect",
    "text-to-path", "text-remove", "text-replace", "font-match"
]

@test("Skills directory exists")
def test_skills_dir_exists():
    assert (PROJECT_ROOT / ".claude" / "skills").exists()


for skill_name in SKILLS:
    @test(f"Skill '{skill_name}' exists")
    def test_skill_exists(name=skill_name):
        path = PROJECT_ROOT / ".claude" / "skills" / name / "SKILL.md"
        assert path.exists(), f"SKILL.md not found for {name}"

    @test(f"Skill '{skill_name}' has frontmatter")
    def test_skill_frontmatter(name=skill_name):
        path = PROJECT_ROOT / ".claude" / "skills" / name / "SKILL.md"
        content = path.read_text()
        assert content.startswith("---"), "Missing YAML frontmatter"
        fm = parse_yaml_frontmatter(content)
        assert "name" in fm, "Missing 'name' in frontmatter"
        assert "description" in fm, "Missing 'description' in frontmatter"

    @test(f"Skill '{skill_name}' has required sections")
    def test_skill_sections(name=skill_name):
        path = PROJECT_ROOT / ".claude" / "skills" / name / "SKILL.md"
        content = path.read_text()
        required = ["Triggers", "Inputs", "Outputs", "Execution"]
        for section in required:
            assert f"# {section}" in content, f"Missing section: {section}"

    @test(f"Skill '{skill_name}' under 200 lines")
    def test_skill_lines(name=skill_name):
        path = PROJECT_ROOT / ".claude" / "skills" / name / "SKILL.md"
        content = path.read_text()
        lines = len(content.splitlines())
        assert lines < 200, f"Has {lines} lines (max 200)"

    @test(f"Skill '{skill_name}' has no emojis")
    def test_skill_no_emojis(name=skill_name):
        path = PROJECT_ROOT / ".claude" / "skills" / name / "SKILL.md"
        content = path.read_text()
        matches = EMOJI_PATTERN.findall(content)
        assert not matches, f"Found emojis: {matches}"


# Run skill tests
for name, obj in list(globals().items()):
    if name.startswith("test_skill") and callable(obj):
        obj()


# ============= SUBAGENTS TESTS =============

print("\n" + "="*60)
print("SUBAGENTS UNIT TESTS")
print("="*60)

AGENTS = [
    "batch_processor", "layer_editor", "composition_engine",
    "quality_checker", "template_engine"
]
VALID_MODELS = ["claude-sonnet-4-20250514", "claude-haiku-3-5-20241022", "claude-opus-4-5-20251101"]

@test("Agents directory exists")
def test_agents_dir_exists():
    assert (PROJECT_ROOT / ".claude" / "agents").exists()

test_agents_dir_exists()


for agent_name in AGENTS:
    @test(f"Agent '{agent_name}' exists")
    def test_agent_exists(name=agent_name):
        path = PROJECT_ROOT / ".claude" / "agents" / f"{name}.md"
        assert path.exists(), f"{name}.md not found"

    @test(f"Agent '{agent_name}' has frontmatter")
    def test_agent_frontmatter(name=agent_name):
        path = PROJECT_ROOT / ".claude" / "agents" / f"{name}.md"
        content = path.read_text()
        assert content.startswith("---"), "Missing YAML frontmatter"
        fm = parse_yaml_frontmatter(content)
        assert "name" in fm, "Missing 'name' in frontmatter"
        assert "description" in fm, "Missing 'description' in frontmatter"
        assert "model" in fm, "Missing 'model' in frontmatter"

    @test(f"Agent '{agent_name}' uses valid model")
    def test_agent_model(name=agent_name):
        path = PROJECT_ROOT / ".claude" / "agents" / f"{name}.md"
        content = path.read_text()
        fm = parse_yaml_frontmatter(content)
        model = fm.get("model", "")
        assert model in VALID_MODELS, f"Invalid model: {model}"

    @test(f"Agent '{agent_name}' has required sections")
    def test_agent_sections(name=agent_name):
        path = PROJECT_ROOT / ".claude" / "agents" / f"{name}.md"
        content = path.read_text()
        required = ["Role", "Capabilities", "Workflow"]
        for section in required:
            assert f"# {section}" in content, f"Missing section: {section}"

    @test(f"Agent '{agent_name}' under 250 lines")
    def test_agent_lines(name=agent_name):
        path = PROJECT_ROOT / ".claude" / "agents" / f"{name}.md"
        content = path.read_text()
        lines = len(content.splitlines())
        assert lines < 250, f"Has {lines} lines (max 250)"

    @test(f"Agent '{agent_name}' has no emojis")
    def test_agent_no_emojis(name=agent_name):
        path = PROJECT_ROOT / ".claude" / "agents" / f"{name}.md"
        content = path.read_text()
        matches = EMOJI_PATTERN.findall(content)
        assert not matches, f"Found emojis: {matches}"


# Run agent tests
for name, obj in list(globals().items()):
    if name.startswith("test_agent") and callable(obj):
        obj()


# ============= AGENTS.MD TESTS =============

print("\n" + "="*60)
print("AGENTS.MD HIERARCHY TESTS")
print("="*60)

AGENTS_MD_LOCATIONS = [
    "AGENTS.md",
    "src/AGENTS.md",
    "src/fal_api/AGENTS.md",
    ".claude/AGENTS.md",
    "docs/AGENTS.md"
]

for loc in AGENTS_MD_LOCATIONS:
    @test(f"AGENTS.md exists at {loc}")
    def test_agents_md_exists(path=loc):
        full_path = PROJECT_ROOT / path
        assert full_path.exists(), f"AGENTS.md not found at {path}"

    @test(f"AGENTS.md at {loc} under 500 lines")
    def test_agents_md_lines(path=loc):
        full_path = PROJECT_ROOT / path
        if full_path.exists():
            content = full_path.read_text()
            lines = len(content.splitlines())
            assert lines < 500, f"Has {lines} lines (max 500)"

    @test(f"AGENTS.md at {loc} has no emojis")
    def test_agents_md_no_emojis(path=loc):
        full_path = PROJECT_ROOT / path
        if full_path.exists():
            content = full_path.read_text()
            matches = EMOJI_PATTERN.findall(content)
            assert not matches, f"Found emojis: {matches}"


# Run AGENTS.md tests
for name, obj in list(globals().items()):
    if name.startswith("test_agents_md") and callable(obj):
        obj()


# ============= INTEGRATION TESTS =============

print("\n" + "="*60)
print("INTEGRATION TESTS")
print("="*60)

@test("Root AGENTS.md has Golden Rules")
def test_golden_rules():
    content = (PROJECT_ROOT / "AGENTS.md").read_text()
    assert "Golden Rules" in content

@test("Root AGENTS.md has Context Map")
def test_context_map():
    content = (PROJECT_ROOT / "AGENTS.md").read_text()
    assert "Context Map" in content

@test(".claude/AGENTS.md lists skills")
def test_claude_lists_skills():
    content = (PROJECT_ROOT / ".claude" / "AGENTS.md").read_text()
    for skill in SKILLS:
        assert skill in content, f"Missing skill: {skill}"

@test(".claude/AGENTS.md lists subagents")
def test_claude_lists_agents():
    content = (PROJECT_ROOT / ".claude" / "AGENTS.md").read_text()
    agents = ["BatchProcessor", "LayerEditor", "CompositionEngine", "QualityChecker"]
    for agent in agents:
        assert agent in content, f"Missing agent: {agent}"

@test("CLAUDE.md exists")
def test_claude_md():
    assert (PROJECT_ROOT / ".claude" / "CLAUDE.md").exists()

@test("decompose.py exists")
def test_decompose_py():
    assert (PROJECT_ROOT / "src" / "fal_api" / "decompose.py").exists()

@test("export.py exists")
def test_export_py():
    assert (PROJECT_ROOT / "src" / "fal_api" / "export.py").exists()

@test("run_demo.py exists")
def test_run_demo_py():
    assert (PROJECT_ROOT / "src" / "fal_api" / "run_demo.py").exists()

@test(".env.example exists")
def test_env_example():
    assert (PROJECT_ROOT / ".env.example").exists()

@test(".env.example has FAL_KEY")
def test_env_example_fal_key():
    content = (PROJECT_ROOT / ".env.example").read_text()
    assert "FAL_KEY" in content

@test("requirements-fal.txt exists")
def test_requirements():
    assert (PROJECT_ROOT / "requirements-fal.txt").exists()

@test("README.md documents agent system")
def test_readme_agents():
    content = (PROJECT_ROOT / "README.md").read_text()
    assert "Agent" in content or "Skills" in content


# Run integration tests
test_golden_rules()
test_context_map()
test_claude_lists_skills()
test_claude_lists_agents()
test_claude_md()
test_decompose_py()
test_export_py()
test_run_demo_py()
test_env_example()
test_env_example_fal_key()
test_requirements()
test_readme_agents()


# ============= SUMMARY =============

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total:  {passed + failed}")
print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")

if errors:
    print("\n" + "-"*60)
    print("FAILURES:")
    print("-"*60)
    for name, msg in errors:
        print(f"  {name}: {msg}")

print("\n" + "="*60)
if failed == 0:
    print("ALL TESTS PASSED - TDD COMPLIANCE VERIFIED")
    sys.exit(0)
else:
    print(f"TDD COMPLIANCE FAILED - {failed} test(s) need attention")
    sys.exit(1)
