import psutil
import json
import os

def diag():
    results = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'cmdline', 'ppid', 'create_time']):
        try:
            info = proc.info
            name = info['name'].lower()
            if 'node' in name or 'python' in name:
                # Calculate resident set size in MB
                rss_mb = info['memory_info'].rss / (1024 * 1024)
                
                # Check if parent is alive
                parent_alive = False
                try:
                    if info['ppid'] > 0:
                        parent = psutil.Process(info['ppid'])
                        if parent.is_running():
                            parent_alive = True
                except:
                    pass

                results.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "rss_mb": round(rss_mb, 2),
                    "parent_alive": parent_alive,
                    "ppid": info['ppid'],
                    "cmdline": " ".join(info['cmdline']) if info['cmdline'] else ""
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    # Sort by memory usage
    results.sort(key=lambda x: x['rss_mb'], reverse=True)
    print(json.dumps(results[:20], indent=2))

if __name__ == "__main__":
    diag()
