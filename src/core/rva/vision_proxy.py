import logging
import time
from PIL import Image
from typing import Optional

from src.core.rva.shared_memory_manager import VisionBuffer
from src.core.rva.control_plane import VisionControlClient

logger = logging.getLogger("RVA.VisionProxy")

class VisionProxy:
    """
    High-level Proxy for communication with the PyRefly background service.
    Handles the wake/read/sleep cycle to minimize resource usage.
    """
    def __init__(self, buffer_name: str = "PyRefly_Main_SHM"):
        self.buffer_name = buffer_name
        self._buffer: Optional[VisionBuffer] = None

    def _ensure_buffer(self):
        if self._buffer is None:
            try:
                self._buffer = VisionBuffer(self.buffer_name, create=False)
            except Exception as e:
                logger.error(f"Failed to connect to VisionBuffer: {e}")
                return False
        return True

    def capture_frame(self, wait_time: float = 0.2) -> Optional[Image.Image]:
        """
        Standardized capture flow:
        1. Wake up service (RESUME)
        2. Wait for fresh frame
        3. Read from SHM
        4. Hibernate (PAUSE)
        """
        if not self._ensure_buffer():
            return None
            
        try:
            # 1. Wake up
            VisionControlClient.send_command("RESUME")
            
            # 2. Wait for a fresh frame to be captured
            time.sleep(wait_time) 
            
            # 3. Read (Zero-copy view)
            frame, fid = self._buffer.read(make_copy=False)
            
            # 4. Hibernate immediately to save CPU
            VisionControlClient.send_command("PAUSE")
            
            if frame is not None:
                # Convert numpy array view to PIL Image (PIL will handle the copy if needed internally)
                return Image.fromarray(frame)
            return None
        except Exception as e:
            logger.error(f"VisionProxy capture failed: {e}")
            return None

    def shutdown_service(self):
        """Send SHUTDOWN signal to background daemon."""
        VisionControlClient.send_command("SHUTDOWN")
        if self._buffer:
            self._buffer.close()
            self._buffer = None

# Tip(Eng): "Hibernate" implies a deeper sleep than "Standby", but both are acceptable in this context.
# Design Note: The wait_time of 200ms ensures at least 4-5 capture attempts occurred in the background.
