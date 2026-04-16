import asyncio
import logging
import os
import time
from pywinauto import Application
from src.core.rva.rva_engine import RVAEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Paint_Task")

async def run_paint_task():
    engine = RVAEngine()
    
    # 1. 啟動小畫家
    logger.info("Starting Paint...")
    app = Application(backend="uia").start("mspaint.exe")
    time.sleep(3) # 等待程式開啟
    
    # 2. 點擊「文字」工具 (UIA Name: "Text")
    # 如果 UIA 找不到，robust_click 會嘗試 Vision
    logger.info("Selecting Text tool...")
    success = await engine.robust_click("Text")
    if not success:
        # 嘗試點擊 "A" 圖標 (部分舊版 UIA 名稱不同)
        await engine.robust_click("A")

    # 3. 在畫布上點擊以開始輸入
    # 這裡我們模擬在中央點擊
    import pyautogui
    w, h = pyautogui.size()
    pyautogui.click(w//2, h//2)
    time.sleep(1)
    
    # 4. 輸入 "Hello"
    logger.info("Typing 'Hello'...")
    pyautogui.write("Hello", interval=0.1)
    time.sleep(1)
    
    # 5. 存檔 (Ctrl+S)
    logger.info("Saving file to D:\\temp\\hello.txt...")
    pyautogui.hotkey('ctrl', 's')
    time.sleep(2)
    
    # 6. 輸入路徑並按 Enter
    # 畫面上應已出現另存新檔視窗
    pyautogui.write("D:\\temp\\hello.txt", interval=0.05)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    
    logger.info("Paint task completed.")

if __name__ == "__main__":
    asyncio.run(run_paint_task())
