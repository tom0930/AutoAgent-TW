from enum import IntEnum

class ExitCode(IntEnum):
    """Standardized exit codes for AutoAgent-TW CI/CD and Headless execution."""
    SUCCESS = 0
    FAILURE = 1
    NEEDS_HUMAN = 2
    AUTH_ERROR = 10
    RATE_LIMIT = 42
    TIMEOUT = 124
