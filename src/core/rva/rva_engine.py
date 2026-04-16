import asyncio
import logging
import pyautogui
from PIL import Image
from typing import Optional, Tuple
import pygetwindow as gw

from src.core.rva.rva_audit import rva_audit
from src.core.rva.vision_client import RVAVisionClient

logger = logging.getLogger("RVA.Engine")

# Configure PyAutoGUI security
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5  # Add a default pause between operations

class RVAEngine:
    def __init__(self):
        self.vision_client = RVAVisionClient()
        
    def _get_active_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Get coordinates of currently active window (left, top, width, height)"""
        try:
            window = gw.getActiveWindow()
            if not window:
                return None
            return (window.left, window.top, window.width, window.height)
        except Exception:
            return None

    def _try_uia_fast_path(self, target: str, action_type: str) -> bool:
        """
        Attempt to use pywinauto UIAutomation backend.
        Return True if successful, False to trigger Vision Fallback.
        """
        try:
            from pywinauto import Desktop
            # In an industrial engine, we would parse target hierarchy here.
            # For resilience, if target is not easily discoverable by strict match, 
            # we instantly return False to fallback to Vision.
            app = Desktop(backend="uia").window(active_only=True)
            if not app.exists():
                return False
                
            element = app.child_window(best_match=target, control_type="Button")
            if element.exists(timeout=0.5):
                if action_type == "click":
                    element.click_input()
                elif action_type == "double_click":
                    element.double_click_input()
                return True
            return False
        except Exception as e:
            logger.debug(f"UIA fast path missed for '{target}': {e}")
            return False

    async def perform_action(self, target: str, action_type: str = "click") -> bool:
        """
        Execute RVA operation with UIA -> Vision fallback strategy.
        Incorporates Full Auditing & FailSafe.
        """
        logger.info(f"RVA Action requested: {action_type} on '{target}'")
        rva_audit.start_action()
        
        try:
            # 1. Attempt UIA Fast Path
            if self._try_uia_fast_path(target, action_type):
                logger.info("UIA Fast Path: Succeeded.")
                rva_audit.log_action("rva_click", {"target": target}, "SUCCESS", "Resolved via UIA")
                return True

            logger.info("UIA Fast Path: Failed/Missed. Triggering Vision Fallback.")

            # 2. Locate Active Window
            rect = self._get_active_window_rect()
            if not rect:
                # Fallback to whole screen if no active window
                rect = (0, 0, pyautogui.size().width, pyautogui.size().height)
                
            left, top, width, height = rect
            
            # Clamp to screen to avoid negative coordinates
            left = max(0, left)
            top = max(0, top)
            width = min(pyautogui.size().width - left, width)
            height = min(pyautogui.size().height - top, height)

            # 3. Take localized screenshot
            screenshot = pyautogui.screenshot(region=(left, top, width, height))

            # 4. Request Vision BBox
            bbox = await self.vision_client.find_target_bbox(screenshot, target)
            if not bbox:
                logger.warning(f"Vision Fallback: Could not locate '{target}'.")
                rva_audit.log_action("rva_click", {"target": target}, "FAILED", "Vision failed to locate element")
                return False

            # BBox format is (ymin, xmin, ymax, xmax) normalized [0.0, 1.0]
            ymin, xmin, ymax, xmax = bbox
            
            # Calculate Center locally
            local_center_x = (xmin + xmax) / 2.0 * width
            local_center_y = (ymin + ymax) / 2.0 * height
            
            # Translate to Global Screen Coordinates
            global_x = left + int(local_center_x)
            global_y = top + int(local_center_y)

            logger.info(f"Vision localized '{target}' at global ({global_x}, {global_y})")

            # 5. Perform Action
            if action_type == "click":
                pyautogui.click(x=global_x, y=global_y)
            elif action_type == "double_click":
                pyautogui.doubleClick(x=global_x, y=global_y)
            elif action_type == "right_click":
                pyautogui.rightClick(x=global_x, y=global_y)
            elif action_type == "hover":
                pyautogui.moveTo(x=global_x, y=global_y)
            else:
                logger.error(f"Unknown RVA action: {action_type}")
                return False

            rva_audit.log_action("rva_click", {"target": target, "coords": [global_x, global_y]}, "SUCCESS", "Resolved via Vision Fallback")
            return True

        except pyautogui.FailSafeException:
            logger.critical("RVA FAILSAFE TRIGGERED! Mouse moved to corner.")
            rva_audit.log_action("rva_click", {"target": target}, "FAILSAFE", "User triggered FailSafe")
            raise
        except Exception as e:
            logger.error(f"RVA Engine crashed: {e}")
            rva_audit.log_action("rva_click", {"target": target}, "ERROR", str(e))
            return False
        finally:
            rva_audit.end_action()
