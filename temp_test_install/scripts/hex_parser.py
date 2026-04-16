import struct
import re
import json
import sys
from pathlib import Path

def parse_with_endian(hex_bytes, format_type="I", mode="LSB"):
    """
    mode: "LSB" (Little-Endian, Python: <) 
          "MSB" (Big-Endian, Python: >)
    format_type: "I" (uint32), "H" (uint16), "f" (float), "B" (uint8)
    """
    prefix = "<" if mode == "LSB" else ">"
    try:
        # Unpack according to type
        value = struct.unpack(f"{prefix}{format_type}", hex_bytes)[0]
        return value
    except Exception as e:
        return f"Error: {str(e)}"

def get_bit_range(value, start_bit, end_bit):
    """
    Get specific bits from a value (e.g., bit[14:12])
    """
    if not isinstance(value, int):
        return None
    mask = (1 << (end_bit - start_bit + 1)) - 1
    return (value >> start_bit) & mask

def parse_hex_dump(raw_text, mode="LSB"):
    """
    Extract hex values from raw UART text and parse common header/status fields.
    Example Input: "00004000: 78 56 34 12 00 00 80 3F"
    """
    # Extract all hex-looking pairs
    hex_pattern = re.compile(r'([0-9A-Fa-f]{2})')
    all_bytes = hex_pattern.findall(raw_text)
    
    if not all_bytes:
        return {"error": "No hex data found in input."}
        
    bytes_data = bytes([int(b, 16) for b in all_bytes])
    
    results = {
        "raw_len": len(bytes_data),
        "fields": [],
        "hex_string": " ".join(all_bytes)
    }
    
    # Example parsing logic for MicroBlaze firmware context
    # Assume first 4 bytes is a status or marker
    if len(bytes_data) >= 4:
        marker = parse_with_endian(bytes_data[:4], "I", mode)
        results["fields"].append({
            "name": "Head_Marker",
            "value": hex(marker) if isinstance(marker, int) else marker,
            "interpretation": "Standard Magic" if marker == 0xAA995566 else "Unknown"
        })
        
    # Assume next 4 bytes could be a system tick or status bitfield
    if len(bytes_data) >= 8:
        status_reg = parse_with_endian(bytes_data[4:8], "I", mode)
        if isinstance(status_reg, int):
            results["fields"].append({
                "name": "Status_Register",
                "value": hex(status_reg),
                "bits": {
                    "Error_Bit_14": get_bit_range(status_reg, 14, 14),
                    "Ready_Bit_0": get_bit_range(status_reg, 0, 0)
                }
            })

    return results

if __name__ == "__main__":
    # Internal CLI for Agent to call via subprocess if needed
    if len(sys.argv) > 1:
        # Example: python hex_parser.py "66 55 99 AA"
        input_text = " ".join(sys.argv[1:])
        print(json.dumps(parse_hex_dump(input_text), indent=2))
