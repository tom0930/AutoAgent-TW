import sys
import os
import time
import unittest
import numpy as np
import psutil
from threading import Thread

# Project Root Setup
sys.path.append(os.getcwd())

from src.core.rva.pyrefly_service import PyReflyService
from src.core.rva.vision_proxy import VisionProxy
from src.core.rva.control_plane import VisionControlClient

class TestVisionLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We start the service in a background thread for in-process testing
        # In real life it is a subprocess, but thread testing validates the logic just as well
        cls.service = PyReflyService(buffer_name="QA_Test_SHM")
        cls.service_thread = Thread(target=cls.service.start, daemon=True)
        cls.service_thread.start()
        time.sleep(2) # Initial boot
        cls.proxy = VisionProxy(buffer_name="QA_Test_SHM")

    @classmethod
    def tearDownClass(cls):
        cls.service.stop()

    def test_01_standby_on_boot(self):
        """Verify service starts in standby (Active event is not set)."""
        self.assertFalse(self.service._active_event.is_set())
        print("[QA] Standby on boot confirmed.")

    def test_02_wake_and_capture(self):
        """Verify proxy can wake the service and receive a frame."""
        frame = self.proxy.capture_frame(wait_time=0.5)
        self.assertIsNotNone(frame, "Should receive a frame when captured via Proxy")
        self.assertIsInstance(frame.size, tuple)
        print(f"[QA] Wake and capture successful: {frame.size}")
        
        # After capture_frame, it should return to standby
        self.assertFalse(self.service._active_event.is_set(), "Service should be PAUSED after capture_frame")

    def test_03_shm_integrity(self):
        """Verify the frame data coming from SHM is valid numpy/PIL compatible."""
        frame = self.proxy.capture_frame()
        arr = np.array(frame)
        self.assertEqual(len(arr.shape), 3, "Should be a 3D RGB/RGBA array")
        self.assertGreater(arr.mean(), 0, "Image should not be pitch black (usually)")
        print(f"[QA] SHM Integrity verified. Mean intensity: {arr.mean():.2f}")

    def test_04_shutdown_signal_manual(self):
        """Verify the service responds to SHUTDOWN via Named Pipe."""
        res = VisionControlClient.send_command("SHUTDOWN")
        self.assertTrue(res, "Command should be sent successfully")
        time.sleep(1)
        self.assertFalse(self.service._running, "Service _running flag should be False after SHUTDOWN")

if __name__ == "__main__":
    # Note: Using cls in setUpClass requires special care or just global access
    # Refactoring slightly for standard unittest runner
    unittest.main()
