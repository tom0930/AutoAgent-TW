# scratch/rva_draw_car.py — Robotic Drawing Task

import time
import subprocess
import pyautogui
import logging
from src.core.rva.rva_engine import RVAEngine
from src.core.rva.gui_control import PywinautoController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RVA.Drawing")

def draw_car():
    engine = RVAEngine()
    
    # 1. Start MSPaint
    logger.info("Starting MS Paint...")
    subprocess.Popen("mspaint.exe")
    time.sleep(3) # Wait for startup
    
    window_title = "Untitled - Paint"
    # Note: Depending on system language, the title might change. 
    # Industrial controller uses regex. Supports English/Chinese Paint
    window_title_re = ".*(Paint|小畫家).*"
    
    try:
        # 2. Ensure Paint is visible and focused
        win = engine.gui._get_window(window_title_re)
        win.set_focus()
        win.maximize()
        time.sleep(1)
        
        # 3. Locate Canvas (usually 'UIA_Window_Canvas_Type' or similar)
        # For simplicity in drawing, we will find the center of the window and draw offset
        rect = engine._get_active_window_rect(window_title)
        left, top, width, height = rect
        center_x = left + width // 2
        center_y = top + height // 2
        
        logger.info(f"Target Canvas Center: ({center_x}, {center_y})")
        
        # 4. Drawing Logic
        pyautogui.PAUSE = 0.2
        
        # Body (Rectangle)
        logger.info("Drawing car body...")
        pyautogui.moveTo(center_x - 100, center_y)
        pyautogui.dragRel(200, 0, duration=0.5)  # Bottom 
        pyautogui.dragRel(0, -60, duration=0.5)  # Right
        pyautogui.dragRel(-200, 0, duration=0.5) # Top
        pyautogui.dragRel(0, 60, duration=0.5)   # Left
        
        # Roof (Trapezoid)
        logger.info("Drawing car roof...")
        pyautogui.moveTo(center_x - 70, center_y - 60)
        pyautogui.dragTo(center_x - 40, center_y - 120, duration=0.5)
        pyautogui.dragTo(center_x + 40, center_y - 120, duration=0.5)
        pyautogui.dragTo(center_x + 70, center_y - 60, duration=0.5)
        
        # Wheels (Circles - simplified squares for demo)
        logger.info("Drawing wheels...")
        # Wheel 1
        pyautogui.moveTo(center_x - 60, center_y)
        pyautogui.dragRel(30, 0, duration=0.2)
        pyautogui.dragRel(0, 30, duration=0.2)
        pyautogui.dragRel(-30, 0, duration=0.2)
        pyautogui.dragRel(0, -30, duration=0.2)
        
        # Wheel 2
        pyautogui.moveTo(center_x + 30, center_y)
        pyautogui.dragRel(30, 0, duration=0.2)
        pyautogui.dragRel(0, 30, duration=0.2)
        pyautogui.dragRel(-30, 0, duration=0.2)
        pyautogui.dragRel(0, -30, duration=0.2)
        
        logger.info("Drawing task COMPLETED.")
        
        # Take a confirmation screenshot
        engine._save_debug_image(pyautogui.screenshot(region=rect), "finished_car")
        
    except Exception as e:
        logger.error(f"Drawing failed: {e}")
        # Take error screenshot
        pyautogui.screenshot("error_drawing.png")

if __name__ == "__main__":
    draw_car()
