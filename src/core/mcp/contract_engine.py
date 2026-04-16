import hashlib
import json
import time
from typing import Dict, Any, Optional

class ContractEngine:
    """
    Phase 153: Cryptographic Verification Contract Engine.
    Generates salted SHA-256 signatures for tool execution plans to ensure 
    Human-in-the-loop integrity and prevent Agent Drift.
    """
    
    @staticmethod
    def generate_contract(thread_id: str, risk_level: int, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a sealed verification contract with a cryptographic hash.
        """
        timestamp = time.time()
        # Salt includes thread_id and timestamp to ensure uniqueness and freshness
        payload_str = json.dumps({
            "thread_id": thread_id,
            "tool_name": tool_name,
            "args": args,
            "risk_level": risk_level,
            "salt_timestamp": timestamp
        }, sort_keys=True)
        
        plan_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        return {
            "v": "1.0",
            "hash": plan_hash,
            "risk_level": risk_level,
            "tool": tool_name,
            "rationale": f"Autonomous execution of {tool_name} with risk level {risk_level} requires human validation.",
            "timestamp": timestamp,
            "thread_id": thread_id,
            "sealed_args": args
        }

    @staticmethod
    def verify_contract(contract: Dict[str, Any], current_args: Dict[str, Any]) -> bool:
        """
        Verifies if the current tool arguments match the sealed contract.
        Prevents modification of plan after user approval.
        """
        if "sealed_args" not in contract:
            return False
            
        # Strict comparison of serialized arguments
        sealed = json.dumps(contract["sealed_args"], sort_keys=True)
        current = json.dumps(current_args, sort_keys=True)
        
        return sealed == current
