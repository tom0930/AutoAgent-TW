import pytest
from scripts.execution.context_router import ContextScopeRouter
from scripts.execution.validator import ValidationGate

def test_context_router_paths():
    files = ["src/api/routes.py"]
    scope = ContextScopeRouter.get_scope("backend", files)
    
    assert "src/api/" in scope["allowed_paths"]
    assert "src/core/" in scope["allowed_paths"]
    assert "tests/" in scope["allowed_paths"]
    assert "src/api/routes.py" in scope["allowed_paths"]
    
    # Check that UI paths are not included for backend role
    assert "src/components/" not in scope["allowed_paths"]

def test_context_router_unrecognized_role():
    files = ["main.py"]
    scope = ContextScopeRouter.get_scope("unknown_role", files)
    # Should fallback to developer
    assert "src/" in scope["allowed_paths"]
    assert "main.py" in scope["allowed_paths"]

def test_validation_gate_success(monkeypatch):
    import subprocess
    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = "success"
            stderr = ""
        return MockResult()
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    success, payload = ValidationGate.run_checks([["echo", "test"]])
    assert success is True

def test_validation_gate_failure(monkeypatch):
    import subprocess
    def mock_run(hook, *args, **kwargs):
        if hook[0] == "fail_cmd":
            raise subprocess.CalledProcessError(1, hook, output="failed output", stderr="failed stderr")
        elif hook[0] == "git":
            class MockResult:
                stdout = "diff data"
            return MockResult()
            
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    success, payload = ValidationGate.run_checks([["fail_cmd"]])
    assert success is False
    assert "failed stderr" in payload["error_log"]
    assert payload["diff"] == "diff data"
