import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("Core.Security.SandboxEvaluator")

class SandboxEvaluator:
    """
    L5 Defense: Predicts risk of execution before it happens.
    Simulates a 'Pre-flight Check' for dangerous operations.
    """
    DANGEROUS_COMMANDS = [
        "rm -rf", "mkfs", "dd if=", "shutdown", "reboot",
        "chmod 777", "chown", "passwd", "userdel",
        "curl", "wget" # Networking tools often used for data exfiltration
    ]

    DANGEROUS_FILES = [
        "/etc/shadow", "/etc/passwd", ".env", "id_rsa", "id_ed25519",
        "~/.bash_history", "~/.ssh/config"
    ]

    def evaluate_command(self, cmd: str) -> Tuple[bool, str, int]:
        """
        Evaluates a shell command risk.
        Returns (is_allowed, reason, risk_level 0-10).
        """
        risk_level = 0
        reasons = []

        for dangerous in self.DANGEROUS_COMMANDS:
            if dangerous in cmd:
                risk_level += 5
                reasons.append(f"Contains restricted command: {dangerous}")

        for dangerous_file in self.DANGEROUS_FILES:
            if dangerous_file in cmd:
                risk_level += 3
                reasons.append(f"Accesses sensitive file/path: {dangerous_file}")

        if risk_level >= 5:
            return False, f"HIGH RISK (Blocked): {', '.join(reasons)}", risk_level

        return True, "Safe", 0

    def evaluate_python(self, code: str) -> Tuple[bool, str, int]:
        """
        Evaluates Python code for dangerous imports or calls.
        """
        dangerous_imports = ["os", "subprocess", "shutil", "socket", "pickle", "marshal"]
        risk_level = 0
        reasons = []

        for imp in dangerous_imports:
            if f"import {imp}" in code or f"from {imp}" in code:
                risk_level += 4
                reasons.append(f"Imports dangerous module: {imp}")

        if "eval(" in code or "exec(" in code:
            risk_level += 6
            reasons.append("Uses dynamic execution (eval/exec)")

        if risk_level >= 10:
            return False, f"BLOCKING RISK: {', '.join(reasons)}", risk_level

        return True, "Manual Review Required" if risk_level > 0 else "Safe", risk_level
