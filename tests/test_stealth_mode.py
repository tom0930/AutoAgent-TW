import pytest
from src.core.context_scoper import ContextScoper
from src.integrations.rva.headless_adapter import HeadlessRVAAdapter

def test_context_scoper_stealth():
    scoper = ContextScoper(is_stealth=True, max_tokens=1024)
    base_context = {"docs": ["src/api.py", "README.md", "config.yaml"]}
    
    scoped = scoper.get_scoped_context(["src/api.py"], base_context)
    
    assert scoped["stealth"] is True
    assert scoped["max_tokens"] == 1024
    assert "src/api.py" in scoped["relevant_docs"]
    assert "config.yaml" not in scoped["relevant_docs"]

def test_headless_rva_adapter():
    adapter = HeadlessRVAAdapter(headless_mode=True)
    
    result = adapter.perform_action("click_button", {"id": "submit"})
    assert result["status"] == "skipped"
    
    assert adapter.capture_screen() == b""

def test_headless_rva_standard():
    adapter = HeadlessRVAAdapter(headless_mode=False)
    with pytest.raises(NotImplementedError):
        adapter.perform_action("click", {})
