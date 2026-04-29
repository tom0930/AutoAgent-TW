import sys
import re
from typing import TextIO, List

class LogSanitizerStream:
    """
    Wraps a text stream and filters out sensitive patterns (API Keys, Tokens).
    """
    def __init__(self, stream: TextIO, patterns: List[str]):
        self._stream = stream
        self._patterns = [re.compile(p) for p in patterns]

    def write(self, data: str) -> int:
        if not data:
            return 0
        
        sanitized_data = data
        for pattern in self._patterns:
            sanitized_data = pattern.sub(" ***MASKED*** ", sanitized_data)
            
        return self._stream.write(sanitized_data)

    def flush(self):
        self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)

def install_ci_sanitizer():
    """
    Installs global stdout/stderr hooks to mask sensitive tokens in CI logs.
    """
    sensitive_patterns = [
        r"sk-[a-zA-Z0-9]{32,}",      # OpenAI/Anthropic/Gemini pattern
        r"ghp_[a-zA-Z0-9]{36,}",     # GitHub Personal Access Token
        r"glpat-[a-zA-Z0-9-]{20,}",  # GitLab PAT
        r"token=[a-zA-Z0-9._-]{40,}" # Generic token param
    ]
    
    sys.stdout = LogSanitizerStream(sys.stdout, sensitive_patterns)
    sys.stderr = LogSanitizerStream(sys.stderr, sensitive_patterns)
    print("[LogSanitizer] CI Log Sanitization active. Tokens will be masked.")
