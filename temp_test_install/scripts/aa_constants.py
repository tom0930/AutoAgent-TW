"""Shared constants for AutoAgent-TW.

Centralized path handling to ensure consistency across CLI, 
Background Daemons, and Sub-Agents.
"""

import os
from pathlib import Path

def get_aa_home() -> Path:
    """Return the AutoAgent home directory (default: current directory).
    
    Reads AA_HOME env var, falls back to the project root.
    """
    # In AutoAgent-TW, the home is usually the project root z:\autoagent-TW
    return Path(os.getenv("AA_HOME", os.getcwd())).resolve()

def get_planning_dir() -> Path:
    """Return the path to the centralized .planning directory."""
    return get_aa_home() / ".planning"

def get_state_dir() -> Path:
    """Return the path to the .agent-state directory."""
    return get_aa_home() / ".agent-state"

def get_logs_dir() -> Path:
    """Return the path to the .agents/logs directory."""
    return get_aa_home() / ".agents" / "logs"

def get_skills_dir() -> Path:
    """Return the path to the global skills directory."""
    # Priority for Antigravity Global Skills
    global_dir = Path(os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\skills"))
    if global_dir.exists():
        return global_dir
    return get_aa_home() / ".agents" / "skills"

def get_config_path() -> Path:
    """Return the path to the mcp_servers.json config."""
    return get_aa_home() / ".agents" / "mcp_servers.json"
