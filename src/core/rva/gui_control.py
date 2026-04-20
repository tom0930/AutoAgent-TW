# src/core/rva/gui_control.py — Phase 157 Best Approach (v4)

import logging
import time
import re
import fnmatch
from typing import Optional, Dict, Any, List
from pywinauto import Desktop, Application
from pywinauto.timings import wait_until

logger = logging.getLogger("RVA.GUIControl")

# --- Sensitive Control Blacklist ---
SENSITIVE_CONTROL_TYPES = frozenset([
    "PasswordBox", "PasswordEdit",
])
SENSITIVE_TITLE_PATTERNS = [
    r".*password.*", r".*密碼.*", r".*\.env.*",
    r".*private.*key.*", r".*secret.*",
]

class _TTLCache:
    """Window handle cache with auto-expiry to avoid stale handles."""
    def __init__(self, ttl: float = 30.0):
        self._store = {}
        self._ttl = ttl
    
    def get(self, key: str):
        if key in self._store:
            val, ts = self._store[key]
            if time.time() - ts < self._ttl:
                return val
            del self._store[key]
        return None
    
    def set(self, key: str, val):
        self._store[key] = (val, time.time())
    
    def invalidate(self, key: Optional[str] = None):
        if key and key in self._store:
            del self._store[key]
        else:
            self._store.clear()


class PywinautoController:
    """L0/L1: Industrial pywinauto UIA Controller (Best Approach v4)"""
    
    def __init__(self, primary_backend: str = "uia"):
        self._cache = _TTLCache(ttl=30.0)
        self._primary_backend = primary_backend
    
    # --- Core: Window Resolution ---
    
    def _get_window(self, title_re: str, timeout: float = 5.0):
        """Find window with TTL cache + dual-backend fallback."""
        cached = self._cache.get(title_re)
        if cached:
            try:
                # Minimal check if window is still alive
                if cached.exists(timeout=0.3):
                    return cached
            except Exception:
                pass
            self._cache.invalidate(title_re)
        
        # Try both backends (uia first, then win32)
        for backend in [self._primary_backend, "win32" if self._primary_backend == "uia" else "uia"]:
            try:
                desktop = Desktop(backend=backend)
                # Use found_index=0 to resolve ambiguity (ElementAmbiguousError)
                win = desktop.window(title_re=title_re, found_index=0)
                win.wait('visible', timeout=timeout)
                self._cache.set(title_re, win)
                logger.debug(f"Resolved window [{title_re}] using {backend} backend")
                return win
            except Exception:
                continue
        
        raise RuntimeError(f"Window not found after timeout ({timeout}s): {title_re}")
    
    # --- Core: Element Operations ---
    
    def find_and_click(self, window_title_re: str,
                       auto_id: Optional[str] = None,
                       control_type: Optional[str] = None,
                       title_re: Optional[str] = None,
                       class_name: Optional[str] = None,
                       timeout: float = 3.0,
                       max_retries: int = 2,
                       **extra_kwargs) -> bool:
        """Locate and click element with retry and security audit."""
        for attempt in range(max_retries):
            try:
                win = self._get_window(window_title_re)
                
                kwargs = extra_kwargs.copy()
                if auto_id: kwargs['auto_id'] = auto_id
                if control_type: kwargs['control_type'] = control_type
                if title_re: kwargs['title_re'] = title_re
                if class_name: kwargs['class_name'] = class_name
                
                element = win.child_window(**kwargs)
                if not element.exists(timeout=timeout):
                    # Fallback for Scintilla editors (e.g. Notepad 2e, Notepad++) if we were looking for Edit
                    if kwargs.get('control_type') == 'Edit':
                        element = win.child_window(class_name='Scintilla')
                        if not element.exists(timeout=0.5):
                            logger.debug(f"Element [{kwargs}] and Scintilla fallback not found in attempt {attempt+1}")
                            continue

                if element.exists(timeout=timeout):
                    # Security check
                    if self._is_sensitive(element):
                        logger.warning(f"BLOCKED: Sensitive control detected in {window_title_re}")
                        return False
                    
                    element.set_focus()
                    element.click_input()
                    logger.info(f"✓ Clicked element [{kwargs}] in window [{window_title_re}]")
                    return True
            except Exception as e:
                logger.debug(f"Attempt {attempt+1}/{max_retries} failed: {e}")
                time.sleep(0.4)
                self._cache.invalidate(window_title_re) # Force refresh window on failure
        
        return False
    
    def read_text(self, window_title_re: str,
                  auto_id: Optional[str] = None,
                  control_type: Optional[str] = None,
                  title_re: Optional[str] = None,
                  class_name: Optional[str] = None,
                  **extra_kwargs) -> str:
        """Directly read control text (Eye-0) with security masking."""
        try:
            win = self._get_window(window_title_re, timeout=3.0)
            kwargs = extra_kwargs.copy()
            if auto_id: kwargs['auto_id'] = auto_id
            if control_type: kwargs['control_type'] = control_type
            if title_re: kwargs['title_re'] = title_re
            if class_name: kwargs['class_name'] = class_name
            
            element = win.child_window(**kwargs)
            if not element.exists(timeout=1.0): # Faster check for initial
                if kwargs.get('control_type') == 'Edit':
                    element = win.child_window(class_name='Scintilla')
            
            if element.exists(timeout=2):
                if self._is_sensitive(element):
                    logger.info(f"Read sensitive control - returning [REDACTED]")
                    return "[REDACTED]"
                text = element.window_text()
                return text if text else ""
        except Exception as e:
            logger.debug(f"Read text failed from {window_title_re}: {e}")
        return ""
    
    # --- L1: Google Desktop App Overlay ---
    
    def invoke_google_desktop(self, query: str, use_lens: bool = False) -> bool:
        """Programmatically invoke Google Desktop with fallback."""
        try:
            overlay = self._get_window(r".*(Google|Search|Gemini|Lens).*", timeout=4)
            
            # Find Edit control
            edit = overlay.child_window(control_type="Edit")
            if edit.exists(timeout=3):
                edit.set_focus()
                edit.set_edit_text(query)
            else:
                # Fallback to key typing if Edit box UIA is missing
                overlay.type_keys(query, with_spaces=True)
            
            if use_lens:
                lens_btn = overlay.child_window(
                    title_re=r"Lens|視覺搜尋|Screen",
                    control_type="Button"
                )
                if lens_btn.exists(timeout=2):
                    lens_btn.click_input()
            
            overlay.type_keys('{ENTER}')
            
            # Wait for any text component to appear (meaning it responded)
            wait_until(12, 0.5, lambda: overlay.child_window(control_type="Text").exists(timeout=1))
            return True
            
        except Exception as e:
            logger.warning(f"Invoke via pywinauto failed: {e}. Falling back to keyboard simulation.")
            import pyautogui
            pyautogui.hotkey('alt', 'space')
            time.sleep(1.0)
            pyautogui.typewrite(query, interval=0.03)
            pyautogui.press('enter')
            return True
    
    # --- Specific App Helpers (Vivado/Vitis) ---
    
    def get_vivado_tree_items(self) -> List[str]:
        """Read Vivado Project Explorer TreeView."""
        try:
            win = self._get_window(r".*Vivado.*")
            tree = win.child_window(control_type="Tree")
            if tree.exists(timeout=3):
                return [item.text() for item in tree.get_items()]
        except Exception as e:
            logger.debug(f"Failed to read Vivado tree: {e}")
        return []

    # --- Security Logic ---
    
    def _is_sensitive(self, element) -> bool:
        """Pattern matching for sensitive UI components."""
        try:
            # 1. By Control Type
            e_info = element.element_info
            if e_info.control_type in SENSITIVE_CONTROL_TYPES:
                return True
            
            # 2. By Name/Title Patterns
            text = element.window_text() or ""
            for pattern in SENSITIVE_TITLE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            
            # 3. By ClassName (e.g., Edit with 'Password' in it)
            class_name = e_info.class_name or ""
            if "password" in class_name.lower():
                return True
                
        except Exception:
            pass
        return False
