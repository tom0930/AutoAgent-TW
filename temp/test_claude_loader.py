import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config.claude_loader import ClaudeLoader

def test_loader():
    loader = ClaudeLoader(str(PROJECT_ROOT))
    if not loader.exists():
        print("CLAUDE.md not found!")
        return
        
    fragment = loader.load_prompt_fragment()
    print("\n--- Prompt Fragment Generated ---")
    print(fragment)
    print("-" * 30)

if __name__ == "__main__":
    test_loader()
