import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.hooks.hook_manager import HookManager

def test_hook():
    mgr = HookManager(str(PROJECT_ROOT))
    event_data = {
        "tool_name": "write_file",
        "file_path": "test_script.py"
    }
    print("Testing PostToolUse event...")
    mgr.trigger("PostToolUse", event_data)

if __name__ == "__main__":
    test_hook()
