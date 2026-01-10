"""
TDD Unit tests for new Skills (Phase 2 expansion).
Tests: smart-upscale, style-transfer, color-palette, text-to-layer

RED PHASE: These tests are written BEFORE implementation.
"""

import pytest
import re
from pathlib import Path


SKILLS_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills"

NEW_SKILLS = [
    "smart-upscale",
    "style-transfer",
    "color-palette",
    "text-to-layer"
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


class TestNewSkillsExistence:
    """Test that all new skills exist."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_directory_exists(self, skill_name):
        """Each skill must have its own directory."""
        skill_dir = SKILLS_DIR / skill_name
        assert skill_dir.exists(), f"Skill directory not found: {skill_name}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_file_exists(self, skill_name):
        """Each skill must have a SKILL.md file."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md not found for {skill_name}"


class TestNewSkillsStructure:
    """Test new skill file structure."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_has_yaml_frontmatter(self, skill_name):
        """Skill must have YAML frontmatter."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        assert content.startswith("---"), f"Missing YAML frontmatter in {skill_name}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_fields(self, skill_name):
        """Frontmatter must have name and description."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        fm = parse_yaml_frontmatter(content)
        assert "name" in fm, f"Missing 'name' in {skill_name}"
        assert "description" in fm, f"Missing 'description' in {skill_name}"
        assert fm["name"] == skill_name, f"Name mismatch in {skill_name}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_has_required_sections(self, skill_name):
        """Skill must have all required sections."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        for section in REQUIRED_SECTIONS:
            assert f"# {section}" in content, f"Missing '{section}' in {skill_name}"


class TestSmartUpscaleSkill:
    """Specific tests for smart-upscale skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "smart-upscale" / "SKILL.md"
        return skill_path.read_text()

    def test_has_scale_factor_input(self, skill_content):
        """Must accept scale factor parameter."""
        assert "scale" in skill_content.lower()
        # Should support 2x, 4x scaling
        has_factors = "2x" in skill_content or "4x" in skill_content or "scale_factor" in skill_content
        assert has_factors, "Missing scale factor options"

    def test_has_upscale_triggers(self, skill_content):
        """Must have upscale-related triggers."""
        content_lower = skill_content.lower()
        triggers = ["upscale", "enlarge", "enhance", "resolution"]
        found = sum(1 for t in triggers if t in content_lower)
        assert found >= 2, "Missing upscale triggers"

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean_triggers = ["확대", "업스케일", "해상도", "고화질"]
        found = sum(1 for t in korean_triggers if t in skill_content)
        assert found >= 1, "Missing Korean triggers"

    def test_uses_fal_api(self, skill_content):
        """Should use Fal AI upscaler."""
        assert "fal" in skill_content.lower() or "api" in skill_content.lower()


class TestStyleTransferSkill:
    """Specific tests for style-transfer skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "style-transfer" / "SKILL.md"
        return skill_path.read_text()

    def test_has_style_options(self, skill_content):
        """Must support multiple style options."""
        content_lower = skill_content.lower()
        styles = ["watercolor", "oil", "sketch", "cartoon", "anime"]
        found = sum(1 for s in styles if s in content_lower)
        assert found >= 3, f"Only found {found}/5 style options"

    def test_has_style_triggers(self, skill_content):
        """Must have style-related triggers."""
        content_lower = skill_content.lower()
        assert "style" in content_lower
        assert "transfer" in content_lower or "transform" in content_lower

    def test_has_layer_support(self, skill_content):
        """Should support applying to specific layers."""
        assert "layer" in skill_content.lower()

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean_triggers = ["스타일", "변환", "수채화", "유화"]
        found = sum(1 for t in korean_triggers if t in skill_content)
        assert found >= 1, "Missing Korean triggers"


class TestColorPaletteSkill:
    """Specific tests for color-palette skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "color-palette" / "SKILL.md"
        return skill_path.read_text()

    def test_has_palette_extraction(self, skill_content):
        """Must support palette extraction."""
        content_lower = skill_content.lower()
        assert "palette" in content_lower or "color" in content_lower
        assert "extract" in content_lower or "analyze" in content_lower

    def test_has_color_count_input(self, skill_content):
        """Must accept number of colors parameter."""
        has_count = "num_colors" in skill_content or "color_count" in skill_content or "colors" in skill_content.lower()
        assert has_count, "Missing color count parameter"

    def test_outputs_hex_codes(self, skill_content):
        """Should output hex color codes."""
        content_lower = skill_content.lower()
        assert "hex" in content_lower or "#" in skill_content

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean_triggers = ["색상", "팔레트", "컬러", "추출"]
        found = sum(1 for t in korean_triggers if t in skill_content)
        assert found >= 1, "Missing Korean triggers"


class TestTextToLayerSkill:
    """Specific tests for text-to-layer skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "text-to-layer" / "SKILL.md"
        return skill_path.read_text()

    def test_has_prompt_input(self, skill_content):
        """Must accept text prompt parameter."""
        content_lower = skill_content.lower()
        assert "prompt" in content_lower or "text" in content_lower

    def test_outputs_rgba_layer(self, skill_content):
        """Must output RGBA layer with transparency."""
        content_lower = skill_content.lower()
        assert "rgba" in content_lower or "alpha" in content_lower or "transparent" in content_lower

    def test_has_generation_triggers(self, skill_content):
        """Must have generation-related triggers."""
        content_lower = skill_content.lower()
        triggers = ["generate", "create", "make", "add layer"]
        found = sum(1 for t in triggers if t in content_lower)
        assert found >= 2, "Missing generation triggers"

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean triggers."""
        korean_triggers = ["생성", "레이어 추가", "만들어", "그려"]
        found = sum(1 for t in korean_triggers if t in skill_content)
        assert found >= 1, "Missing Korean triggers"

    def test_uses_image_generation_api(self, skill_content):
        """Should use image generation API."""
        content_lower = skill_content.lower()
        has_api = "fal" in content_lower or "flux" in content_lower or "stable" in content_lower
        assert has_api, "Missing image generation API reference"


class TestNewSkillsLineLimit:
    """Test that new skills respect line limits."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_under_150_lines(self, skill_name):
        """Skills should be concise (under 150 lines)."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        line_count = len(content.splitlines())
        assert line_count < 150, f"{skill_name} has {line_count} lines (max 150)"


class TestNoEmojisInNewSkills:
    """Test that new skills don't contain emojis."""

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

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_no_emojis(self, skill_name):
        """Skills must not contain emojis."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        matches = self.EMOJI_PATTERN.findall(content)
        assert not matches, f"Emojis found in {skill_name}: {matches}"
