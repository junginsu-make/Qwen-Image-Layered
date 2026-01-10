"""
Pytest configuration for Qwen-Image-Layered tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return project root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def skills_dir(project_root):
    """Return skills directory path."""
    return project_root / ".claude" / "skills"


@pytest.fixture
def agents_dir(project_root):
    """Return agents directory path."""
    return project_root / ".claude" / "agents"


@pytest.fixture
def fal_api_dir(project_root):
    """Return fal_api directory path."""
    return project_root / "src" / "fal_api"
