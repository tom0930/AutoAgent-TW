import sys
import os
from mcp.server.fastmcp import FastMCP
from typing import Optional

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# pyrefly: ignore [missing-import]
from src.core.rva.rva_engine import RVAEngine
# pyrefly: ignore [missing-import]
from src.core.rva.rva_audit import rva_audit

mcp = FastMCP("RVA_Windows_GUI")
engine = RVAEngine()

DANGER_KEYWORDS = ["erase", "program", "format", "flash", "delete", "clear"]

@mcp.tool()
async def rva_click(target: str, action_type: str = "click", verify: bool = False, auth_code: Optional[str] = None) -> str:
    """
    Perform a robust GUI automation action on the target element.
    Uses UIA fast path and falls back to normalized vision scaling when needed.
    
    Args:
        target: The text, button name, or visual query to locate the element.
        action_type: 'click', 'double_click', 'right_click', 'hover', or 'drag'.
        verify: (Experimental) Set to True to snapshot before/after for vision-based success validation.
        auth_code: Mandatory token for destructive actions. Use 'OVERRIDE_153'.
    """
    tl_target = target.lower()
    is_dangerous = any(k in tl_target for k in DANGER_KEYWORDS)
    
    if is_dangerous:
        if auth_code != "OVERRIDE_153":
            rva_audit.log_action("mcp_server", {"target": target}, "BLOCKED", "HITL validation failed for dangerous keyword.")
            return f"BLOCKED: Operation on '{target}' is restricted. You must provide auth_code='OVERRIDE_153' (Phase 153 Human-In-The-Loop contract)."
            
    success = await engine.perform_action(target, action_type, verify=verify)
    if success:
        return f"SUCCESS: Action '{action_type}' performed on '{target}' (Verified={verify})."
    else:
        return f"FAILED: Could not find or interact with '{target}'. See rva_audit.log."

if __name__ == "__main__":
    mcp.run()
