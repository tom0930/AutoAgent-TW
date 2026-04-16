import win32gui
import win32process
import ctypes
from ctypes import wintypes
import psutil

# DWM constants
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

def diag_windows(keywords=["Antigravity", "Brave", "Status"]):
    print(f"{'Title':<50} | {'PID':<8} | {'HWND':<10} | {'(X, Y, W, H)':<20}")
    print("-" * 100)
    
    def callback(hwnd, extra):
        if not win32gui.IsWindowVisible(hwnd):
            return True
            
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
            
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        # Filter by keywords
        matched = any(kw.lower() in title.lower() for kw in keywords)
        
        # Also check process name if title doesn't match but we might be interested
        try:
            proc = psutil.Process(pid)
            if any(kw.lower() in proc.name().lower() for kw in keywords):
                matched = True
        except:
            pass
            
        if matched:
            rect = get_precise_rect(hwnd)
            print(f"{title[:50]:<50} | {pid:<8} | {hwnd:<10} | {str(rect):<20}")
        return True

    win32gui.EnumWindows(callback, None)

if __name__ == "__main__":
    diag_windows()
