import win32gui
import win32con
import time
import win32process
import ctypes
from ctypes import wintypes

dwmapi = ctypes.WinDLL("dwmapi")
DWMWA_EXTENDED_FRAME_BOUNDS = 9

def get_precise_rect(hwnd):
    rect = wintypes.RECT()
    dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect)
    )
    return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

def restore_and_diag(window_name="Status"):
    hwnd = win32gui.FindWindow(None, window_name)
    if not hwnd:
        print(f"Window '{window_name}' not found.")
        return

    print(f"Found Window: {window_name} (HWND: {hwnd})")
    
    # 強制顯示並恢復視窗 (SW_RESTORE = 9)
    print("Attempting to restore window...")
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    
    # 等待渲染動畫完成
    time.sleep(1)
    
    rect = get_precise_rect(hwnd)
    print(f"New Precise Rect: {rect}")
    
    if rect[2] > 0 and rect[3] > 0:
        print("SUCCESS: Window is now visual and ready for capture.")
    else:
        print("WARNING: Window still has 0 size. It might be a background process only.")

if __name__ == "__main__":
    restore_and_diag()
