# tests/rva/test_synergy.py

import pytest
import asyncio
from src.core.rva.rva_engine import RVAEngine

@pytest.mark.asyncio
async def test_rva_google_synergy():
    """Verify that RVAEngine can successfully query and extract from Google App."""
    engine = RVAEngine()
    
    if not engine.google_ctrl.is_running():
        pytest.skip("Google App is not running for synergy test.")
    
    query = "Xilinx AXI VDMA register map"
    # Note: query_google_ai is not async currently for simplicity 
    # as it's a wrapper around pywinauto which is synchronous.
    result = engine.query_google_ai(query)
    
    assert result is not None
    print(f"\nSynergy Result Length: {len(result)}")
    if len(result) > 0:
        print(f"Synergy Metadata: {result[:200]}...")
        # Check for key automotive/industrial terms that would appear in an VDMA search
        assert any(term in result.lower() for term in ["vdma", "register", "xilinx", "address", "axi"])

    # Ensure it minimizes after
    engine.google_ctrl.minimize()
