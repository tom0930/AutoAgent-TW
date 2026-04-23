"""Pytest configuration for AI Harness test suite."""
from __future__ import annotations

import sys
import os

# Ensure project root is on sys.path for all tests
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def pytest_configure(config):
    """Configure pytest settings."""
    # Register custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    for item in items:
        # Auto-mark tests based on their location
        if "integration" in str(item.fspath):
            item.add_marker("integration")
        elif "tests/" in str(item.fspath):
            item.add_marker("unit")
