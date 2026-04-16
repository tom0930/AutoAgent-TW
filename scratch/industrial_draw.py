import win32gui
import win32api
import win32con
import time

def draw_industrial_car():
    # 1. 尋找小畫家視窗
    hwnd = win32gui.FindWindow(None, "未命名 - 小畫家")
    if not hwnd:
        # 嘗試處理已經改名或帶有路徑的情況
        def callback(h, extra):
            if "小畫家" in win32gui.GetWindowText(h):
                extra.append(h)
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        if hwnds: hwnd = hwnds[0]

    if not hwnd:
        print("Error: Could not find Paint window.")
        return

    # 2. 獲取內部繪圖區域 (Canvas) 的視窗句柄
    # 小畫家的繪圖區通常是一個子視窗，類名為 "MSPaintView" 或 "Afx:" 系列
    canvas_hwnd = 0
    def find_canvas(h, extra):
        nonlocal canvas_hwnd
        class_name = win32gui.GetClassName(h)
        if "MSPaintView" in class_name or "Afx" in class_name:
            canvas_hwnd = h
    win32gui.EnumChildWindows(hwnd, find_canvas, None)
    
    target_hwnd = canvas_hwnd if canvas_hwnd else hwnd
    print(f"Targeting HWND: {target_hwnd}")

    # 3. 強制置頂並獲取焦點
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)

    # 4. 發射畫圖指令 (使用 WM_LBUTTONDOWN + WM_MOUSEMOVE)
    def make_lparam(x, y):
        return (y << 16) | x

    # 畫一個大的矩形 (相對座標)
    start_x, start_y = 200, 200
    win32api.PostMessage(target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, make_lparam(start_x, start_y))
    
    # 繪製車身 (緩慢移動)
    for i in range(0, 400, 10):
        win32api.PostMessage(target_hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, make_lparam(start_x + i, start_y))
        time.sleep(0.01)
    for i in range(0, 150, 10):
        win32api.PostMessage(target_hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, make_lparam(start_x + 400, start_y + i))
        time.sleep(0.01)
    for i in range(400, 0, -10):
        win32api.PostMessage(target_hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, make_lparam(start_x + i, start_y + 150))
        time.sleep(0.01)
    for i in range(150, 0, -10):
        win32api.PostMessage(target_hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, make_lparam(start_x, start_y + i))
        time.sleep(0.01)

    win32api.PostMessage(target_hwnd, win32con.WM_LBUTTONUP, 0, make_lparam(start_x, start_y))
    print("Industrial sequence completed.")

if __name__ == "__main__":
    draw_industrial_car()
