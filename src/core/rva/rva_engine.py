import logging
import pyautogui
import os
import datetime
import asyncio
from typing import Optional, Tuple
import pygetwindow as gw

# Industrial Win32 additions
try:
    from pywinauto import Desktop
    import win32gui
    import win32ui
    import win32con
    import ctypes
    from ctypes import wintypes
    HAS_WIN32 = True
    
    # DWM API for real coordinates (avoiding shadow bias)
    dwmapi = ctypes.WinDLL("dwmapi")
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
except ImportError:
    HAS_WIN32 = False

# pyrefly: ignore [missing-import]
from src.core.rva.rva_audit import rva_audit
# pyrefly: ignore [missing-import]
from src.core.rva.vision_client import RVAVisionClient
# pyrefly: ignore [missing-import]
from src.core.rva.vision_proxy import VisionProxy
# pyrefly: ignore [missing-import]
from src.core.rva.gui_control import PywinautoController
# pyrefly: ignore [missing-import]
from src.core.rva.context_monitor import ContextMonitor
from PIL import Image

logger = logging.getLogger("RVA.Engine")

# --- Debug Configuration ---
# User Request: Debug default ENABLE, Installation package DISABLE
DEFAULT_SAVE_PATH = r"z:\del\rva"
RVA_DEBUG_SAVE = os.environ.get("RVA_DEBUG_SAVE", "True").lower() == "true"
# ---------------------------

# Configure PyAutoGUI security
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5  # Add a default pause between operations

class RVAEngine:
    def __init__(self, use_uia: bool = True):
        self.vision_client = RVAVisionClient()
        self.vision_proxy = VisionProxy()
        # Phase 157: Industrial GUI Controller
        self.gui = PywinautoController(primary_backend="uia" if use_uia else "win32")
        self.monitor = ContextMonitor(self.gui)
        
        # Phase 149: Resource Extreme Optimization
        try:
            # pyrefly: ignore [missing-import]
            from src.core.reaper import AgentReaper
            reaper = AgentReaper(dry_run=False)
            reaper.reap() # Clear orphans on startup
        except Exception as e:
            logger.warning(f"Failed to run early reaping: {e}")
        
    def _save_debug_image(self, image, name: str):
        r"""Helper to save screenshots to z:\del\rva if debugging is enabled."""
        if not RVA_DEBUG_SAVE:
            return
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            # Sanitize name for filename
            safe_name = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in name])
            path = os.path.join(DEFAULT_SAVE_PATH, f"{timestamp}_{safe_name}.png")
            
            # Ensure directory exists (last-minute check)
            os.makedirs(DEFAULT_SAVE_PATH, exist_ok=True)
            
            image.save(path)
            logger.debug(f"Saved debug screen capture: {path}")
        except Exception as e:
            logger.warning(f"Failed to save debug image: {e}")
        
    def _get_precise_rect(self, hwnd) -> Tuple[int, int, int, int]:
        """Get visual window coordinates using DWM to avoid shadow padding."""
        if not HAS_WIN32:
            # pyrefly: ignore [bad-return]
            return None
            
        rect = wintypes.RECT()
        dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rect),
            ctypes.sizeof(rect)
        )
        # pyrefly: ignore [bad-return, unsupported-operation]
        return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

    def _get_active_window_rect(self, window_name: Optional[str] = None) -> Tuple[int, int, int, int]:
        r"""
        Get window coordinates. Falls back to Full Screen if target not found.
        """
        try:
            target_win = None
            if window_name and HAS_WIN32:
                hwnd = win32gui.FindWindow(None, window_name)
                if hwnd:
                    rect = self._get_precise_rect(hwnd)
                    if rect:
                        return rect
            
            # Fallback to pygetwindow if no specific name or Win32 failed
            if not target_win:
                target_win = gw.getActiveWindow()
                
            if target_win and target_win.width > 20 and target_win.height > 20:
                # Clamp within screen bounds
                screen_w, screen_h = pyautogui.size()
                left = max(0, target_win.left)
                top = max(0, target_win.top)
                width = min(screen_w - left, target_win.width)
                height = min(screen_h - top, target_win.height)
                # pyrefly: ignore [bad-return]
                return (left, top, width, height)
        except Exception as e:
            logger.debug(f"Failed to get window rect: {e}")
            
        w, h = pyautogui.size()
        return (0, 0, w, h)

    def _capture_occluded_window(self, window_name: str) -> Optional[Image.Image]:
        """Attempt to capture window content even if covered/occluded using Win32 API."""
        if not HAS_WIN32:
            return None
        try:
            hwnd = win32gui.FindWindow(None, window_name)
            if not hwnd:
                return None
                
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                return None

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # PW_RENDERFULLCONTENT = 2. Works for many apps even if covered.
            # pyrefly: ignore [missing-attribute]
            result = win32gui.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
            
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            if result == 1:
                return im
            return None
        except Exception as e:
            logger.debug(f"Robust capture failed for '{window_name}': {e}")
            return None

    async def perform_action(self, target: str, action_type: str = "click", verify: bool = False, 
                             window_name: Optional[str] = None, wait_for_window: bool = False,
                             timeout: float = 10.0) -> bool:
        """
        Industrial RVA entry point.
        Supports:
        - wait_for_window: Pre-action synchronization
        - verify: Vision-based post-action validation
        """
        logger.info(f"RVA Action requested: {action_type} on '{target}' (Wait={wait_for_window}, Window={window_name})")
        rva_audit.start_action()

        try:
            # Phase 157: Synchronization layer
            if wait_for_window and window_name:
                if not self.monitor.wait_for_window(window_name, timeout=timeout):
                    return False

            if window_name:
                self.gui.focus_window(window_name)

            # 1. Pre-capture if verification is needed
            before_snap = None
            if verify:
                # Optimized capture
                safe_rect = self._get_active_window_rect(window_name)
                before_snap = pyautogui.screenshot(region=safe_rect)
                self._save_debug_image(before_snap, f"before_{target}")

            # 2. Execute Core (UIA -> Vision fallback)
            success = await self._execute_core(target, action_type, window_name)
            if not success:
                return False

            # 3. Post-capture and Verify
            if verify and before_snap:
                await asyncio.sleep(1.0)
                safe_rect = self._get_active_window_rect(window_name)
                after_snap = pyautogui.screenshot(region=safe_rect)
                self._save_debug_image(after_snap, f"after_{target}")
                
                judgment = await self.vision_client.verify_action_result(
                    before_snap, after_snap, f"Successful {action_type} on {target}"
                )
                
                if not judgment.get("success"):
                    logger.warning(f"Vision Verification FAILED: {judgment.get('reason')}")
                    return False
                logger.info("Vision Verification PASSED.")

            return True

        except pyautogui.FailSafeException:
            logger.critical("RVA FAILSAFE TRIGGERED!")
            raise
        except Exception as e:
            logger.error(f"RVA Action failed: {e}")
            return False
        finally:
            rva_audit.end_action()

    async def _execute_core(self, target: str, action_type: str, window_name: Optional[str] = None) -> bool:
        """Core execution logic (UIA -> Vision)."""
        # Eye-0: Industrial UIA Path
        if window_name:
            # Using the new controller's robust search
            if self.gui.find_and_click(window_name, title_re=f".*{target}.*", timeout=1.0):
                rva_audit.log_action(f"rva_{action_type}", {"target": target}, "SUCCESS", "Resolved via UIA")
                return True
            
            # Additional check for common buttons/elements by control_type
            for c_type in ["Button", "ListItem", "MenuItem", "CheckBox"]:
                if self.gui.find_and_click(window_name, control_type=c_type, title_re=f".*{target}.*", timeout=0.1):
                    rva_audit.log_action(f"rva_{action_type}", {"target": target}, "SUCCESS", f"Resolved via UIA ({c_type})")
                    return True

        # Eye-1: Vision Fallback (Coordinate-based)
        safe_rect = self._get_active_window_rect(window_name)
        left, top, width, height = safe_rect

        screenshot = self.vision_proxy.capture_frame()
        if not screenshot:
            logger.debug("VisionProxy unavailable, falling back to local screenshot.")
            screenshot = pyautogui.screenshot(region=safe_rect)

        self._save_debug_image(screenshot, f"vision_locate_{target}")
        bbox = await self.vision_client.find_target_bbox(screenshot, target)
        if not bbox:
            rva_audit.log_action("rva_click", {"target": target}, "FAILED", "Vision failed to locate element")
            return False

        ymin, xmin, ymax, xmax = bbox
        local_center_x = (xmin + xmax) / 2.0 * width
        local_center_y = (ymin + ymax) / 2.0 * height
        global_x = left + int(local_center_x)
        global_y = top + int(local_center_y)

        if action_type == "click":
            pyautogui.click(x=global_x, y=global_y)
        elif action_type == "double_click":
            pyautogui.doubleClick(x=global_x, y=global_y)
        elif action_type == "right_click":
            pyautogui.rightClick(x=global_x, y=global_y)
        elif action_type == "hover":
            pyautogui.moveTo(x=global_x, y=global_y)
        elif action_type == "drag":
            pyautogui.dragTo(x=global_x, y=global_y, duration=0.5, button='left')
        
        rva_audit.log_action("rva_click", {"target": target, "coords": [global_x, global_y]}, "SUCCESS", "Resolved via Vision")
        return True
