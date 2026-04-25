"""AI Harness Health Check System
Provides comprehensive system diagnostics for the AI Harness Framework.
"""
from __future__ import annotations

import sys
import os
import time
import psutil
import platform
import importlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum


class HealthLevel(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    name: str
    level: HealthLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    @property
    def icon(self) -> str:
        return {"ok": "✅", "warning": "⚠️", "error": "❌", "unknown": "❓"}[self.level.value]

    @property
    def passed(self) -> bool:
        return self.level == HealthLevel.OK


@dataclass
class HealthReport:
    checks: List[HealthCheckResult] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)

    def add(self, result: HealthCheckResult):
        self.checks.append(result)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if c.level == HealthLevel.WARNING)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if c.level == HealthLevel.ERROR)

    @property
    def duration_ms(self) -> float:
        return (time.time() - self.started_at) * 1000

    def summary(self) -> str:
        total = self.total
        passed = self.passed_count
        warns = self.warning_count
        failed = self.failed_count
        dur = self.duration_ms
        return (
            f"\n{'─' * 50}\n"
            f" 健康檢查報告  |  {passed}/{total} passed"
            f"  ⚠️ {warns}  ❌ {failed}  ({dur:.0f}ms)\n"
            f"{'─' * 50}"
        )

    def print_report(self, verbose: bool = False):
        print(self.summary())
        for check in self.checks:
            icon = check.icon
            if verbose or check.level != HealthLevel.OK:
                details = ""
                if check.details and verbose:
                    kv = "  ".join(f"{k}={v}" for k, v in check.details.items() if v is not None)
                    details = f"  [{kv}]" if kv else ""
                print(f"  {icon} [{check.name}] {check.message}{details}")
        print()


class HealthChecker:
    """
    Multi-subsystem health checker for AI Harness.
    Run all checks or specific categories.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or Path.cwd()
        self.process = psutil.Process()

    def check_all(self) -> HealthReport:
        """Run all health checks."""
        report = HealthReport()
        for check_fn in [
            self.check_python_runtime,
            self.check_core_imports,
            self.check_memory,
            self.check_disk_space,
            self.check_processes,
            self.check_skill_engine,
            self.check_vision_system,
            self.check_mcp_hub,
            self.check_cron_scheduler,
            self.check_orchestration,
            self.check_canvas_system,
            self.check_gateway,
            self.check_config,
        ]:
            result = check_fn()
            report.add(result)
        return report

    # ── Individual Checks ────────────────────────────────────

    def check_python_runtime(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            ver = platform.python_version()
            arch = platform.architecture()[0]
            impl = platform.python_implementation()
            details = {
                "version": ver,
                "implementation": impl,
                "arch": arch,
                "executable": sys.executable,
            }
            # Warn if not CPython
            if impl != "CPython":
                return HealthCheckResult(
                    name="Python Runtime",
                    level=HealthLevel.WARNING,
                    message=f"Non-CPython detected: {impl}",
                    details=details,
                    duration_ms=(time.time() - t0) * 1000,
                )
            return HealthCheckResult(
                name="Python Runtime",
                level=HealthLevel.OK,
                message=f"{impl} {ver} ({arch})",
                details=details,
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return HealthCheckResult(
                name="Python Runtime",
                level=HealthLevel.ERROR,
                message=str(e),
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_core_imports(self) -> HealthCheckResult:
        t0 = time.time()
        modules = [
            "src.core.harness_gateway",
            "src.core.session_manager",
            "src.core.skill",
            "src.core.mcp",
            "src.core.cron",
            "src.core.node",
            "src.core.orchestration",
            "src.core.rva",
        ]
        failed: List[str] = []
        for mod in modules:
            try:
                importlib.import_module(mod)
            except Exception as e:
                failed.append(f"{mod}: {e}")

        if failed:
            return HealthCheckResult(
                name="Core Imports",
                level=HealthLevel.ERROR,
                message=f"{len(failed)}/{len(modules)} modules failed to import",
                details={"failed": failed[:5]},
                duration_ms=(time.time() - t0) * 1000,
            )
        return HealthCheckResult(
            name="Core Imports",
            level=HealthLevel.OK,
            message=f"全部 {len(modules)} 核心模組匯入成功",
            details={"modules": len(modules)},
            duration_ms=(time.time() - t0) * 1000,
        )

    def check_memory(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            mem = self.process.memory_info()
            sys_mem = psutil.virtual_memory()
            rss_mb = mem.rss / 1024 / 1024
            sys_used_pct = sys_mem.percent

            level = HealthLevel.OK
            if rss_mb > 800:
                level = HealthLevel.ERROR
            elif rss_mb > 600:
                level = HealthLevel.WARNING

            msg = f"Python {rss_mb:.0f}MB | System {sys_used_pct:.0f}% used"
            return HealthCheckResult(
                name="Memory",
                level=level,
                message=msg,
                details={"rss_mb": round(rss_mb, 1), "sys_used_pct": sys_used_pct},
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return HealthCheckResult(
                name="Memory",
                level=HealthLevel.UNKNOWN,
                message=str(e),
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_disk_space(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            drive = Path(self.workspace.root if hasattr(self.workspace, "root") else self.workspace)
            # Find the actual drive on Windows
            if not drive.exists():
                drive = Path("Z:/") if Path("Z:/").exists() else Path("C:/")
            usage = psutil.disk_usage(str(drive))
            free_gb = usage.free / 1024 / 1024 / 1024
            pct = usage.percent

            if pct > 95:
                level = HealthLevel.ERROR
            elif pct > 85:
                level = HealthLevel.WARNING
            else:
                level = HealthLevel.OK

            return HealthCheckResult(
                name="Disk Space",
                level=level,
                message=f"{free_gb:.1f}GB free ({pct:.0f}% used)",
                details={"free_gb": round(free_gb, 2), "used_pct": pct},
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return HealthCheckResult(
                name="Disk Space",
                level=HealthLevel.UNKNOWN,
                message=str(e),
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_processes(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            # Check for key child processes
            children = self.process.children(recursive=True)
            child_info = {c.name(): c.status() for c in children[:10]}
            return HealthCheckResult(
                name="Child Processes",
                level=HealthLevel.OK,
                message=f"{len(children)} child processes",
                details={"children_count": len(children), "samples": dict(list(child_info.items())[:5])},
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return HealthCheckResult(
                name="Child Processes",
                level=HealthLevel.WARNING,
                message=f"Cannot enumerate: {e}",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_skill_engine(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            from src.core.skill import SkillEngine
            engine = SkillEngine(self.workspace / "skills")
            skills = engine.list_skills(enabled_only=False)
            enabled = engine.list_skills(enabled_only=True)
            return HealthCheckResult(
                name="Skill Engine",
                level=HealthLevel.OK,
                message=f"{len(enabled)}/{len(skills)} skills enabled",
                details={"total": len(skills), "enabled": len(enabled)},
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="Skill Engine",
                level=HealthLevel.ERROR,
                message="SkillEngine not found",
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return HealthCheckResult(
                name="Skill Engine",
                level=HealthLevel.WARNING,
                message=str(e),
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_vision_system(self) -> HealthCheckResult:
        t0 = time.time()
        # Step 2: Headless Mode (Phase 129)
        if os.environ.get("AA_HEADLESS") == "1":
            return HealthCheckResult(
                name="Vision System",
                level=HealthLevel.OK,
                message="Skipped (Headless Mode Active)",
                duration_ms=(time.time() - t0) * 1000,
            )
            
        try:
            from src.core.rva import VisionHarness
            return HealthCheckResult(
                name="Vision System",
                level=HealthLevel.OK,
                message="VisionHarness available",
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="Vision System",
                level=HealthLevel.WARNING,
                message="VisionHarness not available",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_mcp_hub(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            from src.core.mcp import MCPHub
            return HealthCheckResult(
                name="MCP Hub",
                level=HealthLevel.OK,
                message="MCPHub available",
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="MCP Hub",
                level=HealthLevel.WARNING,
                message="MCPHub not available",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_cron_scheduler(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            from src.core.cron import CronScheduler
            return HealthCheckResult(
                name="Cron Scheduler",
                level=HealthLevel.OK,
                message="CronScheduler available",
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="Cron Scheduler",
                level=HealthLevel.WARNING,
                message="CronScheduler not available",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_orchestration(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            from src.core.orchestration import OrchestrationCoordinator
            return HealthCheckResult(
                name="Orchestration",
                level=HealthLevel.OK,
                message="OrchestrationCoordinator available",
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="Orchestration",
                level=HealthLevel.WARNING,
                message="OrchestrationCoordinator not available",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_canvas_system(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            from src.harness.canvas import CanvasSystem
            return HealthCheckResult(
                name="Canvas System",
                level=HealthLevel.OK,
                message="CanvasSystem available",
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="Canvas System",
                level=HealthLevel.WARNING,
                message="CanvasSystem not available",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_gateway(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            from src.core.harness_gateway import HarnessGateway
            return HealthCheckResult(
                name="Gateway Daemon",
                level=HealthLevel.OK,
                message="HarnessGateway available",
                duration_ms=(time.time() - t0) * 1000,
            )
        except ImportError:
            return HealthCheckResult(
                name="Gateway Daemon",
                level=HealthLevel.ERROR,
                message="HarnessGateway not found",
                duration_ms=(time.time() - t0) * 1000,
            )

    def check_config(self) -> HealthCheckResult:
        t0 = time.time()
        config_file = self.workspace / "config" / "harness.toml"
        if not config_file.exists():
            config_file = self.workspace / "config" / "ai_harness.toml"
        if not config_file.exists():
            return HealthCheckResult(
                name="Config File",
                level=HealthLevel.WARNING,
                message="No harness config file found",
                details={"searched": ["config/harness.toml", "config/ai_harness.toml"]},
                duration_ms=(time.time() - t0) * 1000,
            )
        return HealthCheckResult(
            name="Config File",
            level=HealthLevel.OK,
            message=f"Found: {config_file.name}",
            details={"path": str(config_file)},
            duration_ms=(time.time() - t0) * 1000,
        )


def run_health_check(workspace: Optional[Path] = None, verbose: bool = False) -> int:
    """Run all health checks and return exit code (0=healthy, 1=issues)."""
    checker = HealthChecker(Path(workspace) if workspace else None)
    report = checker.check_all()
    report.print_report(verbose=verbose)
    # Return 0 only if no errors
    return 0 if report.failed_count == 0 else 1
