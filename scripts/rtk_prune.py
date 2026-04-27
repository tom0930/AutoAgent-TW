import sys
import os
import re
from pathlib import Path

def prune_code(content: str, mode: str, ext: str) -> str:
    """
    Performs role-aware token pruning based on the specified mode and file extension.
    """
    if mode == "standard":
        return content

    # Aggressive mode: Strip comments and docstrings to save tokens for logic-heavy roles (e.g. C++ expert)
    if mode == "aggressive":
        if ext in [".py"]:
            # Strip Python docstrings
            content = re.sub(r'"""(.*?)"""', '', content, flags=re.DOTALL)
            content = re.sub(r"'''(.*?)'''", '', content, flags=re.DOTALL)
            # Strip line comments
            content = re.sub(r'#.*', '', content)
        elif ext in [".cpp", ".h", ".hpp", ".c", ".cu"]:
            # Strip C-style comments
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            content = re.sub(r'//.*', '', content)
        
        # Remove redundant whitespace and empty lines
        lines = [line.rstrip() for line in content.splitlines() if line.strip()]
        return "\n".join(lines)

    # Sanitized mode: Mask potential secrets for security auditors or external agents
    if mode == "sanitized":
        # Pattern to catch potential assignment of secrets
        secret_patterns = [
            r'(?i)(password|passwd|pwd|secret|api_key|apikey|token|auth_key)\s*[:=]\s*[\'"][^\'"]+[\'"]',
            r'(?i)(password|passwd|pwd|secret|api_key|apikey|token|auth_key)\s*[:=]\s*[^\s,]+'
        ]
        for pattern in secret_patterns:
            content = re.sub(pattern, r'\1 = "[REDACTED]"', content)
        return content

    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: python rtk_prune.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    mode = os.getenv("AA_RTK_MODE", "standard")
    
    if not file_path.exists():
        sys.exit(0)

    try:
        ext = file_path.suffix.lower()
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        pruned = prune_code(content, mode, ext)
        sys.stdout.write(pruned)
    except Exception as e:
        # Fallback to raw content if pruning fails
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            sys.stdout.write(f.read())

if __name__ == "__main__":
    main()
