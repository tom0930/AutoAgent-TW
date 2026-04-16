import psutil
import os
import sys
from pathlib import Path

def get_dir_size(path='.'):
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total

def audit_system():
    # 1. Memory Analysis
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            info = proc.info
            rss = info['memory_info'].rss / (1024 * 1024)
            processes.append((info['pid'], info['name'], rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    processes.sort(key=lambda x: x[2], reverse=True)
    
    print("=" * 80)
    print(f"{'TOP 15 Memory Consumers':^80}")
    print("-" * 80)
    print(f"{'PID':<10} {'Name':<30} {'RSS Memory (MB)':<15}")
    for pid, name, rss in processes[:15]:
        print(f"{pid:<10} {name:<30} {rss:<15.2f}")
    
    # 2. Workspace File Analysis
    print("\n" + "=" * 80)
    print(f"{'TOP 10 Largest Files in Workspace':^80}")
    print("-" * 80)
    files = []
    workspace = Path(".")
    for f in workspace.rglob('*'):
        if f.is_file():
            try:
                files.append((f, f.stat().st_size / (1024 * 1024)))
            except (OSError, PermissionError):
                continue
    
    files.sort(key=lambda x: x[1], reverse=True)
    print(f"{'Size (MB)':<15} {'Path'}")
    for f_path, size in files[:10]:
        print(f"{size:<15.2f} {f_path}")

    # 3. Overall stats
    mem = psutil.virtual_memory()
    print("\n" + "=" * 80)
    print(f"System Total Memory: {mem.total / (1024**3):.2f} GB")
    print(f"System Used Memory:  {mem.used / (1024**3):.2f} GB ({mem.percent}%)")

if __name__ == "__main__":
    audit_system()
