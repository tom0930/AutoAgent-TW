import sys
import io
from src.core.runtime.headless import HeadlessRuntime
from src.utils.log_sanitizer_ci import LogSanitizerStream

def test_headless_runtime_override():
    runtime = HeadlessRuntime(default_input="auto-pass")
    runtime.activate()
    
    # Mock stdin as empty to trigger default
    sys.stdin = io.StringIO("")
    assert runtime.override_input("Should we continue?") == "auto-pass"

def test_log_sanitizer_masking():
    output = io.StringIO()
    sanitizer = LogSanitizerStream(output, [r"sk-[a-zA-Z0-9]{10,}"])
    
    sanitizer.write("Key is REDACTED_HISTORICAL_SECRET and it is secret.")
    assert "REDACTED_HISTORICAL_SECRET" not in output.getvalue()
    assert "***MASKED***" in output.getvalue()

def test_log_sanitizer_multiple_patterns():
    output = io.StringIO()
    sanitizer = LogSanitizerStream(output, [r"ghp_[a-zA-Z0-9]{10,}", r"token=[a-zA-Z0-9]{10,}"])
    
    sanitizer.write("GitHub: ghp_mysecrettoken123, App: token=9876543210zyx")
    val = output.getvalue()
    assert "ghp_mysecrettoken123" not in val
    assert "token=9876543210zyx" not in val
    assert val.count("***MASKED***") == 2
