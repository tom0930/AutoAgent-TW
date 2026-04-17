import win32pipe
import win32file
import pywintypes
import threading
import logging
import json
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)

PIPE_NAME = r'\\.\pipe\AntigravityVisionControl'

class VisionControlServer:
    """Named Pipe Server for Vision Engine control signals."""
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info(f"Vision Control Server started on {PIPE_NAME}")

    def stop(self):
        self._running = False
        # Create a dummy client connection to break the ConnectNamedPipe block
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None, win32file.OPEN_EXISTING, 0, None
            )
            win32file.CloseHandle(handle)
        except:
            pass

    def _listen_loop(self):
        while self._running:
            try:
                # Create the pipe instance
                pipe = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1, 65536, 65536,
                    0,
                    None
                )
                
                # Wait for client to connect
                win32pipe.ConnectNamedPipe(pipe, None)
                
                # Read message
                res, data = win32file.ReadFile(pipe, 1024)
                if res == 0:
                    # pyrefly: ignore [missing-attribute]
                    cmd = data.decode('utf-8').strip()
                    logger.debug(f"Received control command: {cmd}")
                    self.callback(cmd)
                
                win32pipe.DisconnectNamedPipe(pipe)
                win32file.CloseHandle(pipe)
            except Exception as e:
                if self._running:
                    logger.error(f"Pipe Server error: {e}")
                    time.sleep(1)

class VisionControlClient:
    """Client for sending commands to the Vision Engine."""
    @staticmethod
    def send_command(command: str):
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None, win32file.OPEN_EXISTING, 0, None
            )
            
            # Use message mode
            win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            win32file.WriteFile(handle, command.encode('utf-8'))
            win32file.CloseHandle(handle)
            return True
        except pywintypes.error as e:
            logger.warning(f"Failed to send command '{command}' to Vision Engine: {e}")
            return False

# Tip(Eng): "Named Pipe" (兩字大寫時為專有名詞) is standard.
# Design Note: The server uses message mode for reliable command boundary detection.
