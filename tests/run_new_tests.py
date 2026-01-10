#!/usr/bin/env python3
"""
Detailed tests for new skills and TemplateEngine agent.
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


print("=" * 60)
print("NEW SKILLS DETAILED TESTS")
print("=" * 60)

# Test smart-upscale
skill = PROJECT_ROOT / ".claude/skills/smart-upscale/SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("smart-upscale: name matches", fm.get("name") == "smart-upscale", "Name mismatch")
test("smart-upscale: has scale factor", "scale" in content.lower(), "Missing scale")
test("smart-upscale: has 2x/4x", "2x" in content or "4x" in content or "scale_factor" in content, "Missing factors")
test("smart-upscale: Korean triggers", any(t in content for t in ["업스케일", "확대", "해상도"]), "Missing Korean")

# Test style-transfer
skill = PROJECT_ROOT / ".claude/skills/style-transfer/SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("style-transfer: name matches", fm.get("name") == "style-transfer", "Name mismatch")
styles = ["watercolor", "oil", "sketch", "cartoon", "anime"]
found = sum(1 for s in styles if s in content.lower())
test("style-transfer: has 3+ styles", found >= 3, f"Only {found} styles")
test("style-transfer: Korean triggers", any(t in content for t in ["스타일", "수채화", "유화"]), "Missing Korean")

# Test color-palette
skill = PROJECT_ROOT / ".claude/skills/color-palette/SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("color-palette: name matches", fm.get("name") == "color-palette", "Name mismatch")
test("color-palette: has hex", "hex" in content.lower() or "#" in content, "Missing hex")
test("color-palette: has extract", "extract" in content.lower() or "analyze" in content.lower(), "Missing extract")
test("color-palette: Korean triggers", any(t in content for t in ["색상", "팔레트", "컬러"]), "Missing Korean")

# Test text-to-layer
skill = PROJECT_ROOT / ".claude/skills/text-to-layer/SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-to-layer: name matches", fm.get("name") == "text-to-layer", "Name mismatch")
test("text-to-layer: has prompt", "prompt" in content.lower(), "Missing prompt")
test("text-to-layer: RGBA/alpha", any(t in content.lower() for t in ["rgba", "alpha", "transparent"]), "Missing transparency")
test("text-to-layer: generation API", any(t in content.lower() for t in ["fal", "flux", "stable"]), "Missing API")
test("text-to-layer: Korean triggers", any(t in content for t in ["생성", "레이어 추가", "만들어"]), "Missing Korean")

print()
print("=" * 60)
print("TEMPLATE ENGINE DETAILED TESTS")
print("=" * 60)

agent = PROJECT_ROOT / ".claude/agents/template_engine.md"
content = agent.read_text()
fm = parse_yaml_frontmatter(content)

test("TemplateEngine: name matches", fm.get("name") == "TemplateEngine", f"Got: {fm.get('name')}")
test("TemplateEngine: has model", "model" in fm, "Missing model")
test("TemplateEngine: template loading", "template" in content.lower() and ("load" in content.lower() or "select" in content.lower()), "Missing template loading")
test("TemplateEngine: layer placement", "layer" in content.lower() and any(t in content.lower() for t in ["place", "position", "slot"]), "Missing placement")
types = ["banner", "poster", "social", "card", "thumbnail"]
found = sum(1 for t in types if t in content.lower())
test("TemplateEngine: 3+ template types", found >= 3, f"Only {found} types")
test("TemplateEngine: dimensions", "1080" in content or "1920" in content or "dimension" in content.lower(), "Missing dimensions")
test("TemplateEngine: slots defined", "slot" in content.lower() or "placeholder" in content.lower(), "Missing slots")
test("TemplateEngine: render step", any(t in content.lower() for t in ["render", "compose", "generate"]), "Missing render")
test("TemplateEngine: JSON output", "```json" in content or '{"' in content, "Missing JSON")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")

if errors:
    print()
    print("FAILURES:")
    for name, msg in errors:
        print(f"  {name}: {msg}")
    sys.exit(1)
else:
    print()
    print("ALL NEW COMPONENT TESTS PASSED")
    sys.exit(0)
