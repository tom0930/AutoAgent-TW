import pyautogui
import os

def capture_top_tray():
    # 確保座標正確性 (3840x2160 下的邏輯座標)
    # 取右上角範圍
    width, height = pyautogui.size()
    print(f"Screen size: {width}x{height}")
    
    # 區域：從 3000 開始，寬 840，高 150 (頂部工作列)
    region = (width - 1000, 0, 1000, 150)
    
    # 執行 Win+D 確保沒被視窗遮住
    pyautogui.hotkey('win', 'd')
    import time
    time.sleep(1)
    
    # 截圖
    snap = pyautogui.screenshot(region=region)
    path = r"z:\del\rva\top_tray_debug.png"
    snap.save(path)
    print(f"Top Tray snapshot saved to: {path}")

if __name__ == "__main__":
    capture_top_tray()
