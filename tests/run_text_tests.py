#!/usr/bin/env python3
"""
Detailed tests for Text Processing Skills.
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

print("=" * 60)
print("TEXT SKILLS - OCR/EXTRACTION")
print("=" * 60)

# text-extract
skill = SKILLS_DIR / "text-extract" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-extract: name matches", fm.get("name") == "text-extract")
test("text-extract: has OCR", "ocr" in content.lower() or "optical" in content.lower())
test("text-extract: has language support", "language" in content.lower())
test("text-extract: Korean triggers", any(t in content for t in ["텍스트 추출", "글자 인식", "OCR"]))

# text-translate
skill = SKILLS_DIR / "text-translate" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-translate: name matches", fm.get("name") == "text-translate")
test("text-translate: has translation", "translat" in content.lower())
test("text-translate: source/target langs", "source" in content.lower() and "target" in content.lower())
test("text-translate: Korean triggers", any(t in content for t in ["번역", "변환"]))

print()
print("=" * 60)
print("TEXT SKILLS - LAYER EDITING")
print("=" * 60)

# text-overlay
skill = SKILLS_DIR / "text-overlay" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-overlay: name matches", fm.get("name") == "text-overlay")
test("text-overlay: has position params", any(t in content.lower() for t in ["position", "x", "y"]))
test("text-overlay: has font params", "font" in content.lower())
test("text-overlay: has color", "color" in content.lower())
test("text-overlay: Korean triggers", any(t in content for t in ["텍스트 추가", "워터마크", "캡션"]))

# text-effect
skill = SKILLS_DIR / "text-effect" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-effect: name matches", fm.get("name") == "text-effect")
effects = ["shadow", "glow", "outline", "neon", "3d", "gradient"]
found = sum(1 for e in effects if e in content.lower())
test("text-effect: has 3+ effects", found >= 3, f"Only {found} effects")
test("text-effect: has intensity/blur", "intensity" in content.lower() or "blur" in content.lower())
test("text-effect: Korean triggers", any(t in content for t in ["텍스트 효과", "그림자", "네온"]))

# text-to-path
skill = SKILLS_DIR / "text-to-path" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-to-path: name matches", fm.get("name") == "text-to-path")
paths = ["curve", "circle", "arc", "wave", "spiral"]
found = sum(1 for p in paths if p in content.lower())
test("text-to-path: has 2+ path types", found >= 2, f"Only {found} paths")
test("text-to-path: has text input", "text" in content.lower())
test("text-to-path: Korean triggers", any(t in content for t in ["곡선", "원형", "패스"]))

print()
print("=" * 60)
print("TEXT SKILLS - AI-BASED")
print("=" * 60)

# text-remove
skill = SKILLS_DIR / "text-remove" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-remove: name matches", fm.get("name") == "text-remove")
test("text-remove: has removal", any(t in content.lower() for t in ["remove", "erase", "delete"]))
test("text-remove: has inpainting", any(t in content.lower() for t in ["inpaint", "fill", "restore"]))
test("text-remove: uses API", any(t in content.lower() for t in ["fal", "api", "ai"]))
test("text-remove: Korean triggers", any(t in content for t in ["텍스트 제거", "글자 지우기"]))

# text-replace
skill = SKILLS_DIR / "text-replace" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("text-replace: name matches", fm.get("name") == "text-replace")
test("text-replace: has replace", any(t in content.lower() for t in ["replace", "swap", "change"]))
test("text-replace: has old/new params", ("old" in content.lower() or "original" in content.lower()) and ("new" in content.lower() or "replacement" in content.lower()))
test("text-replace: Korean triggers", any(t in content for t in ["텍스트 교체", "바꾸기", "변경"]))

# font-match
skill = SKILLS_DIR / "font-match" / "SKILL.md"
content = skill.read_text()
fm = parse_yaml_frontmatter(content)
test("font-match: name matches", fm.get("name") == "font-match")
test("font-match: has detection", any(t in content.lower() for t in ["detect", "identify", "match", "recognize"]))
info_terms = ["name", "family", "style", "weight", "similar"]
found = sum(1 for t in info_terms if t in content.lower())
test("font-match: has font info output", found >= 2, f"Only {found} terms")
test("font-match: Korean triggers", any(t in content for t in ["폰트 찾기", "글꼴", "서체"]))

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
    print("ALL TEXT SKILL TESTS PASSED")
    sys.exit(0)
