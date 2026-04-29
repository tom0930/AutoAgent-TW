import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HeadlessRuntime:
    """
    Overrides interactive behaviors for CI/CD environments.
    Prevents blocking input() calls and GUI prompts.
    """
    
    def __init__(self, default_input: str = ""):
        self.default_input = default_input
        self._is_active = False

    def activate(self):
        """Enable headless mode hooks."""
        self._is_active = True
        logger.info("[HeadlessRuntime] Active. Interactive prompts are disabled.")

    def override_input(self, prompt: str = "") -> str:
        """
        Intercepts input() calls. Returns default_input or reads from stdin
        if available without blocking.
        """
        if not self._is_active:
            return input(prompt)
            
        logger.debug(f"[HeadlessRuntime] Intercepted input prompt: '{prompt}'")
        
        # In CI, we usually don't have a terminal, so reading from stdin
        # might hang if not piped. We return the default instead.
        if not sys.stdin.isatty():
            return self.default_input
            
        try:
            # Attempt non-blocking read or return default
            return sys.stdin.readline().strip() or self.default_input
        except EOFError:
            return self.default_input

    @property
    def is_headless(self) -> bool:
        return self._is_active
