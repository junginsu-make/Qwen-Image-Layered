"""
Unit tests for Claude Code Skills.
Tests skill definition structure, trigger keywords, and validation rules.
"""

import pytest
import yaml
import re
from pathlib import Path


SKILLS_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills"

EXPECTED_SKILLS = [
    "image-decompose",
    "layer-export",
    "quick-edit",
    "background-remove"
]

REQUIRED_SECTIONS = [
    "Triggers",
    "Inputs",
    "Outputs",
    "Execution",
    "Validation",
    "Error Handling"
]


class TestSkillsExistence:
    """Test that all expected skills exist."""

    def test_skills_directory_exists(self):
        """Skills directory must exist."""
        assert SKILLS_DIR.exists(), f"Skills directory not found: {SKILLS_DIR}"

    @pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
    def test_skill_exists(self, skill_name):
        """Each expected skill must have a SKILL.md file."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Skill not found: {skill_name}"


class TestSkillStructure:
    """Test skill file structure and frontmatter."""

    @pytest.fixture
    def skill_content(self, request):
        """Load skill content."""
        skill_name = request.param
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        return skill_path.read_text()

    @pytest.mark.parametrize("skill_content", EXPECTED_SKILLS, indirect=True)
    def test_has_yaml_frontmatter(self, skill_content):
        """Skill must have YAML frontmatter."""
        assert skill_content.startswith("---"), "Missing YAML frontmatter"
        # Find closing ---
        second_dash = skill_content.find("---", 3)
        assert second_dash > 3, "Invalid YAML frontmatter structure"

    @pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
    def test_frontmatter_has_required_fields(self, skill_name):
        """Frontmatter must have name and description."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()

        # Extract frontmatter
        start = content.find("---") + 3
        end = content.find("---", start)
        frontmatter = content[start:end].strip()

        # Parse YAML
        parsed = yaml.safe_load(frontmatter)

        assert "name" in parsed, f"Missing 'name' in {skill_name}"
        assert "description" in parsed, f"Missing 'description' in {skill_name}"
        assert parsed["name"] == skill_name, f"Name mismatch in {skill_name}"

    @pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
    def test_has_required_sections(self, skill_name):
        """Skill must have all required sections."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()

        for section in REQUIRED_SECTIONS:
            assert f"# {section}" in content, f"Missing section '{section}' in {skill_name}"


class TestImageDecomposeSkill:
    """Specific tests for image-decompose skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "image-decompose" / "SKILL.md"
        return skill_path.read_text()

    def test_has_english_triggers(self, skill_content):
        """Must have English trigger keywords."""
        assert "decompose" in skill_content.lower()
        assert "layer" in skill_content.lower()

    def test_has_korean_triggers(self, skill_content):
        """Must have Korean trigger keywords."""
        assert "분해" in skill_content
        assert "레이어" in skill_content

    def test_has_layer_count_input(self, skill_content):
        """Must accept num_layers parameter."""
        assert "num_layers" in skill_content
        assert "2-10" in skill_content or "2 to 10" in skill_content.lower()

    def test_execution_uses_run_demo(self, skill_content):
        """Execution must use run_demo.py."""
        assert "run_demo.py" in skill_content
        assert "--image" in skill_content
        assert "--layers" in skill_content


class TestLayerExportSkill:
    """Specific tests for layer-export skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "layer-export" / "SKILL.md"
        return skill_path.read_text()

    def test_supports_multiple_formats(self, skill_content):
        """Must support PPTX, PSD, ZIP formats."""
        assert "pptx" in skill_content.lower()
        assert "psd" in skill_content.lower()
        assert "zip" in skill_content.lower()

    def test_has_export_triggers(self, skill_content):
        """Must have export-related triggers."""
        assert "export" in skill_content.lower()
        assert "save" in skill_content.lower() or "내보내기" in skill_content


class TestQuickEditSkill:
    """Specific tests for quick-edit skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "quick-edit" / "SKILL.md"
        return skill_path.read_text()

    def test_supports_transform_operations(self, skill_content):
        """Must support resize, rotate, flip."""
        content_lower = skill_content.lower()
        assert "resize" in content_lower
        assert "rotate" in content_lower
        assert "flip" in content_lower

    def test_supports_color_operations(self, skill_content):
        """Must support color adjustments."""
        content_lower = skill_content.lower()
        has_color = any(op in content_lower for op in ["color", "brightness", "contrast", "saturation", "hue"])
        assert has_color, "Missing color adjustment operations"


class TestBackgroundRemoveSkill:
    """Specific tests for background-remove skill."""

    @pytest.fixture
    def skill_content(self):
        skill_path = SKILLS_DIR / "background-remove" / "SKILL.md"
        return skill_path.read_text()

    def test_uses_two_layers(self, skill_content):
        """Background remove should use 2 layers."""
        assert "2" in skill_content
        # Should mention foreground and background
        content_lower = skill_content.lower()
        assert "foreground" in content_lower or "background" in content_lower

    def test_has_remove_triggers(self, skill_content):
        """Must have remove/separate triggers."""
        content_lower = skill_content.lower()
        has_trigger = any(t in content_lower for t in ["remove", "separate", "누끼", "배경"])
        assert has_trigger, "Missing background removal triggers"


class TestSkillLineLimit:
    """Test that skills respect line limits."""

    @pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
    def test_skill_under_200_lines(self, skill_name):
        """Skills should be concise (under 200 lines)."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        line_count = len(content.splitlines())
        assert line_count < 200, f"{skill_name} has {line_count} lines (max 200)"


class TestNoEmojisInSkills:
    """Test that skills don't contain emojis."""

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
        "\U00002600-\U000026FF"  # misc symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+",
        flags=re.UNICODE
    )

    @pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
    def test_no_emojis(self, skill_name):
        """Skills must not contain emojis."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        matches = self.EMOJI_PATTERN.findall(content)
        assert not matches, f"Emojis found in {skill_name}: {matches}"
