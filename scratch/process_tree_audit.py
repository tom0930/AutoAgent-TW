import psutil
import json
import os

def analyze_tree():
    results = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid']):
        try:
            if "antigravity" in proc.info['name'].lower() or \
               (proc.info['cmdline'] and any("antigravity" in x.lower() for x in proc.info['cmdline'])):
                results.append(proc.info)
        except:
            continue
            
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    analyze_tree()
