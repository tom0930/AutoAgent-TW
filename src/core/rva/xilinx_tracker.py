import logging
import time
from typing import Optional, Callable
from pywinauto import Application, Desktop

logger = logging.getLogger("RVA_Xilinx")

class XilinxConsoleTracker:
    """
    Xilinx/Vitis Console Tracker
    透過 pywinauto 直接掛載進 IDE 的 Console 視窗，監控燒錄文字。
    """
    
    def __init__(self, window_title: str = "Xilinx SDK"):
        self.window_title = window_title
        self.last_text = ""

    def find_console_control(self):
        """尋找 Console 控制項 (通常是 RichEdit20W 或類似類名)"""
        try:
            desktop = Desktop(backend="uia")
            # 模糊匹配 IDE 主視窗
            main_win = desktop.window(title_re=f".*{self.window_title}.*")
            if not main_win.exists():
                return None
            
            # 尋找 Console 區域的編輯器
            # Xilinx SDK 常用 'RichEdit' 或 'Edit'
            console = main_win.child_window(control_type="Document") # UIA backend 常見 Document 或 Edit
            if console.exists():
                return console
        except Exception as e:
            logger.debug(f"RVA: Failed to find console control: {e}")
        return None

    def get_latest_logs(self) -> str:
        """獲取新產生的日誌行"""
        console = self.find_console_control()
        if not console:
            return ""

        try:
            full_text = console.get_value() # UIA backend: get_value()
            if full_text == self.last_text:
                return ""
            
            # 僅傳回新增加的部分
            new_part = full_text[len(self.last_text):]
            self.last_text = full_text
            return new_part
        except Exception as e:
            logger.error(f"RVA Trace Error: {e}")
            return ""

    def wait_for_keyword(self, keyword: str, timeout: int = 600) -> bool:
        """阻塞並等待關鍵字出現 (如 'Programming succeeded')"""
        logger.info(f"RVA Track: Waiting for keyword '{keyword}' in Console...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            new_logs = self.get_latest_logs()
            if keyword in new_logs:
                logger.info(f"RVA Track: Keyword '{keyword}' found!")
                return True
            time.sleep(1.0)
        
        logger.warning(f"RVA Track: Timeout waiting for '{keyword}'.")
        return False
