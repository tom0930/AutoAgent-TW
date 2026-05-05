"""Shared constants for AutoAgent-TW.

Centralized path handling to ensure consistency across CLI, 
Background Daemons, and Sub-Agents.
"""

import os
from pathlib import Path

def get_aa_core() -> Path:
    """Return the AutoAgent core installation directory.
    
    Reads AA_CORE env var, falls back to Z:\\AutoAgent-TW as default.
    """
    return Path(os.getenv("AA_CORE", r"Z:\AutoAgent-TW")).resolve()

def get_workspace() -> Path:
    """Return the active user workspace (sandbox) directory.
    
    Reads AA_WORKSPACE env var, falls back to the current working directory.
    """
    return Path(os.getenv("AA_WORKSPACE", os.getcwd())).resolve()

def get_planning_dir() -> Path:
    """Return the path to the centralized .planning directory in the workspace."""
    return get_workspace() / ".planning"

def get_state_dir() -> Path:
    """Return the path to the .agent-state directory in the workspace."""
    return get_workspace() / ".agent-state"

def get_logs_dir() -> Path:
    """Return the path to the .agents/logs directory."""
    return get_workspace() / ".agents" / "logs"

def get_skills_dir() -> Path:
    """Return the path to the global skills directory."""
    # Priority for Antigravity Global Skills
    global_dir = Path(os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\skills"))
    if global_dir.exists():
        return global_dir
    return get_workspace() / ".agents" / "skills"

def get_config_path() -> Path:
    """Return the path to the mcp_servers.json config."""
    return get_workspace() / ".agents" / "mcp_servers.json"
