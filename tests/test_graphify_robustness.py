import subprocess
import os
from pathlib import Path

def test_cli_commands():
    project_root = Path("z:/AutoAgent-TW")
    script_path = project_root / "scripts" / "aa_graphify.py"
    
    print("[*] Testing 'aa-graphify status'...")
    res = subprocess.run(["python", str(script_path), "status"], capture_output=True, text=True)
    assert res.returncode == 0
    print("  - OK")

    print("[*] Testing 'aa-graphify query' (dry run)...")
    # Using a simple query to check if it triggers the graphify logic
    res = subprocess.run(["python", str(script_path), "query", "What is Orchestration?"], capture_output=True, text=True)
    # Even if it fails to find nodes, it should return code 0 if the plumbing works
    assert res.returncode == 0
    print("  - OK")

    print("[*] Verifying file paths...")
    status_json = project_root / ".planning" / "graphify-out" / "status.json"
    if status_json.exists():
        print(f"  - Found status.json at {status_json}")
    else:
        print(f"  - [!] status.json missing (expected if not run yet)")

if __name__ == "__main__":
    try:
        test_cli_commands()
        print("\n[✅] ALL PLUMBING TESTS PASSED.")
    except Exception as e:
        print(f"\n[❌] TEST FAILED: {e}")
        exit(1)
