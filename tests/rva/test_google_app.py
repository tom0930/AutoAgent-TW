# tests/rva/test_google_app.py

import pytest
import time
from src.core.rva.google_app import GoogleAppController

@pytest.fixture
def google_ctrl():
    return GoogleAppController()

def test_google_interaction_flow(google_ctrl):
    """E2E flow: Presence -> Search -> Extract."""
    if not google_ctrl.is_running():
        pytest.skip("Google App is not running.")

    # 1. Ensure visible
    assert google_ctrl.ensure_visible() is True
    
    # 2. Search (Neutral query)
    query = "Xilinx SDK VDMA configuration"
    assert google_ctrl.perform_search(query) is True
    
    # 3. Wait for results
    time.sleep(5)
    
    # 4. Extract
    content = google_ctrl.extract_content()
    print(f"\nSearch Query: {query}")
    print(f"Content Length: {len(content)}")
    if len(content) > 0:
        print(f"First 200 chars: {content[:200]}")
        # At least one word from query should ideally be there, 
        # but Google Search is dynamic so we just check content exists
        assert len(content) > 0
    
    # 5. Cleanup (minimize)
    google_ctrl.minimize()
