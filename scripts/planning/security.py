# scripts/planning/security.py
from typing import List, Dict, Any

DANGEROUS_TOOLS = [
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "run_command",
    "send_command_input"
]

def wrap_user_prompt(prompt: str) -> str:
    """Wraps user prompt in delimiters to prevent prompt injection."""
    return f"""
<user_input>
{prompt}
</user_input>
"""

def filter_read_only_tools(available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters out dangerous tools from the list of available tools."""
    return [tool for tool in available_tools if tool.get('name') not in DANGEROUS_TOOLS]
