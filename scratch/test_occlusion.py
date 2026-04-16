import asyncio
import os
import sys
import pyautogui
import time

# Add project root to path
sys.path.append(os.getcwd())

from src.core.rva.rva_engine import RVAEngine

async def test_occlusion():
    engine = RVAEngine()
    target_title = "Status" # 剛才確定的儀表板視窗
    
    print(f"--- Occlusion Test on '{target_title}' ---")
    
    # 確保視窗存在
    import pygetwindow as gw
    wins = gw.getWindowsWithTitle(target_title)
    if not wins:
        print(f"Error: Window '{target_title}' not found.")
        return
        
    win = wins[0]
    # 故意將滑鼠移到角落，並手動確保該視窗被遮住 (在測試時我假設它可能被覆蓋)
    
    print("Capturing using PrintWindow (should work even if occluded)...")
    img = engine._capture_occluded_window(target_title)
    
    if img:
        path = r"z:\del\rva\occlusion_test_success.png"
        img.save(path)
        print(f"Success! Occlusion-proof screenshot saved to: {path}")
        print(f"Image Size: {img.size}")
    else:
        print("Fallback: PrintWindow failed. This app might use GPU acceleration (Chrome/Electron).")

if __name__ == "__main__":
    asyncio.run(test_occlusion())
