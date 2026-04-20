import time
import logging
from typing import Optional, Callable, Any
# pyrefly: ignore [missing-import]
from src.core.rva.gui_control import PywinautoController

logger = logging.getLogger("RVA.ContextMonitor")

class ContextMonitor:
    """
    Observer-based UI state monitor using Smart Polling.
    Eliminates dependency on unstable COM event hooks.
    """
    def __init__(self, controller: Optional[PywinautoController] = None):
        self.gui = controller or PywinautoController()
        
    def wait_for_window(self, title_re: str, timeout: float = 30.0, poll_interval: float = 1.0) -> bool:
        """Wait until a window matching title_re appears."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Use a very short internal timeout for polling hit
                if self.gui._get_window(title_re, timeout=0.1):
                    logger.info(f"Context Hit: Window '{title_re}' detected.")
                    return True
            except:
                pass
            time.sleep(poll_interval)
        
        logger.warning(f"Context Timeout: Window '{title_re}' did not appear after {timeout}s.")
        return False

    def wait_for_element(self, window_title_re: str, timeout: float = 30.0, poll_interval: float = 1.0, **kwargs) -> bool:
        """
        Wait until a specific element exists in the target window.
        kwargs are passed to child_window search (e.g. control_type, auto_id).
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                win = self.gui._get_window(window_title_re, timeout=1.0)
                if win:
                    element = win.child_window(**kwargs)
                    if element.exists(timeout=0.1):
                        logger.info(f"Context Hit: Element {kwargs} found in '{window_title_re}'.")
                        return True
            except:
                pass
            time.sleep(poll_interval)
        
        logger.warning(f"Context Timeout: Element {kwargs} not found in '{window_title_re}' after {timeout}s.")
        return False

    def wait_until(self, condition_func: Callable[[], bool], timeout: float = 30.0, poll_interval: float = 0.5) -> bool:
        """Generic wait for an arbitrary boolean condition."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(poll_interval)
        return False
