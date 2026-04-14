import sys
import subprocess
import json
import os
from pathlib import Path

def run_flash(bin_path=None, offset=None, flash_type=None, cable_url=None):
    """
    Wrapper for Xilinx program_flash command.
    """
    # 1. Load Defaults from flash_config.json
    config_path = "_configs/flash_config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return False

    settings = config.get("flash_settings", {})
    
    # Use provided values or fall back to defaults
    target_bin = bin_path or settings.get("bin_path", "./build/firmware.bin")
    target_offset = offset or settings.get("default_offset", "0x0")
    target_type = flash_type or settings.get("flash_type", "qspi-x4-single")
    target_url = cable_url or settings.get("cable_url", "TCP:127.0.0.1:3121")
    flash_tool = settings.get("program_flash_bin", "program_flash")

    # 2. Build the command
    # Command Pattern: program_flash -f <path> -offset <offset> -flash_type <type> -url <url>
    cmd = [
        flash_tool,
        "-f", str(Path(target_bin).absolute()),
        "-offset", target_offset,
        "-flash_type", target_type,
        "-url", target_url
    ]

    print(f"[Flash Tool] Executing: {' '.join(cmd)}")
    
    # 3. Execution (Dry-run if needed, but here we attempt real execution)
    try:
        # We use shell=True on Windows for program_flash if it's a batch file/alias
        process = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("Success: Flash completed.")
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Flash failed.")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: '{flash_tool}' not found. Please ensure Xilinx Vitis is in your PATH.")
        return False

if __name__ == "__main__":
    # Internal CLI for Agent
    # Example: python flash.py ./build/my.bin 0x40000
    p_bin = sys.argv[1] if len(sys.argv) > 1 else None
    p_offset = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = run_flash(bin_path=p_bin, offset=p_offset)
    sys.exit(0 if success else 1)
