import re
import sys
from typing import List, Pattern

class LogSanitizer:
    """
    AutoAgent-TW Log Sanitizer (Phase 129: Headless Security)
    Redacts sensitive information like API keys and tokens from logs and stdout.
    """
    
    # Default patterns for common secrets
    DEFAULT_PATTERNS = [
        r"sk-ant-api[a-zA-Z0-9\-_]{20,}",  # Anthropic
        r"AIzaSy[a-zA-Z0-9\-_]{30,}",      # Google/Gemini
        r"ghp_[a-zA-Z0-9]{30,}",           # GitHub PAT
        r"xox[baprs]-[a-zA-Z0-9\-_]{10,}", # Slack
        r"[a-fA-F0-9]{32,}",               # Generic MD5/Hex secrets
    ]
    
    def __init__(self, patterns: List[str] = None):
        self.patterns: List[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in (patterns or self.DEFAULT_PATTERNS)
        ]
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def sanitize(self, text: str) -> str:
        """Replace sensitive patterns with [REDACTED]."""
        if not isinstance(text, str):
            return text
            
        sanitized = text
        for pattern in self.patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)
        return sanitized

    def wrap_streams(self):
        """Wrap sys.stdout and sys.stderr with sanitizing proxy."""
        sys.stdout = StreamProxy(self._original_stdout, self.sanitize)
        sys.stderr = StreamProxy(self._original_stderr, self.sanitize)

    def restore_streams(self):
        """Restore original stdout and stderr."""
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

class StreamProxy:
    """Proxy object for file-like streams that applies a filter function."""
    def __init__(self, stream, filter_func):
        self.stream = stream
        self.filter_func = filter_func

    def write(self, data):
        sanitized_data = self.filter_func(data)
        self.stream.write(sanitized_data)

    def flush(self):
        self.stream.flush()

    def __getattr__(self, name):
        return getattr(self.stream, name)
