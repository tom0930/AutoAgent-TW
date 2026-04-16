import ctypes
import pyautogui
import time
import sys

def enable_dpi():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        ctypes.windll.user32.SetProcessDPIAware()

def click_tray(x, y, action="right"):
    enable_dpi()
    print(f"Clicking {action} at ({x}, {y}) (DPI Aware)...")
    pyautogui.moveTo(x, y, duration=0.5)
    
    if action == "right":
        pyautogui.rightClick()
    else:
        pyautogui.doubleClick()
    
    time.sleep(1)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "right"
    x = int(sys.argv[2]) if len(sys.argv) > 2 else 2270
    y = int(sys.argv[3]) if len(sys.argv) > 3 else 25
    click_tray(x, y, action)
