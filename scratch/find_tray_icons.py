import win32gui
import win32process
import win32api
import win32con

def enum_child_windows(parent_hwnd):
    children = []
    def callback(hwnd, param):
        children.append(hwnd)
        return True
    win32gui.EnumChildWindows(parent_hwnd, callback, None)
    return children

def find_tray():
    tray_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
    print(f"Taskbar HWND: {tray_hwnd}")
    
    children = enum_child_windows(tray_hwnd)
    print(f"Found {len(children)} child windows in taskbar.")
    
    for hwnd in children:
        cls = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if "ToolbarWindow32" in cls:
            rect = win32gui.GetWindowRect(hwnd)
            print(f"Found Tray Toolbar: {title} | Class: {cls} | Rect: {rect}")
            
    # Check for overflow window too (the ^ arrow)
    overflow_hwnd = win32gui.FindWindow("NotifyIconOverflowWindow", None)
    if overflow_hwnd:
        print(f"Overflow Menu HWND: {overflow_hwnd}")
        ov_children = enum_child_windows(overflow_hwnd)
        for hwnd in ov_children:
            cls = win32gui.GetClassName(hwnd)
            if "ToolbarWindow32" in cls:
                rect = win32gui.GetWindowRect(hwnd)
                print(f"Found Overflow Toolbar: Class: {cls} | Rect: {rect}")

if __name__ == "__main__":
    find_tray()
