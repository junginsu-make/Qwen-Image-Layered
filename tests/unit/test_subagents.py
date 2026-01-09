"""
Unit tests for Claude Code SubAgents.
Tests agent definition structure, capabilities, and workflow definitions.
"""

import pytest
import yaml
import re
from pathlib import Path


AGENTS_DIR = Path(__file__).parent.parent.parent / ".claude" / "agents"

EXPECTED_AGENTS = [
    "batch_processor",
    "layer_editor",
    "composition_engine",
    "quality_checker"
]

REQUIRED_SECTIONS = [
    "Role",
    "Capabilities",
    "Workflow",
    "Error Handling"
]

VALID_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-haiku-3-5-20241022",
    "claude-opus-4-5-20251101"
]


class TestAgentsExistence:
    """Test that all expected agents exist."""

    def test_agents_directory_exists(self):
        """Agents directory must exist."""
        assert AGENTS_DIR.exists(), f"Agents directory not found: {AGENTS_DIR}"

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_agent_exists(self, agent_name):
        """Each expected agent must have a .md file."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        assert agent_path.exists(), f"Agent not found: {agent_name}"


class TestAgentStructure:
    """Test agent file structure and frontmatter."""

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_has_yaml_frontmatter(self, agent_name):
        """Agent must have YAML frontmatter."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()
        assert content.startswith("---"), f"Missing YAML frontmatter in {agent_name}"
        second_dash = content.find("---", 3)
        assert second_dash > 3, f"Invalid YAML frontmatter in {agent_name}"

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_frontmatter_has_required_fields(self, agent_name):
        """Frontmatter must have name, description, model, and tools."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()

        # Extract frontmatter
        start = content.find("---") + 3
        end = content.find("---", start)
        frontmatter = content[start:end].strip()
        parsed = yaml.safe_load(frontmatter)

        assert "name" in parsed, f"Missing 'name' in {agent_name}"
        assert "description" in parsed, f"Missing 'description' in {agent_name}"
        assert "model" in parsed, f"Missing 'model' in {agent_name}"
        assert "tools" in parsed, f"Missing 'tools' in {agent_name}"

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_model_is_valid(self, agent_name):
        """Agent must use a valid model."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()

        start = content.find("---") + 3
        end = content.find("---", start)
        frontmatter = content[start:end].strip()
        parsed = yaml.safe_load(frontmatter)

        model = parsed.get("model", "")
        assert model in VALID_MODELS, f"Invalid model '{model}' in {agent_name}"

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_has_required_sections(self, agent_name):
        """Agent must have all required sections."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()

        for section in REQUIRED_SECTIONS:
            assert f"# {section}" in content, f"Missing section '{section}' in {agent_name}"


class TestBatchProcessorAgent:
    """Specific tests for BatchProcessor agent."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "batch_processor.md"
        return agent_path.read_text()

    def test_has_collect_images_step(self, agent_content):
        """Must have image collection step."""
        assert "collect" in agent_content.lower() or "Collect" in agent_content

    def test_has_progress_tracking(self, agent_content):
        """Must support progress tracking."""
        assert "progress" in agent_content.lower()

    def test_has_report_generation(self, agent_content):
        """Must generate reports."""
        assert "report" in agent_content.lower()

    def test_defines_failure_handling(self, agent_content):
        """Must define retry and failure strategies."""
        content_lower = agent_content.lower()
        has_retry = "retry" in content_lower
        has_failure = "failure" in content_lower or "failed" in content_lower
        assert has_retry and has_failure, "Missing retry/failure handling"


class TestLayerEditorAgent:
    """Specific tests for LayerEditor agent."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "layer_editor.md"
        return agent_path.read_text()

    def test_supports_transform_operations(self, agent_content):
        """Must support resize, rotate, flip, crop."""
        content_lower = agent_content.lower()
        operations = ["resize", "rotate", "flip", "crop"]
        for op in operations:
            assert op in content_lower, f"Missing operation: {op}"

    def test_supports_undo_redo(self, agent_content):
        """Must support undo/redo."""
        content_lower = agent_content.lower()
        assert "undo" in content_lower
        assert "redo" in content_lower

    def test_has_edit_session(self, agent_content):
        """Must have edit session concept."""
        assert "session" in agent_content.lower() or "Session" in agent_content


class TestCompositionEngineAgent:
    """Specific tests for CompositionEngine agent."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "composition_engine.md"
        return agent_path.read_text()

    def test_supports_blend_modes(self, agent_content):
        """Must support blend modes."""
        content_lower = agent_content.lower()
        assert "blend" in content_lower
        # Check for specific blend modes
        has_blend_modes = any(mode in content_lower for mode in ["normal", "multiply", "screen", "overlay"])
        assert has_blend_modes, "Missing blend mode definitions"

    def test_supports_layouts(self, agent_content):
        """Must support layout templates."""
        content_lower = agent_content.lower()
        assert "layout" in content_lower
        # Check for specific layouts
        has_layouts = any(layout in content_lower for layout in ["grid", "stack", "feature"])
        assert has_layouts, "Missing layout templates"

    def test_can_create_moodboards(self, agent_content):
        """Must support moodboard creation."""
        content_lower = agent_content.lower()
        has_composition = any(term in content_lower for term in ["moodboard", "collage", "composition"])
        assert has_composition, "Missing moodboard/collage capability"


class TestQualityCheckerAgent:
    """Specific tests for QualityChecker agent."""

    @pytest.fixture
    def agent_content(self):
        agent_path = AGENTS_DIR / "quality_checker.md"
        return agent_path.read_text()

    def test_has_quality_criteria(self, agent_content):
        """Must define quality criteria."""
        content_lower = agent_content.lower()
        # Check for quality dimensions
        dimensions = ["completeness", "transparency", "edge", "color"]
        found = sum(1 for d in dimensions if d in content_lower)
        assert found >= 3, f"Only found {found}/4 quality dimensions"

    def test_has_scoring_system(self, agent_content):
        """Must have scoring system."""
        content_lower = agent_content.lower()
        assert "score" in content_lower
        # Check for score ranges
        has_thresholds = any(threshold in agent_content for threshold in ["90", "70", "50"])
        assert has_thresholds, "Missing score thresholds"

    def test_generates_recommendations(self, agent_content):
        """Must generate recommendations."""
        content_lower = agent_content.lower()
        assert "recommend" in content_lower


class TestAgentToolsValidity:
    """Test that agents request valid tools."""

    VALID_TOOLS = [
        "execute",
        "read",
        "write",
        "glob",
        "grep",
        "bash",
        "web_fetch"
    ]

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_tools_are_valid(self, agent_name):
        """Agent tools must be from valid set."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()

        start = content.find("---") + 3
        end = content.find("---", start)
        frontmatter = content[start:end].strip()
        parsed = yaml.safe_load(frontmatter)

        tools = parsed.get("tools", [])
        for tool in tools:
            assert tool in self.VALID_TOOLS, f"Invalid tool '{tool}' in {agent_name}"


class TestAgentLineLimit:
    """Test that agents respect line limits."""

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_agent_under_250_lines(self, agent_name):
        """Agents should be focused (under 250 lines)."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()
        line_count = len(content.splitlines())
        assert line_count < 250, f"{agent_name} has {line_count} lines (max 250)"


class TestAgentOutputFormat:
    """Test that agents define output format."""

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_has_output_format(self, agent_name):
        """Agent must define output format."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()
        assert "Output Format" in content or "Output" in content, f"Missing output format in {agent_name}"

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_has_json_example(self, agent_name):
        """Agent should have JSON output example."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()
        has_json = "```json" in content or '{"' in content
        assert has_json, f"Missing JSON output example in {agent_name}"


class TestNoEmojisInAgents:
    """Test that agents don't contain emojis."""

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

    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_no_emojis(self, agent_name):
        """Agents must not contain emojis."""
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        content = agent_path.read_text()
        matches = self.EMOJI_PATTERN.findall(content)
        assert not matches, f"Emojis found in {agent_name}: {matches}"
