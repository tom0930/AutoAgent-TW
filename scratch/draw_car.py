import pyautogui
import subprocess
import time
import ctypes
import math

def enable_dpi():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        ctypes.windll.user32.SetProcessDPIAware()

def draw_car():
    enable_dpi()
    # 1. 啟動並等待
    print("Launching MS Paint...")
    subprocess.Popen(['mspaint.exe'])
    time.sleep(3) # 等待 UI 加載

    # 2. 設定畫布區域 (假設最大化或預設位置)
    # 我們先假設在螢幕中央附近繪圖以避免邊界問題
    start_x, start_y = 1500, 500 
    
    print("Drawing car body...")
    # 畫車身 (長方形)
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragRel(400, 0, duration=0.5)   # 頂邊
    pyautogui.dragRel(0, 150, duration=0.5)   # 右邊
    pyautogui.dragRel(-400, 0, duration=0.5)  # 底邊
    pyautogui.dragRel(0, -150, duration=0.5)  # 左邊

    print("Drawing wheels...")
    # 畫後輪 (圓形模擬)
    wheel1_center = (start_x + 100, start_y + 150)
    pyautogui.moveTo(wheel1_center[0] + 40, wheel1_center[1])
    for i in range(0, 361, 30):
        rad = math.radians(i)
        px = wheel1_center[0] + 40 * math.cos(rad)
        py = wheel1_center[1] + 40 * math.sin(rad)
        pyautogui.dragTo(px, py, duration=0.05)

    # 畫前輪
    wheel2_center = (start_x + 300, start_y + 150)
    pyautogui.moveTo(wheel2_center[0] + 40, wheel2_center[1])
    for i in range(0, 361, 30):
        rad = math.radians(i)
        px = wheel2_center[0] + 40 * math.cos(rad)
        py = wheel2_center[1] + 40 * math.sin(rad)
        pyautogui.dragTo(px, py, duration=0.05)

    print("Car rendering complete.")

if __name__ == "__main__":
    draw_car()
