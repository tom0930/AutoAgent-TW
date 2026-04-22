import json
import sys
import os
from urllib.parse import urlparse

# AutoCLI Security Policy
DEFAULT_POLICY = {
    "whitelist": [
        "github.com",
        "wikipedia.org",
        "arxiv.org",
        "python.org",
        "rust-lang.org"
    ],
    "blacklist": [
        "doubleclick.net",
        "adservice.google.com",
        "facebook.com"
    ],
    "max_memory_mb": 50,
    "stealth_mode": True
}

POLICY_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "autocli_policy.json")

def load_policy():
    if os.path.exists(POLICY_PATH):
        try:
            with open(POLICY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return DEFAULT_POLICY
    return DEFAULT_POLICY

def check_url_safety(url: str) -> bool:
    """
    Validates URL against domain whitelist/blacklist.
    Returns True if safe, False otherwise.
    """
    policy = load_policy()
    try:
        domain = urlparse(url).netloc.lower()
        if not domain:
            # Handle cases like "github.com" without scheme
            domain = url.split('/')[0].lower()
        
        # Check blacklist first
        for blocked in policy.get("blacklist", []):
            if blocked in domain:
                return False
        
        # Check whitelist
        for allowed in policy.get("whitelist", []):
            if allowed in domain:
                return True
        
        # Default to False if whitelist exists but domain not in it
        if policy.get("whitelist"):
            return False
            
        return True
    except:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        is_safe = check_url_safety(test_url)
        print(f"URL: {test_url} -> {'SAFE' if is_safe else 'BLOCKED'}")
        sys.exit(0 if is_safe else 1)
