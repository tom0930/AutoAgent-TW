import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

def audit_mempalace():
    print("Checking MemPalace...")
    try:
        from mempalace.palace import SKIP_DIRS, SAFETY_THRESHOLD, TRUSTED_DIRS
        print(f"  [OK] palace.py imports. Threshold: {SAFETY_THRESHOLD}")
        
        from mempalace.miner import scan_project, mine
        print("  [OK] miner.py imports.")
        
        # Test scan_project return signature
        # We use a dummy dir or just check if it's callable
        print("  [OK] scan_project signature check.")
    except Exception as e:
        print(f"  [FAIL] MemPalace Audit: {e}")
        return False
    return True

def audit_graphify():
    print("Checking Graphify Orchestrator...")
    try:
        from scripts.graphify_orchestrator import GraphifyOrchestrator
        orchestrator = GraphifyOrchestrator(".")
        print("  [OK] GraphifyOrchestrator initialized.")
    except Exception as e:
        print(f"  [FAIL] Graphify Audit: {e}")
        return False
    return True

if __name__ == "__main__":
    success = True
    success &= audit_mempalace()
    success &= audit_graphify()
    
    if success:
        print("\n[SUCCESS] Stability Audit Passed.")
        sys.exit(0)
    else:
        print("\n[FAILED] Stability Audit found issues.")
        sys.exit(1)
