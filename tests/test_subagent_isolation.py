import pytest
import os
import json
from pathlib import Path
from src.core.orchestration.spawn_manager import AgentProcess
from src.core.orchestration.vfs_guard import VFSGuard
from scripts.rtk_prune import prune_code

def test_vfs_denial(monkeypatch):
    """Verifies that VFSGuard correctly blocks unauthorized paths based on whitelist."""
    monkeypatch.setenv("AA_SUBAGENT_ROLE", "cpp-pro")
    monkeypatch.setenv("AA_WHITELIST", "**/*.cpp,**/*.h,PROJECT.md")
    
    guard = VFSGuard()
    
    # Allowed paths
    assert guard.is_allowed("src/main.cpp") is True
    assert guard.is_allowed("PROJECT.md") is True
    
    # Denied paths
    assert guard.is_allowed("src/core/security.py") is False
    assert guard.is_allowed(".env") is False
    
    with pytest.raises(PermissionError) as excinfo:
        guard.enforce("src/core/security.py")
    assert "Access Denied" in str(excinfo.value)

def test_spawn_manager_role_config():
    """Verifies that AgentProcess can resolve role configurations from subagents.json."""
    agent = AgentProcess("Test Task", role="architect")
    cfg = agent._get_role_config("architect")
    
    assert cfg["rtk_mode"] == "standard"
    assert "**/*.md" in cfg["whitelist"]
    assert "architect.md" in cfg["persona"]

def test_rtk_pruning_aggressive_py():
    """Verifies that aggressive pruning strips Python comments and docstrings."""
    code = """
# Header Comment
def test_func():
    \"\"\"This is a docstring\"\"\"
    x = 10  # inline comment
    return x
"""
    pruned = prune_code(code, "aggressive", ".py")
    assert "# Header Comment" not in pruned
    assert "docstring" not in pruned
    assert "inline comment" not in pruned
    assert "def test_func():" in pruned
    assert "return x" in pruned

def test_rtk_pruning_aggressive_cpp():
    """Verifies that aggressive pruning strips C++ comments."""
    code = """
// Single line comment
/* Multi-line
   comment */
int main() {
    return 0;
}
"""
    pruned = prune_code(code, "aggressive", ".cpp")
    assert "// Single line" not in pruned
    assert "Multi-line" not in pruned
    assert "int main()" in pruned

def test_rtk_pruning_sanitized():
    """Verifies that sanitized mode redacts potential secrets."""
    config = """
[auth]
api_key = "sk-123456789"
db_password = secret_p@ssword
url = https://api.example.com
"""
    pruned = prune_code(config, "sanitized", ".ini")
    assert "sk-123456789" not in pruned
    assert "secret_p@ssword" not in pruned
    assert "[REDACTED]" in pruned
    assert "https://api.example.com" in pruned
