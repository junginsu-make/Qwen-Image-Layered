"""
TDD Unit tests for TemplateEngine SubAgent.

RED PHASE: These tests are written BEFORE implementation.
"""

import pytest
import re
from pathlib import Path


AGENTS_DIR = Path(__file__).parent.parent.parent / ".claude" / "agents"

VALID_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-haiku-3-5-20241022",
    "claude-opus-4-5-20251101"
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
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                items = value[1:-1].split(",")
                result[key] = [item.strip() for item in items]
            else:
                result[key] = value
    return result


class TestTemplateEngineExistence:
    """Test that TemplateEngine agent exists."""

    def test_agent_file_exists(self):
        """TemplateEngine agent file must exist."""
        agent_path = AGENTS_DIR / "template_engine.md"
        assert agent_path.exists(), "template_engine.md not found"


class TestTemplateEngineStructure:
    """Test TemplateEngine file structure."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "template_engine.md"
        return agent_path.read_text()

    @pytest.fixture
    def agent_frontmatter(self, agent_content):
        return parse_yaml_frontmatter(agent_content)

    def test_has_yaml_frontmatter(self, agent_content):
        """Agent must have YAML frontmatter."""
        assert agent_content.startswith("---"), "Missing YAML frontmatter"

    def test_has_required_frontmatter_fields(self, agent_frontmatter):
        """Frontmatter must have required fields."""
        assert "name" in agent_frontmatter, "Missing 'name'"
        assert "description" in agent_frontmatter, "Missing 'description'"
        assert "model" in agent_frontmatter, "Missing 'model'"
        assert "tools" in agent_frontmatter, "Missing 'tools'"

    def test_name_is_correct(self, agent_frontmatter):
        """Name must be TemplateEngine."""
        assert agent_frontmatter.get("name") == "TemplateEngine"

    def test_model_is_valid(self, agent_frontmatter):
        """Must use a valid model."""
        model = agent_frontmatter.get("model", "")
        assert model in VALID_MODELS, f"Invalid model: {model}"

    def test_has_required_sections(self, agent_content):
        """Agent must have all required sections."""
        required = ["Role", "Capabilities", "Workflow", "Error Handling"]
        for section in required:
            assert f"# {section}" in agent_content, f"Missing section: {section}"


class TestTemplateEngineCapabilities:
    """Test TemplateEngine specific capabilities."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "template_engine.md"
        return agent_path.read_text()

    def test_supports_template_loading(self, agent_content):
        """Must support loading templates."""
        content_lower = agent_content.lower()
        assert "template" in content_lower
        assert "load" in content_lower or "select" in content_lower

    def test_supports_layer_placement(self, agent_content):
        """Must support placing layers in template."""
        content_lower = agent_content.lower()
        assert "layer" in content_lower
        assert "place" in content_lower or "position" in content_lower or "slot" in content_lower

    def test_supports_multiple_template_types(self, agent_content):
        """Must support various template types."""
        content_lower = agent_content.lower()
        types = ["banner", "poster", "social", "card", "thumbnail"]
        found = sum(1 for t in types if t in content_lower)
        assert found >= 3, f"Only found {found}/5 template types"

    def test_has_template_customization(self, agent_content):
        """Must support template customization."""
        content_lower = agent_content.lower()
        custom = ["text", "font", "color", "size", "position"]
        found = sum(1 for c in custom if c in content_lower)
        assert found >= 3, f"Only found {found}/5 customization options"

    def test_has_output_formats(self, agent_content):
        """Must support multiple output formats."""
        content_lower = agent_content.lower()
        formats = ["png", "jpg", "jpeg", "webp", "pdf"]
        found = sum(1 for f in formats if f in content_lower)
        assert found >= 2, f"Only found {found}/5 output formats"


class TestTemplateEngineWorkflow:
    """Test TemplateEngine workflow definition."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "template_engine.md"
        return agent_path.read_text()

    def test_has_workflow_steps(self, agent_content):
        """Must have numbered workflow steps."""
        # Check for Step 1, Step 2, etc.
        has_steps = "Step 1" in agent_content or "## 1." in agent_content
        assert has_steps, "Missing workflow steps"

    def test_has_template_selection_step(self, agent_content):
        """Must have template selection step."""
        content_lower = agent_content.lower()
        has_selection = "select" in content_lower and "template" in content_lower
        assert has_selection, "Missing template selection step"

    def test_has_layer_mapping_step(self, agent_content):
        """Must have layer mapping step."""
        content_lower = agent_content.lower()
        has_mapping = "map" in content_lower or "assign" in content_lower or "slot" in content_lower
        assert has_mapping, "Missing layer mapping step"

    def test_has_render_step(self, agent_content):
        """Must have render/compose step."""
        content_lower = agent_content.lower()
        has_render = "render" in content_lower or "compose" in content_lower or "generate" in content_lower
        assert has_render, "Missing render step"


class TestTemplateEngineTemplates:
    """Test that predefined templates are defined."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "template_engine.md"
        return agent_path.read_text()

    def test_has_template_definitions(self, agent_content):
        """Must define template specifications."""
        # Should have dimensions or layout specs
        has_dimensions = "1080" in agent_content or "1920" in agent_content or "dimension" in agent_content.lower()
        assert has_dimensions, "Missing template dimension specifications"

    def test_has_slot_definitions(self, agent_content):
        """Must define slots for layer placement."""
        content_lower = agent_content.lower()
        assert "slot" in content_lower or "placeholder" in content_lower or "zone" in content_lower


class TestTemplateEngineOutput:
    """Test TemplateEngine output format."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "template_engine.md"
        return agent_path.read_text()

    def test_has_output_format_section(self, agent_content):
        """Must have output format section."""
        assert "Output" in agent_content

    def test_has_json_example(self, agent_content):
        """Must have JSON output example."""
        has_json = "```json" in agent_content or '{"' in agent_content
        assert has_json, "Missing JSON output example"


class TestTemplateEngineLineLimit:
    """Test that TemplateEngine respects line limit."""

    def test_agent_under_250_lines(self):
        """Agent should be under 250 lines."""
        agent_path = AGENTS_DIR / "template_engine.md"
        content = agent_path.read_text()
        line_count = len(content.splitlines())
        assert line_count < 250, f"Has {line_count} lines (max 250)"


class TestNoEmojisInTemplateEngine:
    """Test that TemplateEngine doesn't contain emojis."""

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

    def test_no_emojis(self):
        """Agent must not contain emojis."""
        agent_path = AGENTS_DIR / "template_engine.md"
        content = agent_path.read_text()
        matches = self.EMOJI_PATTERN.findall(content)
        assert not matches, f"Emojis found: {matches}"
