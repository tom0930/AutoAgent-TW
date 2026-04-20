# tests/rva/test_gui_control.py

# pyrefly: ignore [missing-import]
import pytest
import subprocess
import time
import os
# pyrefly: ignore [missing-import]
from src.core.rva.gui_control import PywinautoController

@pytest.fixture(scope="module")
def notepad_app():
    """Launch Notepad using pywinauto Application."""
    from pywinauto import Application
    app = Application(backend="uia").start("notepad.exe")
    time.sleep(3.0)
    yield app
    # Cleanup
    os.system("taskkill /f /im notepad.exe")

def test_controller_notepad_basics(notepad_app):
    ctrl = PywinautoController(primary_backend="uia")
    # 1. Test window resolution
    win_title = r".*Notepad.*|.*\u8a18\u4e8b\u672c.*"
    
    # 2. Test typing and reading
    try:
        # Increase timeout for the first successful hit
        success = ctrl.find_and_click(win_title, control_type="Edit", timeout=5.0)
        
        if success:
            print("✓ Successfully clicked Notepad Edit area")
            # Try to read
            text = ctrl.read_text(win_title, control_type="Edit")
            print(f"✓ Initial Text: '{text}'")
        else:
            print("FAILED to find Edit component via UIA")
            # Fallback to win32 in test if uia is being weird
            success = ctrl.find_and_click(win_title, control_type="Edit")

    except Exception as e:
        print(f"Error during test: {e}")
        success = False

    assert success, "Should be able to find and click a component in Notepad"
    
    # 3. Test read_text (should be empty initially)
    text = ctrl.read_text(win_title, control_type="Edit")
    print(f"Read text: '{text}'")
    
    # 4. Test cache (call again, should be faster)
    start_ts = time.time()
    ctrl.read_text(win_title, control_type="Edit")
    end_ts = time.time()
    print(f"Cached read took: {end_ts - start_ts:.4f}s")

def test_sensitive_blacklist():
    ctrl = PywinautoController()
    
    # Mocking is hard with pywinauto objects, 
    # but we can verify the _is_sensitive logic if we expose it or use regex tests
    from src.core.rva.gui_control import SENSITIVE_TITLE_PATTERNS
    import re
    
    assert re.search(SENSITIVE_TITLE_PATTERNS[0], "Please enter your password", re.IGNORECASE)
    assert re.search(SENSITIVE_TITLE_PATTERNS[2], "loading .env file", re.IGNORECASE)

if __name__ == "__main__":
    # Manual run
    pytest.main([__file__, "-s"])
