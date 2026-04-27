import os
import fnmatch
from pathlib import Path
from typing import List, Optional

class VFSGuard:
    """
    Logical VFS Sandbox for AutoAgent-TW Subagents.
    Enforces path-based access control using environment-injected whitelists.
    """

    def __init__(self):
        self.role = os.getenv("AA_SUBAGENT_ROLE", "general-helper")
        whitelist_raw = os.getenv("AA_WHITELIST", "")
        
        # If whitelist is empty or "*", allow all (legacy/general mode)
        if not whitelist_raw or whitelist_raw == "*":
            self.whitelist = ["*"]
        else:
            self.whitelist = [p.strip() for p in whitelist_raw.split(",")]

    def is_allowed(self, file_path: str) -> bool:
        """Checks if the given file path matches any glob pattern in the whitelist."""
        if "*" in self.whitelist:
            return True
            
        # Normalize path
        abs_path = Path(file_path).absolute()
        try:
            # Assume current working directory is the workspace root
            rel_path = str(abs_path.relative_to(Path.cwd())).replace("\\", "/")
        except ValueError:
            # Path is outside the workspace
            return False
            
        for pattern in self.whitelist:
            # Handle recursive globs (**) or simple patterns
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Also check basename for simple hits
            if fnmatch.fnmatch(Path(rel_path).name, pattern):
                return True
                
        return False

    def enforce(self, file_path: str):
        """Raises PermissionError if access is denied."""
        if not self.is_allowed(file_path):
            role_msg = f"Role: {self.role}"
            raise PermissionError(f"VFS Access Denied. {role_msg} cannot access {file_path}")

def validate_access(path: str):
    """Utility function for quick tool-level interception."""
    VFSGuard().enforce(path)

if __name__ == "__main__":
    # Test stub
    guard = VFSGuard()
    print(f"VFS Guard Active | Role: {guard.role}")
    test_file = "src/core/main.py"
    print(f"Access to {test_file}: {guard.is_allowed(test_file)}")
