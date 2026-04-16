import asyncio
import logging
import sys
import os

# Set up project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.rva.rva_engine import RVAEngine

logging.basicConfig(level=logging.INFO)

async def test_vav_paint():
    engine = RVAEngine()
    
    print("--- Testing RVA Verify-Act-Verify (VAV) ---")
    print("Action: Click 'Brush' tool in MS Paint with verification.")
    
    # This will trigger before/after screenshots and vision judgment
    success = await engine.perform_action("Brush", action_type="click", verify=True)
    
    if success:
        print("TEST PASSED: Element clicked and verified visually.")
    else:
        print("TEST FAILED: Action failed or verification rejected.")

if __name__ == "__main__":
    asyncio.run(test_vav_paint())
