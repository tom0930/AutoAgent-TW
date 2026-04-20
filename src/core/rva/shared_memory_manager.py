import numpy as np
import struct
import logging
from multiprocessing import shared_memory
from typing import Optional, Tuple

try:
    import win32event
    import win32api
    import win32con
except ImportError:
    # Fallback for non-windows environments
    win32event = None
    win32con = None

logger = logging.getLogger(__name__)

class VisionBuffer:
    """
    Zero-copy Shared Memory Buffer for high-performance vision data transport.
    Layout:
    - [0-3]: Width (int32)
    - [4-7]: Height (int32)
    - [8-11]: Channels (int32)
    - [12-15]: FrameID (int32)
    - [16-]: Raw Data (RGBA)
    """
    METADATA_SIZE = 16
    MAX_BUFFER_SIZE = 4096 * 2160 * 4 + METADATA_SIZE # Max 4K RGBA
    
    def __init__(self, name: str, create: bool = False):
        self.name = name
        self.shm: Optional[shared_memory.SharedMemory] = None
        self.create = create
        self._mutex = None
        
        # Mutex name must be unique globally on Windows
        self.mutex_name = f"Global\\Antigravity_SHM_Mutex_{name}"
        
        try:
            if create:
                # Cleanup existing if any (avoid resource leak)
                for _ in range(2): # Try twice
                    try:
                        temp = shared_memory.SharedMemory(name=name)
                        temp.close()
                        temp.unlink()
                        logger.info(f"Cleaned up existing SHM: {name}")
                        break
                    except (FileNotFoundError, PermissionError):
                        break
                    except Exception as e:
                        logger.warning(f"Error cleaning SHM {name}: {e}")
                        break
                
                self.shm = shared_memory.SharedMemory(name=name, create=True, size=self.MAX_BUFFER_SIZE)
                if win32event:
                    # pyrefly: ignore [bad-argument-type]
                    self._mutex = win32event.CreateMutex(None, False, self.mutex_name)
            else:
                self.shm = shared_memory.SharedMemory(name=name)
                if win32event:
                    # MUTEX_ALL_ACCESS = 0x1F0001
                    self._mutex = win32event.OpenMutex(0x1F0001, False, self.mutex_name)
        except Exception as e:
            logger.error(f"Failed to initialize VisionBuffer {name}: {e}")
            raise

    def write(self, frame: np.ndarray, frame_id: int):
        """Write frame to shared memory (Server/Producer side)"""
        if not self.create:
            raise PermissionError("Only creator can write to SHM")
            
        h, w, c = frame.shape
        data_size = h * w * c
        
        if data_size + self.METADATA_SIZE > self.MAX_BUFFER_SIZE:
            raise ValueError(f"Frame size {data_size} exceeds buffer capacity {self.MAX_BUFFER_SIZE}")

        # Basic Mutex Lock (Wait max 100ms)
        if self._mutex:
            # pyrefly: ignore [missing-attribute]
            win32event.WaitForSingleObject(self._mutex, 100)
        
        try:
            # Write Metadata
            meta = struct.pack("IIII", w, h, c, frame_id)
            # pyrefly: ignore [missing-attribute]
            self.shm.buf[0:self.METADATA_SIZE] = meta
            
            # Write Pixel Data
            # Optimized: Use ravel() and direct buffer assignment to avoid frame.tobytes() 
            # which creates a massive intermediate bytes object (35MB per frame).
            # pyrefly: ignore [missing-attribute]
            self.shm.buf[self.METADATA_SIZE : self.METADATA_SIZE + data_size] = frame.ravel()
        finally:
            if self._mutex:
                # pyrefly: ignore [missing-attribute]
                win32event.ReleaseMutex(self._mutex)

    def read(self, make_copy: bool = True) -> Tuple[Optional[np.ndarray], int]:
        """Read frame from shared memory (Client/Consumer side)"""
        if self._mutex:
            # pyrefly: ignore [missing-attribute]
            win32event.WaitForSingleObject(self._mutex, 100)
            
        try:
            # Read Metadata
            # pyrefly: ignore [missing-attribute]
            meta = bytes(self.shm.buf[0:self.METADATA_SIZE])
            w, h, c, frame_id = struct.unpack("IIII", meta)
            
            if w == 0 or h == 0:
                return None, 0
                
            # Zero-copy Read: Create ndarray view pointing to SHM buffer
            # pyrefly: ignore [missing-attribute]
            frame = np.ndarray((h, w, c), dtype=np.uint8, buffer=self.shm.buf, offset=self.METADATA_SIZE)
            
            # Use view if requested to save memory (high risk of tearing if producer writes)
            if not make_copy:
                return frame, frame_id
            return frame.copy(), frame_id
        finally:
            if self._mutex:
                # pyrefly: ignore [missing-attribute]
                win32event.ReleaseMutex(self._mutex)

    def close(self):
        if self.shm:
            self.shm.close()
            if self.create:
                self.shm.unlink()
        if self._mutex:
            win32api.CloseHandle(self._mutex)
            self._mutex = None

# Tip(Eng): "Write Metadata" is more standard than "Writing the Meta-data".
# Design Note: Using Global\\ prefix for Mutex ensures cross-session synchronization
# if Windows session isolation is active.
