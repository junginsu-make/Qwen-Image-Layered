"""
TDD Unit tests for Text Skills (Phase 3 expansion).

Skills:
- OCR/Extraction: text-extract, text-translate
- Layer Editing: text-overlay, text-effect, text-to-path
- AI-based: text-remove, text-replace, font-match

RED PHASE: These tests are written BEFORE implementation.
"""

import pytest
import re
from pathlib import Path


SKILLS_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills"

TEXT_SKILLS = [
    # OCR/Extraction
    "text-extract",
    "text-translate",
    # Layer Editing
    "text-overlay",
    "text-effect",
    "text-to-path",
    # AI-based
    "text-remove",
    "text-replace",
    "font-match"
]

REQUIRED_SECTIONS = [
    "Triggers",
    "Inputs",
    "Outputs",
    "Execution",
    "Validation",
    "Error Handling"
]


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
            result[key.strip()] = value.strip()
    return result


class TestTextSkillsExistence:
    """Test that all text skills exist."""

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_skill_directory_exists(self, skill_name):
        """Each skill must have its own directory."""
        skill_dir = SKILLS_DIR / skill_name
        assert skill_dir.exists(), f"Skill directory not found: {skill_name}"

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_skill_file_exists(self, skill_name):
        """Each skill must have a SKILL.md file."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md not found for {skill_name}"


class TestTextSkillsStructure:
    """Test text skill file structure."""

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_has_yaml_frontmatter(self, skill_name):
        """Skill must have YAML frontmatter."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        assert content.startswith("---"), f"Missing YAML frontmatter in {skill_name}"

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_frontmatter_fields(self, skill_name):
        """Frontmatter must have name and description."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        fm = parse_yaml_frontmatter(content)
        assert "name" in fm, f"Missing 'name' in {skill_name}"
        assert "description" in fm, f"Missing 'description' in {skill_name}"
        assert fm["name"] == skill_name, f"Name mismatch in {skill_name}"

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_has_required_sections(self, skill_name):
        """Skill must have all required sections."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        for section in REQUIRED_SECTIONS:
            assert f"# {section}" in content, f"Missing '{section}' in {skill_name}"


# ============= OCR/EXTRACTION SKILLS =============

class TestTextExtractSkill:
    """Tests for text-extract (OCR) skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-extract" / "SKILL.md"
        return skill_path.read_text()

    def test_has_ocr_capability(self, skill_content):
        """Must mention OCR capability."""
        content_lower = skill_content.lower()
        assert "ocr" in content_lower or "optical" in content_lower

    def test_has_language_support(self, skill_content):
        """Must support multiple languages."""
        content_lower = skill_content.lower()
        has_lang = "language" in content_lower or "lang" in content_lower
        assert has_lang, "Missing language support"

    def test_outputs_text(self, skill_content):
        """Must output extracted text."""
        content_lower = skill_content.lower()
        assert "text" in content_lower and ("output" in content_lower or "return" in content_lower)

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["텍스트 추출", "OCR", "글자 인식", "문자 추출"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


class TestTextTranslateSkill:
    """Tests for text-translate skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-translate" / "SKILL.md"
        return skill_path.read_text()

    def test_has_translation_capability(self, skill_content):
        """Must have translation capability."""
        content_lower = skill_content.lower()
        assert "translat" in content_lower

    def test_has_source_target_languages(self, skill_content):
        """Must support source and target languages."""
        content_lower = skill_content.lower()
        has_source = "source" in content_lower or "from" in content_lower
        has_target = "target" in content_lower or "to" in content_lower
        assert has_source and has_target, "Missing source/target language params"

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["번역", "translate", "변환"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


# ============= TEXT LAYER EDITING SKILLS =============

class TestTextOverlaySkill:
    """Tests for text-overlay skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-overlay" / "SKILL.md"
        return skill_path.read_text()

    def test_has_text_input(self, skill_content):
        """Must accept text content input."""
        content_lower = skill_content.lower()
        assert "text" in content_lower

    def test_has_position_params(self, skill_content):
        """Must have position parameters."""
        content_lower = skill_content.lower()
        pos_terms = ["position", "x", "y", "location", "place"]
        assert any(t in content_lower for t in pos_terms), "Missing position params"

    def test_has_font_params(self, skill_content):
        """Must have font customization."""
        content_lower = skill_content.lower()
        assert "font" in content_lower

    def test_has_color_params(self, skill_content):
        """Must have color parameter."""
        content_lower = skill_content.lower()
        assert "color" in content_lower

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["텍스트 추가", "글자 넣기", "워터마크", "캡션"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


class TestTextEffectSkill:
    """Tests for text-effect skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-effect" / "SKILL.md"
        return skill_path.read_text()

    def test_has_effect_types(self, skill_content):
        """Must support multiple effect types."""
        content_lower = skill_content.lower()
        effects = ["shadow", "glow", "outline", "neon", "3d", "gradient"]
        found = sum(1 for e in effects if e in content_lower)
        assert found >= 3, f"Only {found}/6 effects found"

    def test_has_effect_params(self, skill_content):
        """Must have effect customization params."""
        content_lower = skill_content.lower()
        params = ["intensity", "size", "color", "opacity", "blur"]
        found = sum(1 for p in params if p in content_lower)
        assert found >= 2, f"Only {found}/5 params found"

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["텍스트 효과", "그림자", "네온", "효과 적용"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


class TestTextToPathSkill:
    """Tests for text-to-path skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-to-path" / "SKILL.md"
        return skill_path.read_text()

    def test_has_path_types(self, skill_content):
        """Must support different path types."""
        content_lower = skill_content.lower()
        paths = ["curve", "circle", "arc", "wave", "spiral", "custom"]
        found = sum(1 for p in paths if p in content_lower)
        assert found >= 2, f"Only {found}/6 path types found"

    def test_has_text_input(self, skill_content):
        """Must accept text input."""
        assert "text" in skill_content.lower()

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["곡선 텍스트", "원형 텍스트", "패스", "경로"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


# ============= AI-BASED TEXT SKILLS =============

class TestTextRemoveSkill:
    """Tests for text-remove (inpainting) skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-remove" / "SKILL.md"
        return skill_path.read_text()

    def test_has_removal_capability(self, skill_content):
        """Must have text removal capability."""
        content_lower = skill_content.lower()
        assert "remove" in content_lower or "erase" in content_lower or "delete" in content_lower

    def test_has_inpainting(self, skill_content):
        """Should use inpainting technique."""
        content_lower = skill_content.lower()
        assert "inpaint" in content_lower or "fill" in content_lower or "restore" in content_lower

    def test_uses_ai_api(self, skill_content):
        """Should use AI API."""
        content_lower = skill_content.lower()
        assert "fal" in content_lower or "api" in content_lower or "ai" in content_lower

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["텍스트 제거", "글자 지우기", "문자 삭제"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


class TestTextReplaceSkill:
    """Tests for text-replace skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-replace" / "SKILL.md"
        return skill_path.read_text()

    def test_has_replace_capability(self, skill_content):
        """Must have text replacement capability."""
        content_lower = skill_content.lower()
        assert "replace" in content_lower or "swap" in content_lower or "change" in content_lower

    def test_has_old_new_text_params(self, skill_content):
        """Must have old and new text parameters."""
        content_lower = skill_content.lower()
        has_old = "old" in content_lower or "original" in content_lower or "source" in content_lower
        has_new = "new" in content_lower or "replacement" in content_lower or "target" in content_lower
        assert has_old and has_new, "Missing old/new text params"

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["텍스트 교체", "글자 바꾸기", "문자 변경"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


class TestFontMatchSkill:
    """Tests for font-match skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "font-match" / "SKILL.md"
        return skill_path.read_text()

    def test_has_font_detection(self, skill_content):
        """Must detect fonts."""
        content_lower = skill_content.lower()
        assert "font" in content_lower
        assert "detect" in content_lower or "identify" in content_lower or "match" in content_lower

    def test_outputs_font_info(self, skill_content):
        """Must output font information."""
        content_lower = skill_content.lower()
        info_terms = ["name", "family", "style", "weight", "similar"]
        found = sum(1 for t in info_terms if t in content_lower)
        assert found >= 2, f"Only {found}/5 font info terms found"

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean = ["폰트 찾기", "글꼴 인식", "폰트 매칭", "서체"]
        assert any(t in skill_content for t in korean), "Missing Korean triggers"


# ============= LINE LIMIT AND EMOJI TESTS =============

class TestTextSkillsLineLimit:
    """Test that text skills respect line limits."""

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_skill_under_150_lines(self, skill_name):
        """Skills should be concise (under 150 lines)."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        line_count = len(content.splitlines())
        assert line_count < 150, f"{skill_name} has {line_count} lines (max 150)"


class TestNoEmojisInTextSkills:
    """Test that text skills don't contain emojis."""

    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U00002700-\U000027BF"
        "]+",
        flags=re.UNICODE
    )

    @pytest.mark.parametrize("skill_name", TEXT_SKILLS)
    def test_no_emojis(self, skill_name):
        """Skills must not contain emojis."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        matches = self.EMOJI_PATTERN.findall(content)
        assert not matches, f"Emojis found in {skill_name}: {matches}"
