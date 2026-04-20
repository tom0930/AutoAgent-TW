import os
import time
import logging
import threading
import gc
import numpy as np
import mss
from typing import Optional

try:
    import win32event
    import win32api
    import winerror
except ImportError:
    win32event = None

# Setup logger before local imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PyRefly.Service")

# Add parent directory to sys.path if running as standalone
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# pyrefly: ignore [missing-import]
from src.core.rva.shared_memory_manager import VisionBuffer
# pyrefly: ignore [missing-import]
from src.core.rva.control_plane import VisionControlServer

class PyReflyService:
    def __init__(self, buffer_name: str = "PyRefly_Main_SHM"):
        self.buffer_name = buffer_name
        self.mutex_name = "Global\\Antigravity_PyRefly_Single_Instance"
        self._mutex = None
        
        # 1. Prevent Multiple Instances
        if not self._check_single_instance():
            logger.error("Another instance of PyReflyService is already running. Aborting.")
            sys.exit(0)

        self.buffer = VisionBuffer(buffer_name, create=True)
        self.control_server = VisionControlServer(self.handle_command)
        
        self._active_event = threading.Event() # True = Capture, False = Sleep
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None

    def _check_single_instance(self) -> bool:
        """Uses a Windows Mutex to ensure only one service runs."""
        if not win32event: return True
        try:
            # pyrefly: ignore [bad-argument-type]
            self._mutex = win32event.CreateMutex(None, False, self.mutex_name)
            last_error = win32api.GetLastError()
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                return False
            return True
        except Exception as e:
            logger.warning(f"Mutex check failed: {e}")
            return True

    def handle_command(self, cmd: str):
        logger.info(f"Command received: {cmd}")
        if cmd == "RESUME":
            self._active_event.set()
        elif cmd == "PAUSE":
            self._active_event.clear()
            # Explicit memory cleanup
            gc.collect()
            logger.info("Service entered Standby (Memory Flushed).")
        elif cmd == "SHUTDOWN":
            self.stop()

    def start(self):
        self._running = True
        self.control_server.start()
        
        # Start in PAUSE state by default
        self._active_event.clear()
        
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        logger.info("PyRefly Service Initialized (MSS Optimized).")

    def stop(self):
        logger.info("PyRefly Service Shutting Down...")
        self._running = False
        self._active_event.set() # Wake loop to exit
        self.control_server.stop()
        if self.buffer:
            self.buffer.close()
        if self._mutex:
            win32api.CloseHandle(self._mutex)
        logger.info("PyRefly Service Terminated.")

    def _capture_loop(self):
        frame_id = 0
        last_activity = time.time()
        AUTO_SLEEP_SEC = 300 # 5 minutes
        
        with mss.mss() as sct:
            # Primary monitor
            monitor = sct.monitors[1]
            
            while self._running:
                if not self._active_event.is_set():
                    self._active_event.wait()
                    if not self._running: break
                    logger.info("Service Woke Up.")
                    last_activity = time.time() # Reset on wake
                
                try:
                    # Optimized Capture: MSS is significantly lighter and faster
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot) # BGRA format
                    
                    # Write to SHM (Now uses optimized zero-copy in shared_memory_manager)
                    self.buffer.write(frame, frame_id)
                    frame_id = (frame_id + 1) % 1000000
                    
                    # Auto-Sleep Logic: If no one has read from the buffer (proxy logic)
                    # Or just a simple timer since last capture start.
                    # For now, we use a simple timer.
                    if time.time() - last_activity > AUTO_SLEEP_SEC:
                        logger.info("Auto-Sleep triggered: No activity for 5 minutes.")
                        self._active_event.clear()
                        gc.collect()

                    # Cleanup current loop objects to free RAM immediately
                    del frame
                    del screenshot
                    
                    # Cap at ~20 FPS
                    time.sleep(0.05)
                except Exception as e:
                    logger.error(f"Capture error: {e}")
                    time.sleep(1)

if __name__ == "__main__":
    service = PyReflyService()
    try:
        service.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
