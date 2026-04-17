import subprocess
import os
import json
import time
from typing import Dict, List, Any, Optional
# pyrefly: ignore [missing-import]
from src.core.skill_manifest import SkillManifest

class SkillSandboxTester:
    """
    AutoSkills Sandbox Tester (Phase 2 - Task 2.2).
    Simulates isolated execution of skill tests and permission validation.
    """
    def __init__(self, sandbox_temp_dir: str = "temp/sandbox"):
        self.sandbox_temp_dir = sandbox_temp_dir
        os.makedirs(self.sandbox_temp_dir, exist_ok=True)

    def run_test_isolated(self, manifest: SkillManifest, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs a skill test case and validates permission compliance.
        In a production environment, this would spawn a Docker container.
        Here we use a subprocess with restricted environment variables and mocked validation.
        """
        tool_call = test_case.get("tool_call", {})
        expected_output = test_case.get("expected", "")
        
        # 1. Static Permission Check
        print(f"[{manifest.name}] Starting Sandbox Test: {test_case.get('id', 'unknown')}")
        
        # Check if tool is allowed
        allowed_tools = manifest.permissions.tools
        if tool_call.get("name") not in allowed_tools and tool_call.get("name") != "default":
            return {
                "success": False,
                "error": f"Permission Denied: Tool '{tool_call.get('name')}' is used but NOT declared in manifest.json."
            }

        # 2. Execution (Mocked)
        # In a real scenario, this would execute the actual script in 'scripts/'
        # Example check for system run permissions
        if tool_call.get("name") == "system_run":
            cmd = tool_call.get("args", {}).get("cmd", "")
            allowed_cmds = manifest.permissions.system.run if manifest.permissions.system else []
            if cmd.split()[0] not in allowed_cmds:
                return {
                    "success": False,
                    "error": f"Permission Denied: System command '{cmd}' is unauthorized for this skill."
                }

        # 3. Validation Logic
        # Simulating a successful run
        time.sleep(0.5)
        simulated_output = tool_call.get("args", {}).get("test_input", "Mock Result")
        
        return {
            "success": True,
            "actual_output": simulated_output,
            "pass_expected": simulated_output == expected_output or expected_output == "*",
            "audit_log": f"Test executed tool '{tool_call.get('name')}' within sandbox limits."
        }

    def validate_full_skill(self, skill_path: str) -> Dict[str, Any]:
        """Full validation of a skill package."""
        manifest_path = os.path.join(skill_path, "manifest.json")
        if not os.path.exists(manifest_path):
            return {"success": False, "error": "manifest.json not found"}

        try:
            with open(manifest_path, "r") as f:
                manifest = SkillManifest(**json.load(f))
        except Exception as e:
            return {"success": False, "error": f"Invalid manifest: {str(e)}"}
            
        test_dir = os.path.join(skill_path, "tests")
        if not os.path.exists(test_dir):
            return {"success": True, "warning": "No tests/ directory found, only static scan performed."}
            
        test_reports = []
        for test_file in os.listdir(test_dir):
            if not test_file.endswith(".json"): continue
            with open(os.path.join(test_dir, test_file), "r") as f:
                test_cases = json.load(f)
                if isinstance(test_cases, dict): test_cases = [test_cases]
                
                for case in test_cases:
                    report = self.run_test_isolated(manifest, case)
                    test_reports.append({"id": case.get("id"), "report": report})
                    
        return {
            "success": all(r["report"]["success"] for r in test_reports),
            "manifest_validated": True,
            "reports": test_reports
        }

if __name__ == "__main__":
    print("Testing Sandbox Tester Engine...")
    tester = SkillSandboxTester()
    
    # Mock Skill Case: selenium-test
    mock_manifest = SkillManifest(
        name="selenium-test", version="1.0", description="Test browser",
        permissions={"gui": {"click": True}, "tools": ["browser"]}
    )
    
    # Test case: Valid call
    test_valid = {"id": "T001", "tool_call": {"name": "browser", "args": {"test_input": "OK"}}, "expected": "OK"}
    # Test case: Invalid call (unauthorized tool)
    test_invalid = {"id": "T002", "tool_call": {"name": "delete_file", "args": {}}, "expected": "*"}
    
    print(f"\n--- Running VALID Test (T001) ---")
    print(tester.run_test_isolated(mock_manifest, test_valid))
    
    print(f"\n--- Running INVALID Test (T002) - Unauthorized tool ---")
    print(tester.run_test_isolated(mock_manifest, test_invalid))
