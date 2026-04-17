import os
import time
import logging
import ctypes
from typing import Optional, Tuple, List, Dict
import mss
import pyautogui
from pywinauto import Desktop, Application
from imagehash import dhash
from PIL import Image

# pyrefly: ignore [missing-import]
from src.core.rva.vision_client import GeminiVisionClient
# pyrefly: ignore [missing-import]
from src.core.rva.rva_audit import RVAAuditLogger

# 設置日誌
logger = logging.getLogger("RVA_Engine")

class RVAEngine:
    """
    Hybrid RVA Engine
    優先使用 UIA (pywinauto) 定位，失敗時降級至 Vision LLM。
    具備 DPI 感知與畫面前後狀態驗證。
    """
    
    def __init__(self, failsafe: bool = True):
        # 1. 初始化 DPI Awareness
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            logger.info("RVA: DPI Awareness initialized.")
        except Exception:
            pass
            
        pyautogui.FAILSAFE = failsafe
        self.last_screen_hash = None
        self.screenshot_buffer_dir = "scratch/rva_buffer"
        os.makedirs(self.screenshot_buffer_dir, exist_ok=True)
        
        # 3. 初始化子組件
        self.vision = GeminiVisionClient()
        self.audit = RVAAuditLogger()

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Tuple[Image.Image, str]:
        """截圖並返回 Image 物件與暫存路徑"""
        with mss.mss() as sct:
            if region:
                monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
                sct_img = sct.grab(monitor)
            else:
                sct_img = sct.grab(sct.monitors[0])
            
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            path = os.path.join(self.screenshot_buffer_dir, f"snap_{int(time.time())}.png")
            img.save(path)
            return img, path

    def has_screen_changed(self, threshold: int = 5) -> bool:
        """檢測畫面是否變動 (ImageHash)"""
        current_img, _ = self.capture_screen()
        current_hash = dhash(current_img)
        
        if self.last_screen_hash is None:
            self.last_screen_hash = current_hash
            return True
            
        diff = current_hash - self.last_screen_hash
        logger.debug(f"RVA: Screen hash diff: {diff}")
        
        if diff >= threshold:
            self.last_screen_hash = current_hash
            return True
        return False

    def find_by_uia(self, name: str, control_type: str = "Button", backend: str = "uia") -> Optional[object]:
        """優先嘗試 UIA 定位原生控制項"""
        try:
            desktop = Desktop(backend=backend)
            # 尋找具備特定名稱的子視窗
            element = desktop.window(title_re=".*", found_index=0).child_window(title=name, control_type=control_type)
            if element.exists(timeout=0.5):
                return element
        except Exception as e:
            logger.debug(f"RVA: UIA search failed for '{name}': {e}")
        return None

    async def robust_click(self, target_name: str):
        """強健點擊流程: UIA -> Vision -> Audit"""
        # 1. UIA 嘗試
        element = self.find_by_uia(target_name)
        if element:
            # pyrefly: ignore [missing-attribute]
            coords = element.rectangle()
            self.audit.log_action("click_uia", {"target": target_name, "rect": str(coords)})
            # pyrefly: ignore [missing-attribute]
            element.click_input()
            return True

        # 2. Vision 降級
        logger.info(f"RVA: UIA failed for {target_name}, falling back to Vision...")
        img, path = self.capture_screen()
        coord_data = await self.vision.locate_element(path, target_name)
        
        if coord_data:
            # 換算座標
            w, h = img.size
            l, t, r, b = self.vision.denormalize_coords(coord_data.bbox, w, h)
            center_x, center_y = (l + r) // 2, (t + b) // 2
            
            self.audit.log_action("click_vision", {
                "target": target_name, 
                "norm_bbox": coord_data.bbox,
                "pixel_coords": [center_x, center_y]
            }, path)
            
            pyautogui.click(center_x, center_y)
            return True

        self.audit.log_action("click_failed", {"target": target_name})
        return False

    def wait_for_state_change(self, timeout: int = 30, interval: float = 1.0):
        """等待畫面變更 (例如進度條移動)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.has_screen_changed():
                return True
            time.sleep(interval)
        return False

if __name__ == "__main__":
    # 簡易測試
    logging.basicConfig(level=logging.INFO)
    engine = RVAEngine()
    print("Capturing full screen...")
    img = engine.capture_screen()
    # pyrefly: ignore [missing-attribute]
    img.save("scratch/rva_test_full.png")
    print(f"Screen changed? {engine.has_screen_changed()}")
