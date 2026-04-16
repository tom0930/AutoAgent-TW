import pyautogui
import os

def capture_tray():
    # Get screen size
    width, height = pyautogui.size()
    print(f"Screen size: {width}x{height}")
    
    # Target region: Bottom right (approx 500x100 corner)
    region = (width - 500, height - 100, 500, 100)
    
    # Take screenshot
    snap = pyautogui.screenshot(region=region)
    path = r"z:\del\rva\tray_debug.png"
    snap.save(path)
    print(f"Tray snapshot saved to: {path}")

if __name__ == "__main__":
    capture_tray()
