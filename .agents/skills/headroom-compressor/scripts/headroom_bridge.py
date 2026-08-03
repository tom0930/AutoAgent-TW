#!/usr/bin/env python3
"""
Headroom Bridge Gateway for AutoAgent-TW / Antigravity
Provides seamless context compression using Headroom SDK.
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HeadroomBridge")

def compress_payload(data: dict) -> dict:
    try:
        from headroom import compress
        # Assuming payload contains 'messages'
        messages = data.get("messages", [])
        if not messages:
            logger.warning("No messages found in payload to compress.")
            return data
        
        compressed = compress(messages)
        return {"compressed": True, "result": compressed}
    except ImportError:
        logger.error("headroom-ai module not installed. Please run: pip install -e z:\\headroom[all]")
        return {"error": "headroom-ai missing", "raw": data}
    except Exception as e:
        logger.error(f"Error during headroom compression: {e}")
        return {"error": str(e), "raw": data}

if __name__ == "__main__":
    test_data = {
        "messages": [
            {"role": "user", "content": "Hello Headroom!"},
            {"role": "system", "content": "System operational test for AutoAgent-TW integration."}
        ]
    }
    print("Testing Headroom Bridge Integration...")
    res = compress_payload(test_data)
    print(json.dumps(res, indent=2, ensure_ascii=False))
