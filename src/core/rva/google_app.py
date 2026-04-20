# src/core/rva/google_app.py — Phase 158: Google Desktop AI Synergy (v2)

import logging
import time
from typing import Optional, List
from .gui_control import PywinautoController

logger = logging.getLogger("RVA.GoogleApp")

class GoogleAppController:
    """H1: Advanced controller for Google Desktop App (WGA_MainWindow) synergy."""
    
    def __init__(self, controller: Optional[PywinautoController] = None):
        self.ctrl = controller or PywinautoController(primary_backend="uia")
        self.window_title_re = "Google app"
    
    def _get_app_window(self):
        return self.ctrl._get_window(self.window_title_re)

    def is_running(self) -> bool:
        try:
            self._get_app_window()
            return True
        except Exception:
            return False

    def ensure_visible(self) -> bool:
        """Restore and bring the Google App to the foreground."""
        try:
            win = self._get_app_window()
            if win.is_minimized():
                win.restore()
            win.set_focus()
            return True
        except Exception as e:
            logger.error(f"Failed to bring Google App to focus: {e}")
            return False

    def perform_search(self, query: str) -> bool:
        """Type a query into the search box and press enter."""
        try:
            self.ensure_visible()
            win = self._get_app_window()
            
            # Robust Search Box Location
            # We try common identifiers for the Google search box
            search_box = None
            locators = [
                {"auto_id": "qsb-textarea"}, # Gemini/Search mode
                {"title": "Ask anything"},
                {"auto_id": "APjFqb"},      # Classic Search
                {"control_type": "Edit"}    # Fallback first edit
            ]
            
            for loc in locators:
                try:
                    # Using descendants helps find nested Chromium nodes
                    candidate = win.child_window(**loc, found_index=0)
                    if candidate.exists(timeout=0.5):
                        search_box = candidate
                        break
                except:
                    continue
            
            if not search_box:
                raise RuntimeError("Could not locate Google search box.")

            search_box.set_focus()
            search_box.type_keys(f"{query}{{ENTER}}", with_spaces=True)
            logger.info(f"Triggered Google search for: {query}")
            return True
        except Exception as e:
            logger.error(f"Failed to perform Google search: {e}")
            return False

    def extract_content(self, timeout: float = 5.0) -> str:
        """Extract results using an optimized UIA descendants text crawl."""
        try:
            win = self._get_app_window()
            # Ensure visible for text population
            if win.is_minimized():
                win.restore()
            
            # Using find_elements with control_type is often much faster than generic descendants()
            # for complex WebView structures
            texts = []
            elements = win.descendants(control_type="Text")
            for item in elements:
                try:
                    # Defensive check for text property
                    t = item.window_text()
                    if t and len(t.strip()) > 0:
                        texts.append(t.strip())
                except:
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_texts = []
            for t in texts:
                if t not in seen:
                    unique_texts.append(t)
                    seen.add(t)
            
            return "\n".join(unique_texts)
        except Exception as e:
            logger.warning(f"Google App extraction failed: {e}")
            return ""

    def minimize(self) -> bool:
        try:
            win = self._get_app_window()
            win.minimize()
            return True
        except Exception as e:
            logger.error(f"Failed to minimize: {e}")
            return False

if __name__ == "__main__":
    ga = GoogleAppController()
    if ga.is_running():
        ga.perform_search("current time in Taipei")
        time.sleep(3)
        print(ga.extract_content())
