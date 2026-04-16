import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from src.core.rva.rva_engine import RVAEngine

async def test_capture():
    engine = RVAEngine()
    print("Executing capture test on 'Status' window...")
    # 指定鎖定 'Status' 視窗，即使它不是 Active 也能強制對準。
    success = await engine.perform_action("Proxy_Toggle_Dummy", action_type="hover", verify=True, window_name="Status")
    
    print(f"Action result: {success}")
    
    debug_dir = r"z:\del\rva"
    if os.path.exists(debug_dir):
        files = sorted(os.listdir(debug_dir))
        print(f"Latest files in {debug_dir}: {files[-3:]}")
    else:
        print(f"Error: {debug_dir} does not exist.")

if __name__ == "__main__":
    asyncio.run(test_capture())
