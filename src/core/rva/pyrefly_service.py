import os
import time
import logging
import threading
import gc
import numpy as np
import pyautogui
from typing import Optional

# Setup logger before local imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PyRefly.Service")

# Add parent directory to sys.path if running as standalone
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.rva.shared_memory_manager import VisionBuffer
from src.core.rva.control_plane import VisionControlServer

class PyReflyService:
    def __init__(self, buffer_name: str = "PyRefly_Main_SHM"):
        self.buffer_name = buffer_name
        self.buffer = VisionBuffer(buffer_name, create=True)
        self.control_server = VisionControlServer(self.handle_command)
        
        self._active_event = threading.Event() # True = Capture, False = Sleep
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None

    def handle_command(self, cmd: str):
        logger.info(f"Command received: {cmd}")
        if cmd == "RESUME":
            self._active_event.set()
        elif cmd == "PAUSE":
            self._active_event.clear()
            # Flush memory on pause
            gc.collect()
            logger.info("Service entered Standby (Memory Flushed).")
        elif cmd == "SHUTDOWN":
            self.stop()

    def start(self):
        self._running = True
        self.control_server.start()
        
        # Start in PAUSE state by default to save resources
        self._active_event.clear()
        
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        logger.info("PyRefly Service Initialized in STANDBY mode.")

    def stop(self):
        logger.info("PyRefly Service Shutting Down...")
        self._running = False
        self._active_event.set() # Wake loop to exit
        self.control_server.stop()
        if self.buffer:
            self.buffer.close()
        logger.info("PyRefly Service Terminated.")

    def _capture_loop(self):
        frame_id = 0
        while self._running:
            # Wait until active
            if not self._active_event.is_set():
                self._active_event.wait()
                if not self._running: break
                logger.info("Service Woke Up.")
            
            try:
                # Capture screen accurately
                # PyAutoGUI screenshot is quite heavy (creates PIL image)
                # Future Optimization: Use Win32 BitBlt directly to avoid PIL intermediate
                shot = pyautogui.screenshot()
                frame = np.array(shot) # RGB order
                
                # Write to SHM
                self.buffer.write(frame, frame_id)
                frame_id += 4 # Increment by 4 for tracking
                
                # Dynamic FPS control: Max ~20 FPS in active mode
                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Capture error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    service = PyReflyService()
    try:
        service.start()
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
