from typing import List, Dict

class ContextScopeRouter:
    """
    Dynamically limits the context window and accessible paths for agents
    based on their roles to minimize token usage and enforce security.
    """
    
    ROLE_ALLOWED_PATHS = {
        "ui": ["src/components/", "src/app/", "public/"],
        "backend": ["src/api/", "src/core/", "src/models/"],
        "security": ["src/core/security/", "config/", "SECURITY.md"],
        "developer": ["src/", "tests/", "scripts/"]
    }
    
    @classmethod
    def get_scope(cls, role: str, files: List[str]) -> Dict[str, list]:
        """
        Returns a dictionary representing the scope boundaries for a given role and target files.
        """
        # Get base paths for the role, default to developer if unknown
        allowed_paths = cls.ROLE_ALLOWED_PATHS.get(role, cls.ROLE_ALLOWED_PATHS["developer"]).copy()
        
        # Always allow the files they are assigned to modify
        for f in files:
            if f not in allowed_paths:
                allowed_paths.append(f)
                
        # Also, agents should always be able to read tests related to their files
        allowed_paths.append("tests/")
        
        # Remove duplicates
        allowed_paths = list(set(allowed_paths))
        
        return {
            "role": role,
            "allowed_paths": allowed_paths,
            "read_limit": "50k_tokens"  # Just a marker for downstream enforcement
        }
