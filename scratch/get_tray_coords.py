import win32gui
import win32process
import win32api
import win32con
import ctypes
from ctypes import wintypes

# Structure for Toolbar Buttons
class TBBUTTON(ctypes.Structure):
    _fields_ = [
        ('iBitmap', ctypes.c_int),
        ('idCommand', ctypes.c_int),
        ('fsState', ctypes.c_byte),
        ('fsStyle', ctypes.c_byte),
        ('bReserved', ctypes.c_byte * 2),
        ('dwData', ctypes.c_void_p),
        ('iString', ctypes.c_void_p)
    ]

def get_tray_icon_pos(keyword="Antigravity"):
    # Find Taskbar -> User Promoted Notification Area
    tray_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
    
    def find_toolbar(hwnd, results):
        if "ToolbarWindow32" in win32gui.GetClassName(hwnd):
            # Only visible ones
            if win32gui.IsWindowVisible(hwnd):
                results.append(hwnd)
        return True
    
    toolbars = []
    win32gui.EnumChildWindows(tray_hwnd, find_toolbar, toolbars)
    
    # Also check overflow
    overflow = win32gui.FindWindow("NotifyIconOverflowWindow", None)
    if overflow:
        win32gui.EnumChildWindows(overflow, find_toolbar, toolbars)

    for toolbar_hwnd in toolbars:
        button_count = win32gui.SendMessage(toolbar_hwnd, 0x0418, 0, 0) # TB_BUTTONCOUNT
        print(f"Toolbar {toolbar_hwnd} has {button_count} buttons.")
        
        _, pid = win32process.GetWindowThreadProcessId(toolbar_hwnd)
        process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
        
        # Allocate memory in Explorer process for button data
        remote_mem = ctypes.windll.kernel32.VirtualAllocEx(process.handle, 0, ctypes.sizeof(TBBUTTON), win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
        
        for i in range(button_count):
            win32gui.SendMessage(toolbar_hwnd, 0x0417, i, remote_mem) # TB_GETBUTTON
            
            button = TBBUTTON()
            ctypes.windll.kernel32.ReadProcessMemory(process.handle, remote_mem, ctypes.byref(button), ctypes.sizeof(TBBUTTON), None)
            
            # Get Rect for this button
            remote_rect = ctypes.windll.kernel32.VirtualAllocEx(process.handle, 0, ctypes.sizeof(wintypes.RECT), win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
            win32gui.SendMessage(toolbar_hwnd, 0x0433, i, remote_rect) # TB_GETITEMRECT
            
            rect = wintypes.RECT()
            ctypes.windll.kernel32.ReadProcessMemory(process.handle, remote_rect, ctypes.byref(rect), ctypes.sizeof(wintypes.RECT), None)
            
            # Map coordinates to screen
            p1 = win32gui.ClientToScreen(toolbar_hwnd, (rect.left, rect.top))
            p2 = win32gui.ClientToScreen(toolbar_hwnd, (rect.right, rect.bottom))
            
            # Try to get the text (Tooltip)
            # This is complex, but often the idCommand or dwData helps.
            # For brevity, let's just print all rects if we find a match via other means or just print all.
            print(f"  Button {i}: Rect {p1} to {p2}")

        ctypes.windll.kernel32.VirtualFreeEx(process.handle, remote_mem, 0, win32con.MEM_RELEASE)

if __name__ == "__main__":
    get_tray_icon_pos()
