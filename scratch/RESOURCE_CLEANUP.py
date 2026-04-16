import os
import psutil
import logging
from multiprocessing import shared_memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResourceCleanup")

def kill_processes():
    target_names = [
        "pyrefly.exe",
        "language_server_windows_x64.exe",
        "Antigravity.exe",
        "python.exe" # Be careful with python.exe if running from IDE
    ]
    
    current_pid = os.getpid()
    count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Only kill things related to the current project or typical offenders
            name = proc.info['name']
            if any(t.lower() in name.lower() for t in target_names):
                if proc.info['pid'] == current_pid:
                    continue
                
                # Check cmdline to ensure it's OUR project (AutoAgent-TW)
                cmdline = " ".join(proc.info['cmdline'] or [])
                if "autoagent-TW" in cmdline.lower() or "antigravity" in name.lower() or "pyrefly" in name.lower():
                    logger.info(f"Killing process: {name} (PID: {proc.info['pid']})")
                    proc.kill()
                    count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    logger.info(f"Total processes killed: {count}")

def cleanup_shm():
    # Attempt to cleanup common buffer names
    buffers = ["PyRefly_Main_SHM", "Antigravity_Vision_Buffer"]
    for name in buffers:
        try:
            shm = shared_memory.SharedMemory(name=name)
            shm.close()
            shm.unlink()
            logger.info(f"Unlinked SHM: {name}")
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.warning(f"Failed to unlink {name}: {e}")

if __name__ == "__main__":
    logger.info("Starting Industrial-grade Resource Cleanup...")
    kill_processes()
    cleanup_shm()
    logger.info("Cleanup Complete. Memory should be recovered.")
