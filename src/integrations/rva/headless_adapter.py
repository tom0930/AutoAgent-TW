import logging

logger = logging.getLogger(__name__)

class HeadlessRVAAdapter:
    """
    Stubs out RVA (Remote Visual Automation) features when running in Headless mode.
    Prevents mechanical/GUI errors in CI environments.
    """
    def __init__(self, headless_mode: bool = False):
        self.headless_mode = headless_mode

    def perform_action(self, action_name: str, params: dict):
        """
        Intercepts GUI actions and returns a dummy success or NotImplemented.
        """
        if self.headless_mode:
            logger.warning(f"[HeadlessRVA] Intercepted GUI action '{action_name}'. Graceful degradation active.")
            return {"status": "skipped", "reason": "headless_mode"}
            
        # Real logic would be here
        raise NotImplementedError("RVA Engine not initialized.")

    def capture_screen(self):
        """
        Returns a placeholder image or empty bytes in headless mode.
        """
        if self.headless_mode:
            logger.info("[HeadlessRVA] Screen capture skipped.")
            return b""
            
        return b"REAL_SCREEN_BYTES"
