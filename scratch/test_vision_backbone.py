import sys
import os
import time
import numpy as np
import threading
import multiprocessing

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from core.rva.shared_memory_manager import VisionBuffer
from core.rva.control_plane import VisionControlServer, VisionControlClient

def mock_producer():
    """Simulates PyRefly Vision Engine."""
    print("[Producer] Initializing VisionBuffer...")
    buffer = VisionBuffer("TestBuffer", create=True)
    
    status = {"running": True}
    
    def handle_command(cmd):
        print(f"[Producer] Received Command: {cmd}")
        if cmd == "SHUTDOWN":
            status["running"] = False
            
    server = VisionControlServer(handle_command)
    server.start()
    
    frame_id = 0
    try:
        while status["running"]:
            # Generate dummy noise frame
            frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
            buffer.write(frame, frame_id)
            if frame_id % 30 == 0:
                print(f"[Producer] Frame {frame_id} written to SHM.")
            frame_id += 1
            time.sleep(0.033) # ~30 FPS
    finally:
        server.stop()
        buffer.close()
        print("[Producer] Terminated.")

def consumer():
    """Simulates Antigravity Orchestrator."""
    time.sleep(1) # Wait for producer
    print("[Consumer] Connecting to VisionBuffer...")
    buffer = VisionBuffer("TestBuffer", create=False)
    
    # Test Read
    start_time = time.time()
    for i in range(5):
        frame, fid = buffer.read()
        if frame is not None:
            print(f"[Consumer] Read Frame {fid}, shape={frame.shape}")
        time.sleep(0.1)
    
    # Test Control Plane
    print("[Consumer] Sending SHUTDOWN signal...")
    VisionControlClient.send_command("SHUTDOWN")
    
    buffer.close()
    print("[Consumer] Terminated.")

if __name__ == "__main__":
    p = multiprocessing.Process(target=mock_producer)
    p.start()
    
    consumer()
    
    p.join(timeout=5)
    if p.is_alive():
        print("[System] Producer stuck, killing...")
        p.terminate()
    print("[System] Test Complete.")
