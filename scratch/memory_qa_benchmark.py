import time
import psutil
import logging
import numpy as np
from src.core.rva.vision_proxy import VisionProxy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA.MemoryAudit")

def run_memory_audit():
    proxy = VisionProxy()
    pyrefly_proc = None
    
    # Locate pyrefly process
    for proc in psutil.process_iter(['name']):
        if "pyrefly" in proc.info['name'].lower():
            pyrefly_proc = proc
            break
            
    if not pyrefly_proc:
        logger.error("PyRefly service not found. Running proxy once to spawn (if using spawn manager)...")
        proxy.capture_frame()
        time.sleep(2)
        for proc in psutil.process_iter(['name']):
            if "pyrefly" in proc.info['name'].lower():
                pyrefly_proc = proc
                break
    
    if not pyrefly_proc:
        logger.error("Still no pyrefly found. Aborting.")
        return

    logger.info(f"Monitoring PID {pyrefly_proc.pid} ({pyrefly_proc.name()})")
    
    ram_usage = []
    
    for i in range(20):
        img = proxy.capture_frame(wait_time=0.1)
        ws = pyrefly_proc.memory_info().rss / (1024*1024)
        ram_usage.append(ws)
        if i % 5 == 0:
            logger.info(f"Iteration {i}: RAM = {ws:.2f} MB")
        time.sleep(0.1)
        
    avg_ram = sum(ram_usage) / len(ram_usage)
    max_ram = max(ram_usage)
    min_ram = min(ram_usage)
    
    logger.info("--- Phase 149 Memory Metrics ---")
    logger.info(f"Min RAM: {min_ram:.2f} MB")
    logger.info(f"Max RAM: {max_ram:.2f} MB")
    logger.info(f"Avg RAM: {avg_ram:.2f} MB")
    
    if max_ram < 200:
        logger.info("QA PASS: Memory is within industrial bounds (< 200MB).")
    else:
        logger.error(f"QA FAIL: Memory {max_ram:.2f} MB exceeds 200MB limit.")

if __name__ == "__main__":
    run_memory_audit()
