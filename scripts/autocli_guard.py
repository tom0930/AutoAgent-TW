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

    Handles three URL forms:
      - Full URL:  https://github.com/user/repo
      - Bare host: github.com/user/repo  (no scheme)
      - IP:port:   192.168.1.1:8080/path
    """
    policy = load_policy()
    try:
        # Primary: try standard parser
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Fallback: no scheme — treat entire string as domain:port/path
        if not domain:
            # Strip leading // which urlparse tolerates but ignores
            fallback = url.lstrip("/").split("/")[0]
            # Handle user:pass@host:port format
            if "@" in fallback:
                fallback = fallback.split("@")[-1]
            domain = fallback.lower()

        if not domain:
            return False

        # Check blacklist first (broader match)
        for blocked in policy.get("blacklist", []):
            if blocked in domain:
                return False

        # Check whitelist (exact or subdomain match)
        for allowed in policy.get("whitelist", []):
            # Allow exact match OR subdomain (e.g. "github.com" matches "api.github.com")
            if allowed == domain or domain.endswith("." + allowed):
                return True

        # If a whitelist is defined, default-deny
        if policy.get("whitelist"):
            return False

        return True
    except Exception:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        is_safe = check_url_safety(test_url)
        print(f"URL: {test_url} -> {'SAFE' if is_safe else 'BLOCKED'}")
        sys.exit(0 if is_safe else 1)
