"""
Integration tests for the Claude Code Agent System.
Tests AGENTS.md hierarchy, skill-agent coordination, and system integrity.
"""

import pytest
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent

AGENTS_MD_LOCATIONS = [
    PROJECT_ROOT / "AGENTS.md",
    PROJECT_ROOT / "src" / "AGENTS.md",
    PROJECT_ROOT / "src" / "fal_api" / "AGENTS.md",
    PROJECT_ROOT / ".claude" / "AGENTS.md",
    PROJECT_ROOT / "docs" / "AGENTS.md"
]


class TestAgentsMdHierarchy:
    """Test AGENTS.md file hierarchy and cross-references."""

    def test_root_agents_md_exists(self):
        """Root AGENTS.md must exist."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        assert root_agents.exists(), "Root AGENTS.md not found"

    @pytest.mark.parametrize("agents_path", AGENTS_MD_LOCATIONS)
    def test_agents_md_exists(self, agents_path):
        """All expected AGENTS.md files must exist."""
        assert agents_path.exists(), f"AGENTS.md not found at {agents_path}"

    @pytest.mark.parametrize("agents_path", AGENTS_MD_LOCATIONS)
    def test_agents_md_under_500_lines(self, agents_path):
        """AGENTS.md files must be under 500 lines."""
        content = agents_path.read_text()
        line_count = len(content.splitlines())
        assert line_count < 500, f"{agents_path.name} has {line_count} lines (max 500)"

    def test_root_has_context_map(self):
        """Root AGENTS.md must have Context Map."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        content = root_agents.read_text()
        assert "Context Map" in content, "Root AGENTS.md missing Context Map"

    def test_root_references_child_agents(self):
        """Root AGENTS.md must reference child AGENTS.md files."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        content = root_agents.read_text()

        # Check for references to child directories
        expected_refs = ["src/AGENTS.md", ".claude/AGENTS.md"]
        for ref in expected_refs:
            assert ref in content or ref.replace("/", "\\") in content, f"Missing reference to {ref}"


class TestGoldenRules:
    """Test Golden Rules consistency across AGENTS.md files."""

    def test_root_has_golden_rules(self):
        """Root AGENTS.md must define Golden Rules."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        content = root_agents.read_text()
        assert "Golden Rules" in content, "Missing Golden Rules section"

    def test_fal_key_security_rule(self):
        """FAL_KEY security rule must be present."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        content = root_agents.read_text()
        content_lower = content.lower()
        assert "fal_key" in content_lower or "fal key" in content_lower
        assert "never" in content_lower and "hardcode" in content_lower

    def test_env_gitignore_rule(self):
        """Rule about .env in .gitignore must be present."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        content = root_agents.read_text()
        content_lower = content.lower()
        assert ".env" in content
        assert "gitignore" in content_lower

    def test_rgba_preservation_rule(self):
        """RGBA preservation rule must be present."""
        fal_agents = PROJECT_ROOT / "src" / "fal_api" / "AGENTS.md"
        content = fal_agents.read_text()
        content_lower = content.lower()
        assert "rgba" in content_lower or "alpha" in content_lower


class TestSkillAgentCoordination:
    """Test that skills and agents are properly coordinated."""

    def test_claude_agents_md_lists_skills(self):
        """.claude/AGENTS.md must list available skills."""
        claude_agents = PROJECT_ROOT / ".claude" / "AGENTS.md"
        content = claude_agents.read_text()
        skills = ["image-decompose", "layer-export", "quick-edit", "background-remove"]
        for skill in skills:
            assert skill in content, f"Skill '{skill}' not listed in .claude/AGENTS.md"

    def test_claude_agents_md_lists_subagents(self):
        """.claude/AGENTS.md must list available subagents."""
        claude_agents = PROJECT_ROOT / ".claude" / "AGENTS.md"
        content = claude_agents.read_text()
        agents = ["BatchProcessor", "LayerEditor", "CompositionEngine", "QualityChecker"]
        for agent in agents:
            assert agent in content, f"Agent '{agent}' not listed in .claude/AGENTS.md"

    def test_skills_directory_structure(self):
        """Skills must follow directory structure: skills/{name}/SKILL.md"""
        skills_dir = PROJECT_ROOT / ".claude" / "skills"
        assert skills_dir.exists(), "Skills directory not found"

        skill_names = ["image-decompose", "layer-export", "quick-edit", "background-remove"]
        for name in skill_names:
            skill_path = skills_dir / name / "SKILL.md"
            assert skill_path.exists(), f"Skill structure invalid for {name}"

    def test_agents_directory_structure(self):
        """Agents must be in .claude/agents/*.md"""
        agents_dir = PROJECT_ROOT / ".claude" / "agents"
        assert agents_dir.exists(), "Agents directory not found"

        agent_names = ["batch_processor", "layer_editor", "composition_engine", "quality_checker"]
        for name in agent_names:
            agent_path = agents_dir / f"{name}.md"
            assert agent_path.exists(), f"Agent file not found: {name}.md"


class TestDocumentationIntegrity:
    """Test documentation completeness."""

    def test_claude_md_exists(self):
        """CLAUDE.md must exist in .claude directory."""
        claude_md = PROJECT_ROOT / ".claude" / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md not found"

    def test_claude_md_has_quick_start(self):
        """CLAUDE.md must have Quick Start section."""
        claude_md = PROJECT_ROOT / ".claude" / "CLAUDE.md"
        content = claude_md.read_text()
        assert "Quick Start" in content, "Missing Quick Start in CLAUDE.md"

    def test_readme_documents_agent_system(self):
        """README.md must document the agent system."""
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        # Check for agent system section
        has_agent_docs = "Agent" in content or "Skills" in content or "SubAgent" in content
        assert has_agent_docs, "README.md missing agent system documentation"


class TestCodebaseConsistency:
    """Test codebase consistency with agent definitions."""

    def test_fal_api_module_exists(self):
        """Fal API module must exist as referenced in skills."""
        fal_api = PROJECT_ROOT / "src" / "fal_api"
        assert fal_api.exists(), "src/fal_api directory not found"

    def test_decompose_module_exists(self):
        """decompose.py must exist for image-decompose skill."""
        decompose = PROJECT_ROOT / "src" / "fal_api" / "decompose.py"
        assert decompose.exists(), "decompose.py not found"

    def test_export_module_exists(self):
        """export.py must exist for layer-export skill."""
        export = PROJECT_ROOT / "src" / "fal_api" / "export.py"
        assert export.exists(), "export.py not found"

    def test_run_demo_exists(self):
        """run_demo.py must exist as referenced in skills."""
        run_demo = PROJECT_ROOT / "src" / "fal_api" / "run_demo.py"
        assert run_demo.exists(), "run_demo.py not found"


class TestNoEmojisInAgentsmd:
    """Test that AGENTS.md files don't contain emojis."""

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

    @pytest.mark.parametrize("agents_path", AGENTS_MD_LOCATIONS)
    def test_no_emojis(self, agents_path):
        """AGENTS.md files must not contain emojis."""
        content = agents_path.read_text()
        matches = self.EMOJI_PATTERN.findall(content)
        assert not matches, f"Emojis found in {agents_path}: {matches}"


class TestEnvConfiguration:
    """Test environment configuration."""

    def test_env_example_exists(self):
        """.env.example must exist."""
        env_example = PROJECT_ROOT / ".env.example"
        assert env_example.exists(), ".env.example not found"

    def test_env_example_has_fal_key(self):
        """.env.example must include FAL_KEY."""
        env_example = PROJECT_ROOT / ".env.example"
        content = env_example.read_text()
        assert "FAL_KEY" in content, "FAL_KEY not in .env.example"

    def test_gitignore_excludes_env(self):
        """.gitignore must exclude .env file."""
        gitignore = PROJECT_ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            assert ".env" in content, ".env not in .gitignore"


class TestRequirements:
    """Test requirements files exist and are valid."""

    def test_fal_requirements_exists(self):
        """requirements-fal.txt must exist."""
        req = PROJECT_ROOT / "requirements-fal.txt"
        assert req.exists(), "requirements-fal.txt not found"

    def test_fal_requirements_has_essentials(self):
        """requirements-fal.txt must have essential packages."""
        req = PROJECT_ROOT / "requirements-fal.txt"
        content = req.read_text()
        essentials = ["fal-client", "pillow", "python-dotenv"]
        for pkg in essentials:
            assert pkg.lower() in content.lower(), f"Missing package: {pkg}"


class TestFullSystemIntegrity:
    """Test overall system integrity."""

    def test_all_expected_files_exist(self):
        """All expected files for agent system must exist."""
        expected_files = [
            "AGENTS.md",
            "src/AGENTS.md",
            "src/fal_api/AGENTS.md",
            ".claude/AGENTS.md",
            ".claude/CLAUDE.md",
            "docs/AGENTS.md",
            ".claude/skills/image-decompose/SKILL.md",
            ".claude/skills/layer-export/SKILL.md",
            ".claude/skills/quick-edit/SKILL.md",
            ".claude/skills/background-remove/SKILL.md",
            ".claude/agents/batch_processor.md",
            ".claude/agents/layer_editor.md",
            ".claude/agents/composition_engine.md",
            ".claude/agents/quality_checker.md",
            "src/fal_api/decompose.py",
            "src/fal_api/export.py",
            "src/fal_api/run_demo.py",
            ".env.example",
            "requirements-fal.txt"
        ]

        missing = []
        for file in expected_files:
            path = PROJECT_ROOT / file
            if not path.exists():
                missing.append(file)

        assert not missing, f"Missing files: {missing}"

    def test_total_file_count(self):
        """Agent system should have expected number of files."""
        # Count AGENTS.md files
        agents_count = len(list(PROJECT_ROOT.rglob("AGENTS.md")))
        assert agents_count >= 5, f"Expected 5+ AGENTS.md files, found {agents_count}"

        # Count skills
        skills_count = len(list((PROJECT_ROOT / ".claude" / "skills").glob("*/SKILL.md")))
        assert skills_count == 4, f"Expected 4 skills, found {skills_count}"

        # Count agents
        agents_count = len(list((PROJECT_ROOT / ".claude" / "agents").glob("*.md")))
        assert agents_count == 4, f"Expected 4 agents, found {agents_count}"
