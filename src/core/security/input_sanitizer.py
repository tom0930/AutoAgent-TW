import re
import logging
from typing import List, Tuple

logger = logging.getLogger("Core.Security.InputSanitizer")

class InputSanitizer:
    """
    L1 Defense: Filters and sanitizes user inputs for Prompt Injection patterns.
    """
    # Common Prompt Injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore (all )?previous instructions",
        r"(?i)system override",
        r"(?i)you are now (a|an) (hacker|root|admin)",
        r"(?i)print (your )?system prompt",
        r"(?i)forget everything you've learned",
        r"(?i)base64 decode this: [A-Za-z0-9+/=]+",
        r"(?i)execute (the following )?as shell",
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p) for p in self.INJECTION_PATTERNS]

    def is_safe(self, text: str) -> Tuple[bool, str]:
        """
        Checks if the input text is safe from common injection attacks.
        Returns (is_safe, reason).
        """
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return False, f"Potential Prompt Injection detected (Pattern: {pattern.pattern})"
        
        # Check for excessive length or weird character ratios (anomaly detection)
        if len(text) > 50000: # Example limit
            return False, "Input exceeds safety length limits"

        return True, ""

    def sanitize(self, text: str) -> str:
        """
        Escapes potentially dangerous sequences.
        """
        # Placeholder for more complex sanitization
        return text.strip()
