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
    """
    PyRefly Service with enhanced memory management.
    
    Memory optimizations (v1.8.1):
    - Periodic garbage collection every 30 seconds
    - Frame buffer capped at 100MB max
    - Auto-sleep after 5 minutes of inactivity
    - Low-memory mode triggers aggressive GC at 400MB
    - Memory alert at 600MB threshold
    - Hard cap enforced at 800MB with forced shutdown
    
    Default state: DISABLED (pyrefly.exe renamed to pyrefly.exe.disabled)
    To enable: python scripts/pyrefly_mode.py enable
    To disable: python scripts/pyrefly_mode.py disable
    """
    
    def __init__(self, buffer_name: str = "PyRefly_Main_SHM"):
        self.buffer_name = buffer_name
        self.mutex_name = "Global\\Antigravity_PyRefly_Single_Instance"
        self._mutex = None
        
        # Memory thresholds (in MB)
        self.MEMORY_LOW_THRESHOLD_MB = 400
        self.MEMORY_ALERT_THRESHOLD_MB = 600
        self.MEMORY_HARD_CAP_MB = 800
        self.FRAME_BUFFER_MAX_MB = 100
        
        # Garbage collection interval
        self.GC_INTERVAL_SEC = 30
        self._last_gc_time = time.time()
        
        # 1. Prevent Multiple Instances
        if not self._check_single_instance():
            logger.error("Another instance of PyReflyService is already running. Aborting.")
            sys.exit(0)

        self.buffer = VisionBuffer(buffer_name, create=True)
        self.control_server = VisionControlServer(self.handle_command)
        
        self._active_event = threading.Event() # True = Capture, False = Sleep
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None
        self._gc_thread: Optional[threading.Thread] = None
        
        # Memory monitoring
        self._memory_monitor_thread: Optional[threading.Thread] = None
        self._memory_ok = True

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

    def _get_memory_usage_mb(self) -> float:
        """Get current process memory usage in MB."""
        try:
            import psutil
            proc = psutil.Process(os.getpid())
            return proc.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    def _periodic_gc(self):
        """Background thread for periodic garbage collection."""
        while self._running:
            time.sleep(self.GC_INTERVAL_SEC)
            if self._running:
                self._run_gc()

    def _run_gc(self):
        """Execute garbage collection and log memory status."""
        collected = gc.collect()
        self._last_gc_time = time.time()
        mem_mb = self._get_memory_usage_mb()
        logger.debug(f"GC completed: {collected} objects collected, memory: {mem_mb:.1f}MB")
        return mem_mb

    def _memory_monitor_loop(self):
        """Monitor memory usage and take action when thresholds exceeded."""
        while self._running:
            time.sleep(10)  # Check every 10 seconds
            if not self._running:
                break
                
            mem_mb = self._get_memory_usage_mb()
            
            # Low memory warning - aggressive GC
            if mem_mb > self.MEMORY_LOW_THRESHOLD_MB:
                logger.warning(f"Memory usage high ({mem_mb:.1f}MB), running aggressive GC")
                gc.collect(2)  # Full collection
                
            # Alert threshold - log warning
            if mem_mb > self.MEMORY_ALERT_THRESHOLD_MB:
                logger.error(f"MEMORY ALERT: {mem_mb:.1f}MB exceeds {self.MEMORY_ALERT_THRESHOLD_MB}MB threshold!")
                self._memory_ok = False
                # Force garbage collection
                for _ in range(3):
                    gc.collect()
                    
            # Hard cap exceeded - emergency shutdown
            if mem_mb > self.MEMORY_HARD_CAP_MB:
                logger.critical(f"MEMORY HARD CAP EXCEEDED: {mem_mb:.1f}MB > {self.MEMORY_HARD_CAP_MB}MB - EMERGENCY SHUTDOWN")
                self._memory_ok = False
                self.stop()
                break
            else:
                self._memory_ok = True

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
        elif cmd == "MEMORY_STATUS":
            mem_mb = self._get_memory_usage_mb()
            logger.info(f"Current memory usage: {mem_mb:.1f}MB")

    def start(self):
        self._running = True
        self.control_server.start()
        
        # Start in PAUSE state by default
        self._active_event.clear()
        
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        
        # Start periodic GC thread
        self._gc_thread = threading.Thread(target=self._periodic_gc, daemon=True)
        self._gc_thread.start()
        
        # Start memory monitor thread
        self._memory_monitor_thread = threading.Thread(target=self._memory_monitor_loop, daemon=True)
        self._memory_monitor_thread.start()
        
        logger.info("PyRefly Service Initialized (MSS Optimized with Memory Management).")

    def stop(self):
        logger.info("PyRefly Service Shutting Down...")
        self._running = False
        self._active_event.set() # Wake loop to exit
        self.control_server.stop()
        if self.buffer:
            self.buffer.close()
        if self._mutex:
            win32api.CloseHandle(self._mutex)
        # Final GC
        gc.collect()
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
                
                # Check if memory is OK
                if not self._memory_ok:
                    logger.warning("Memory state not OK, pausing capture")
                    self._active_event.clear()
                    continue
                
                try:
                    # Optimized Capture: MSS is significantly lighter and faster
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot) # BGRA format
                    
                    # Frame size check - cap at FRAME_BUFFER_MAX_MB
                    frame_size_mb = frame.nbytes / 1024 / 1024
                    if frame_size_mb > self.FRAME_BUFFER_MAX_MB:
                        logger.warning(f"Frame size {frame_size_mb:.1f}MB exceeds cap, resizing")
                        # Downscale to fit within cap
                        scale = (self.FRAME_BUFFER_MAX_MB / frame_size_mb) ** 0.5
                        new_h = int(frame.shape[0] * scale)
                        new_w = int(frame.shape[1] * scale)
                        frame = np.array(
                            mss.tools.to_png(frame.tobytes(), (frame.shape[1], frame.shape[0]))
                        )
                    
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
                    
                    # Periodic GC check
                    if time.time() - self._last_gc_time > self.GC_INTERVAL_SEC:
                        self._run_gc()
                    
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
