import sys
import os
import json
from pathlib import Path

def verify_firmware(bin_path, config_path="_configs/flash_config.json"):
    """
    Check if the firmware binary matches expectations defined in config.
    """
    if not os.path.exists(bin_path):
        return {"status": "ERROR", "message": f"File not found: {bin_path}"}
    
    # Load requirements
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        return {"status": "ERROR", "message": f"Failed to load config: {str(e)}"}
        
    integrity = config.get("data_integrity", {})
    expected_magic = integrity.get("header_magic", "0xAA995566")
    endian = integrity.get("endianness", "LSB")
    
    file_size = os.path.getsize(bin_path)
    if file_size == 0:
        return {"status": "ERROR", "message": "Binary file is empty."}
        
    # Read first 4 bytes
    with open(bin_path, 'rb') as f:
        header = f.read(4)
        
    # Convert magic string to bytes for comparison
    magic_val = int(expected_magic, 16)
    if endian == "LSB":
        expected_bytes = magic_val.to_bytes(4, byteorder='little')
    else:
        expected_bytes = magic_val.to_bytes(4, byteorder='big')
        
    if header == expected_bytes:
        return {
            "status": "PASS",
            "message": "Header magic match.",
            "file_size": file_size,
            "magic_found": expected_magic
        }
    else:
        actual_hex = header.hex().upper()
        # Common error: Wrong endianness
        swapped_bytes = header[::-1]
        msg = f"Magic mismatch. Expected {expected_magic}, found {actual_hex} (hex)."
        if swapped_bytes == expected_bytes:
            msg += " (Warning: Endianness seems swapped!)"
            
        return {"status": "FAIL", "message": msg}

if __name__ == "__main__":
    # Usage: python pre_flash_verify.py [path_to_bin]
    target = sys.argv[1] if len(sys.argv) > 1 else "./build/firmware.bin"
    result = verify_firmware(target)
    print(json.dumps(result, indent=2))
    
    if result["status"] != "PASS":
        sys.exit(1)
