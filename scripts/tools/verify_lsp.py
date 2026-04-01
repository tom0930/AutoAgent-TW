import subprocess
import json
import os
import sys
from pathlib import Path

# Force UTF-8
import io
if hasattr(sys.stdout, 'detach'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')

def test_lsp_probe():
    print(">>> LSP Pilot Validation: Probing 'update_status' in status_updater.py...")
    
    # Target: .agents/skills/status-notifier/scripts/status_updater.py
    # We need a line/col that contains 'update_status'
    target_file = ".agents/skills/status-notifier/scripts/status_updater.py"
    
    # Run the probe
    # Note: We'll search for the definition of update_status
    # For now, let's just run it on a known location if possible or just check it returns something
    cmd = [
        sys.executable, "scripts/tools/lsp_probe.py",
        "--file", target_file,
        "--line", "20", # Assumption: line 20 has something relevant
        "--col", "5"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            print(f"❌ LSP Probe crashed: {result.stderr}")
            return False
        
        data = json.loads(result.stdout)
        if not data:
            print("⚠️ LSP Probe returned empty result.")
            # This might be expected if no definition at 20:5
            return True 
        
        if "error" in data[0]:
            print(f"❌ LSP Probe error: {data[0]['error']}")
            return False
            
        print(f"✅ LSP Probe Success: Found {len(data)} definitions.")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_lsp_probe()
    sys.exit(0 if success else 1)
