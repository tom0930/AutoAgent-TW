#!/usr/bin/env python3
"""
AutoAgent-TW Doctor Command
============================
System diagnostics and health checks for AutoAgent-TW framework.

Similar to OpenClaw's `openclaw doctor`, this command provides:
- System status and health checks
- Memory usage monitoring (including pyrefly)
- Process monitoring (zombie detection)
- Configuration validation
- Security audit
- Agent state visualization

Usage:
    python scripts/doctor.py                    # Run all checks
    python scripts/doctor.py --repair           # Auto-fix issues
    python scripts/doctor.py --status           # Quick status only
    python scripts/doctor.py --security         # Security audit only
    python scripts/doctor.py --deep             # Deep scan for issues
"""

import os
import sys
import json
import argparse
import platform
import subprocess
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, "detach"):
    sys.stdout = __import__('io').TextIOWrapper(
        sys.stdout.detach(), encoding="utf-8", errors="replace"
    )
    sys.stderr = __import__('io').TextIOWrapper(
        sys.stderr.detach(), encoding="utf-8", errors="replace"
    )

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
AA_HOME = Path(os.environ.get("AA_HOME", Path.home() / ".antigravity"))
CONFIG_DIR = PROJECT_ROOT / "config"
STATE_DIR = PROJECT_ROOT / ".agent-state"
LOGS_DIR = PROJECT_ROOT / "logs"
VENV_PATH = PROJECT_ROOT / "venv"


class HealthStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_action: Optional[str] = None


class AutoAgentDoctor:
    """System diagnostics for AutoAgent-TW."""

    def __init__(self, repair: bool = False, deep: bool = False):
        self.repair = repair
        self.deep = deep
        self.checks: List[HealthCheck] = []
        self.start_time = time.time()

    def _get_process_info(self, proc: psutil.Process) -> Optional[Dict]:
        """Safely get process info."""
        try:
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
                "cmdline": " ".join(proc.cmdline()[:3]) if proc.cmdline() else "",
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def check_system_resources(self) -> HealthCheck:
        """Check overall system resources."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(PROJECT_ROOT))

        status = HealthStatus.OK
        warnings = []

        if cpu_percent > 90:
            status = HealthStatus.WARNING
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
        if memory.percent > 85:
            status = HealthStatus.WARNING if status == HealthStatus.OK else status
            warnings.append(f"High memory usage: {memory.percent:.1f}%")
        if disk.percent > 90:
            status = HealthStatus.WARNING if status == HealthStatus.OK else status
            warnings.append(f"Low disk space: {disk.percent:.1f}% used")

        return HealthCheck(
            name="System Resources",
            status=status,
            message="; ".join(warnings) if warnings else "System resources OK",
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / 1024**3,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024**3,
            },
        )

    def check_pyrefly_status(self) -> HealthCheck:
        """Check pyrefly service status and memory usage."""
        pyrefly_procs = []
        pyrefly_exes = []

        # Check for running processes
        for proc in psutil.process_iter(["pid", "name", "memory_info", "cmdline"]):
            try:
                name = proc.info.get("name", "").lower()
                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                if "pyrefly" in name or "pyrefly" in cmdline:
                    info = self._get_process_info(proc)
                    if info:
                        pyrefly_procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Check if exe is disabled
        pyrefly_exe = Path.home() / ".antigravity" / "extensions" / "meta.pyrefly-0.62.0-win32-x64" / "bin" / "pyrefly.exe"
        pyrefly_disabled = pyrefly_exe.with_suffix(".exe.disabled")

        if pyrefly_disabled.exists():
            exe_status = "DISABLED (memory-safe mode)"
        elif pyrefly_exe.exists():
            exe_status = "ENABLED (may consume 1-4GB RAM)"
        else:
            exe_status = "NOT FOUND"

        total_memory = sum(p["memory_mb"] for p in pyrefly_procs)

        status = HealthStatus.OK
        message = f"Pyrefly status: {exe_status}"

        if pyrefly_procs:
            status = HealthStatus.WARNING
            message += f" | {len(pyrefly_procs)} process(es) running, {total_memory:.0f}MB total"
            if total_memory > 500:
                status = HealthStatus.ERROR
                message += " (HIGH MEMORY USAGE)"

        return HealthCheck(
            name="Pyrefly Service",
            status=status,
            message=message,
            details={
                "exe_status": exe_status,
                "processes": pyrefly_procs,
                "total_memory_mb": total_memory,
                "exe_path": str(pyrefly_exe),
                "disabled_path": str(pyrefly_disabled),
            },
            fix_action="python scripts/pyrefly_mode.py disable" if total_memory > 500 else None,
        )

    def check_antigravity_processes(self) -> HealthCheck:
        """Check for Antigravity IDE processes."""
        ag_procs = []
        targets = ["antigravity", "code", "cursor", "pyrefly", "node"]

        for proc in psutil.process_iter(["pid", "name", "memory_info", "cmdline"]):
            try:
                name = proc.info.get("name", "").lower()
                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                for target in targets:
                    if target in name:
                        info = self._get_process_info(proc)
                        if info and info["memory_mb"] > 50:  # Only significant processes
                            ag_procs.append(info)
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        total_memory = sum(p["memory_mb"] for p in ag_procs)

        status = HealthStatus.OK
        if total_memory > 3000:
            status = HealthStatus.WARNING
        if total_memory > 5000:
            status = HealthStatus.ERROR

        return HealthCheck(
            name="Antigravity Processes",
            status=status,
            message=f"{len(ag_procs)} processes, {total_memory:.0f}MB total",
            details={
                "processes": ag_procs[:10],  # Top 10
                "total_count": len(ag_procs),
                "total_memory_mb": total_memory,
            },
        )

    def check_zombie_processes(self) -> HealthCheck:
        """Check for orphaned/zombie processes."""
        from src.core.reaper import AgentReaper

        reaper = AgentReaper(dry_run=not self.repair)
        zombie_count = 0
        zombie_details = []

        for proc in psutil.process_iter(["pid", "name", "ppid", "cmdline"]):
            try:
                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                name = proc.info.get("name", "").lower()
                for marker in reaper.TARGET_MARKERS:
                    if marker in cmdline or marker in name:
                        # Check if orphan
                        try:
                            parent = psutil.Process(proc.info["ppid"])
                            if not parent.is_running():
                                zombie_count += 1
                                zombie_details.append({
                                    "pid": proc.pid,
                                    "name": name,
                                    "marker": marker,
                                })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            zombie_count += 1
                            zombie_details.append({
                                "pid": proc.pid,
                                "name": name,
                                "marker": marker,
                            })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        status = HealthStatus.OK if zombie_count == 0 else HealthStatus.WARNING

        return HealthCheck(
            name="Zombie Processes",
            status=status,
            message=f"{zombie_count} orphaned processes found",
            details={"zombies": zombie_details},
            fix_action="python scripts/kill_zombies.py" if zombie_count > 0 else None,
        )

    def check_configuration(self) -> HealthCheck:
        """Check configuration files."""
        issues = []
        details = {}

        # Check .env
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            details["env_exists"] = True
            # Check for placeholder secrets
            try:
                content = env_file.read_text(encoding="utf-8")
                if "sk-" in content and "placeholder" not in content.lower():
                    issues.append(".env contains API keys (should be in .gitignore)")
            except Exception:
                pass
        else:
            details["env_exists"] = False

        # Check config directory
        config_file = CONFIG_DIR / "autocli_policy.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    policy = json.load(f)
                details["policy"] = policy
                # Validate whitelist/blacklist
                if not policy.get("whitelist"):
                    issues.append("autocli_policy.json: empty whitelist")
            except Exception as e:
                issues.append(f"Cannot parse autocli_policy.json: {e}")
        else:
            issues.append("Missing config/autocli_policy.json")

        status = HealthStatus.OK if not issues else HealthStatus.WARNING
        return HealthCheck(
            name="Configuration",
            status=status,
            message="; ".join(issues) if issues else "Configuration OK",
            details=details,
        )

    def check_gitignore(self) -> HealthCheck:
        """Check .gitignore for sensitive paths."""
        gitignore = PROJECT_ROOT / ".gitignore"
        required_patterns = [".env", "bin/extension/", "*.pem", "*.key", "secrets/"]

        if not gitignore.exists():
            return HealthCheck(
                name="Gitignore",
                status=HealthStatus.WARNING,
                message=".gitignore not found",
                fix_action="Create .gitignore with required patterns",
            )

        try:
            content = gitignore.read_text(encoding="utf-8")
            missing = []
            for pattern in required_patterns:
                if pattern not in content:
                    missing.append(pattern)

            status = HealthStatus.OK if not missing else HealthStatus.WARNING
            return HealthCheck(
                name="Gitignore",
                status=status,
                message=f"Missing patterns: {', '.join(missing)}" if missing else "Gitignore OK",
                details={"missing_patterns": missing},
                fix_action=f"Add to .gitignore: {' '.join(missing)}" if missing else None,
            )
        except Exception as e:
            return HealthCheck(
                name="Gitignore",
                status=HealthStatus.ERROR,
                message=f"Cannot read .gitignore: {e}",
            )

    def check_agent_state(self) -> HealthCheck:
        """Check agent state files."""
        state_dir = STATE_DIR
        state_files = {}

        if state_dir.exists():
            for f in state_dir.glob("*.json"):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        state_files[f.name] = json.load(fp)
                except Exception as e:
                    state_files[f.name] = {"error": str(e)}

        status = HealthStatus.OK
        messages = []

        # Check for stale locks
        for name, data in state_files.items():
            if isinstance(data, dict) and data.get("locked"):
                lock_time = data.get("lock_time")
                if lock_time:
                    try:
                        lock_dt = datetime.fromisoformat(lock_time)
                        age_hours = (datetime.now() - lock_dt).total_seconds() / 3600
                        if age_hours > 24:
                            messages.append(f"Stale lock in {name} ({age_hours:.1f}h old)")
                            status = HealthStatus.WARNING
                    except Exception:
                        pass

        return HealthCheck(
            name="Agent State",
            status=status,
            message="; ".join(messages) if messages else f"{len(state_files)} state files OK",
            details={"files": list(state_files.keys())},
        )

    def check_virtual_environment(self) -> HealthCheck:
        """Check Python virtual environment."""
        issues = []

        if not VENV_PATH.exists():
            return HealthCheck(
                name="Virtual Environment",
                status=HealthStatus.ERROR,
                message="Virtual environment not found",
                fix_action="Run: python -m venv venv && pip install -r requirements.txt",
            )

        # Check Python version
        py_version = sys.version_info
        details = {
            "python_version": f"{py_version.major}.{py_version.minor}.{py_version.micro}",
            "venv_path": str(VENV_PATH),
        }

        if py_version < (3, 10):
            issues.append(f"Python {py_version.major}.{py_version.minor} < 3.10")

        # Check key packages
        try:
            import langchain
            import psutil
            details["langchain_version"] = getattr(langchain, "__version__", "unknown")
        except ImportError as e:
            issues.append(f"Missing package: {e}")

        status = HealthStatus.OK if not issues else HealthStatus.WARNING
        return HealthCheck(
            name="Virtual Environment",
            status=status,
            message="; ".join(issues) if issues else "Virtual environment OK",
            details=details,
        )

    def check_security(self) -> HealthCheck:
        """Check for security issues."""
        issues = []
        details = {}

        # Check for hardcoded secrets
        patterns = ["api_key", "password", "secret", "token", "credential"]
        exclude_dirs = {".git", "venv", "node_modules", "__pycache__", ".pytest_cache"}

        if self.deep:
            for root, dirs, files in os.walk(PROJECT_ROOT):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for f in files:
                    if f.endswith((".py", ".json", ".yaml", ".yml", ".env")):
                        fp = Path(root) / f
                        try:
                            content = fp.read_text(encoding="utf-8", errors="ignore")
                            for pattern in patterns:
                                if f"{pattern}=" in content.lower() and "placeholder" not in content.lower():
                                    issues.append(f"Potential secret in {fp.relative_to(PROJECT_ROOT)}")
                                    break
                        except Exception:
                            pass

        # Check file permissions
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            details["env_permissions"] = oct(env_file.stat().st_mode)[-3:]

        status = HealthStatus.OK if not issues else HealthStatus.WARNING
        return HealthCheck(
            name="Security",
            status=status,
            message=f"{len(issues)} potential issues found" if issues else "No security issues",
            details=details,
        )

    def run_all_checks(self) -> List[HealthCheck]:
        """Run all health checks."""
        self.checks = [
            self.check_system_resources(),
            self.check_pyrefly_status(),
            self.check_antigravity_processes(),
            self.check_zombie_processes(),
            self.check_configuration(),
            self.check_gitignore(),
            self.check_agent_state(),
            self.check_virtual_environment(),
            self.check_security() if self.deep else HealthCheck(
                name="Security",
                status=HealthStatus.OK,
                message="Skipped (use --deep for full scan)",
            ),
        ]
        return self.checks

    def print_report(self):
        """Print diagnostic report."""
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("  AutoAgent-TW Doctor Report")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")

        # Summary
        ok_count = sum(1 for c in self.checks if c.status == HealthStatus.OK)
        warn_count = sum(1 for c in self.checks if c.status == HealthStatus.WARNING)
        error_count = sum(1 for c in self.checks if c.status == HealthStatus.ERROR)

        status_icon = "✅" if error_count == 0 else ("⚠️" if warn_count > 0 else "❌")
        print(f"{status_icon} Summary: {ok_count} OK, {warn_count} Warnings, {error_count} Errors\n")

        # Detailed checks
        for check in self.checks:
            icon = {
                HealthStatus.OK: "✅",
                HealthStatus.WARNING: "⚠️",
                HealthStatus.ERROR: "❌",
                HealthStatus.CRITICAL: "💀",
            }.get(check.status, "❓")

            print(f"{icon} {check.name}")
            print(f"   └─ {check.message}")

            if check.fix_action and self.repair:
                print(f"   └─ 🔧 Fix: {check.fix_action}")

            if self.deep and check.details:
                for key, value in list(check.details.items())[:5]:
                    if isinstance(value, (list, dict)):
                        value = f"({len(value)} items)"
                    print(f"      • {key}: {value}")
            print()

        print(f"Completed in {elapsed:.2f}s")
        print("=" * 60 + "\n")

        return error_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="AutoAgent-TW System Doctor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/doctor.py                  # Run all checks
    python scripts/doctor.py --repair         # Auto-fix issues
    python scripts/doctor.py --status         # Quick status
    python scripts/doctor.py --security       # Security audit only
    python scripts/doctor.py --deep          # Deep scan
        """,
    )
    parser.add_argument("--repair", "-r", action="store_true", help="Auto-fix issues where possible")
    parser.add_argument("--deep", "-d", action="store_true", help="Deep scan for security issues")
    parser.add_argument("--status", "-s", action="store_true", help="Quick status only")
    parser.add_argument("--security", action="store_true", help="Security audit only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    doctor = AutoAgentDoctor(repair=args.repair, deep=args.deep)
    doctor.run_all_checks()

    if args.json:
        result = {
            "timestamp": datetime.now().isoformat(),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                    "fix_action": c.fix_action,
                }
                for c in doctor.checks
            ],
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        success = doctor.print_report()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
