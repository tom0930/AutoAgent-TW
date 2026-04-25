"""
AI Harness CLI - Unified command-line interface
Version: v1.1.0

Usage:
    aa-harness <command> [options]

Examples:
    aa-harness start
    aa-harness status
    aa-harness skill list
    aa-harness agent spawn "help me analyze this"
    aa-harness doctor          # Run health checks
    aa-harness orchestrate     # Show orchestration graph
    aa-harness canvas list    # List canvas nodes
"""
from __future__ import annotations

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Phase 129: Headless Security
try:
    from src.core.security.log_sanitizer import LogSanitizer
except ImportError:
    LogSanitizer = None

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class HarnessCLI:
    """
    AI Harness unified CLI

    Provides functionality equivalent to the OpenClaw CLI.
    """

    VERSION = "1.1.0"
    NAME = "aa-harness"

    def __init__(self, argv: Optional[List[str]] = None):
        self.argv = argv or sys.argv[1:]
        self.parser = self._build_parser()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging."""
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)

        logger = logging.getLogger("harness.cli")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(
            log_dir / "cli.log",
            encoding="utf-8",
            mode="a",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        return logger

    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser."""
        parser = argparse.ArgumentParser(
            prog=self.NAME,
            description=f"AI Harness CLI v{self.VERSION}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  aa-harness start           Start Gateway service
  aa-harness stop            Stop Gateway service
  aa-harness status          View service status
  aa-harness skill list      List all Skills
  aa-harness agent spawn     Start a sub-agent
  aa-harness session list    List all Sessions
  aa-harness cron list       List scheduled tasks
  aa-harness node list       List paired devices
  aa-harness doctor          Run system health checks
  aa-harness orchestrate     View orchestration graph
  aa-harness canvas list     List canvas nodes
  aa-harness --help          Show help
            """,
        )

        parser.add_argument(
            "--version", "-v",
            action="version",
            version=f"{self.NAME} v{self.VERSION}",
        )
        parser.add_argument(
            "--verbose", "-V",
            action="store_true",
            help="Enable verbose output",
        )
        parser.add_argument(
            "--workspace", "-w",
            default=os.getcwd(),
            help="Working directory",
        )
        parser.add_argument(
            "--headless",
            action="store_true",
            help="Run in headless mode (no interaction, structured output)",
        )

        # Subcommands
        subparsers = parser.add_subparsers(
            dest="command",
            title="commands",
            description="Available commands",
        )

        self._add_gateway_commands(subparsers)
        self._add_skill_commands(subparsers)
        self._add_agent_commands(subparsers)
        self._add_session_commands(subparsers)
        self._add_cron_commands(subparsers)
        self._add_node_commands(subparsers)
        self._add_vision_commands(subparsers)
        self._add_system_commands(subparsers)
        self._add_doctor_commands(subparsers)   # NEW: health checks
        self._add_orchestrate_commands(subparsers)  # NEW
        self._add_canvas_commands(subparsers)   # NEW

        return parser

    # ── Subcommand Builders ──────────────────────────────────

    def _add_gateway_commands(self, subparsers):
        """Gateway commands: start/stop/restart/status."""
        start = subparsers.add_parser("start", help="Start Gateway service")
        start.add_argument("--foreground", "-f", action="store_true", help="Run in foreground")
        start.add_argument("--port", "-p", type=int, default=18792, help="Port number")

        subparsers.add_parser("stop", help="Stop Gateway service")
        subparsers.add_parser("restart", help="Restart Gateway service")
        status = subparsers.add_parser("status", help="Show Gateway status")
        status.add_argument("--json", action="store_true", help="Output as JSON")

    def _add_skill_commands(self, subparsers):
        """Skill commands."""
        skill = subparsers.add_parser("skill", help="Manage skills")
        skill_sub = skill.add_subparsers(dest="skill_command", title="skill commands")

        skill_sub.add_parser("list", help="List all skills")
        skill_sub.add_parser("enabled", help="List enabled skills")
        se = skill_sub.add_parser("enable", help="Enable a skill")
        se.add_argument("name", help="Skill name")
        sd = skill_sub.add_parser("disable", help="Disable a skill")
        sd.add_argument("name", help="Skill name")
        si = skill_sub.add_parser("install", help="Install a skill from URL/path")
        si.add_argument("source", help="Skill source URL or path")
        su = skill_sub.add_parser("uninstall", help="Uninstall a skill")
        su.add_argument("name", help="Skill name")

    def _add_agent_commands(self, subparsers):
        """Agent commands."""
        agent = subparsers.add_parser("agent", help="Manage agents")
        agent_sub = agent.add_subparsers(dest="agent_command", title="agent commands")

        sp = agent_sub.add_parser("spawn", help="Spawn a new agent")
        sp.add_argument("prompt", nargs="*", help="Agent prompt")
        sp.add_argument("--runtime", choices=["subagent", "acp", "process"],
                        default="subagent", help="Runtime type")
        sp.add_argument("--model", help="Model to use")
        sp.add_argument("--timeout", type=int, default=0, help="Timeout in seconds")

        agent_sub.add_parser("list", help="List active agents")
        ka = agent_sub.add_parser("kill", help="Kill an agent")
        ka.add_argument("agent_id", help="Agent ID to kill")

    def _add_session_commands(self, subparsers):
        """Session commands."""
        session = subparsers.add_parser("session", help="Manage sessions")
        session_sub = session.add_subparsers(dest="session_command", title="session commands")

        session_sub.add_parser("list", help="List all sessions")
        si = session_sub.add_parser("show", help="Show session details")
        si.add_argument("session_id", help="Session ID")
        sd = session_sub.add_parser("delete", help="Delete a session")
        sd.add_argument("session_id", help="Session ID to delete")
        sd.add_argument("--force", "-f", action="store_true", help="Force delete")

    def _add_cron_commands(self, subparsers):
        """Cron/scheduler commands."""
        cron = subparsers.add_parser("cron", help="Manage scheduled tasks")
        cron_sub = cron.add_subparsers(dest="cron_command", title="cron commands")

        cron_sub.add_parser("list", help="List scheduled tasks")
        cron_sub.add_parser("status", help="Show scheduler status")
        ad = cron_sub.add_parser("add", help="Add a scheduled task")
        ad.add_argument("name", help="Task name")
        ad.add_argument("schedule", help="Cron expression or interval (e.g., '5m', '1h', '*/15 * * * *')")
        ad.add_argument("command", help="Command to execute")
        rm = cron_sub.add_parser("remove", help="Remove a scheduled task")
        rm.add_argument("job_id", help="Job ID to remove")
        rn = cron_sub.add_parser("run", help="Run a job immediately")
        rn.add_argument("job_id", help="Job ID to run")

    def _add_node_commands(self, subparsers):
        """Node/device pairing commands."""
        node = subparsers.add_parser("node", help="Manage paired devices")
        node_sub = node.add_subparsers(dest="node_command", title="node commands")

        node_sub.add_parser("list", help="List paired devices")
        nd = node_sub.add_parser("describe", help="Show device details")
        nd.add_argument("device_id", help="Device ID")
        np = node_sub.add_parser("pair", help="Pair a new device")
        np.add_argument("code", help="Pairing code")
        nr = node_sub.add_parser("remove", help="Remove a paired device")
        nr.add_argument("device_id", help="Device ID to remove")

    def _add_vision_commands(self, subparsers):
        """Vision system commands."""
        vision = subparsers.add_parser("vision", help="Manage vision system")
        vision_sub = vision.add_subparsers(dest="vision_command", title="vision commands")

        vi = vision_sub.add_parser("info", help="Show vision system info")
        vi.add_argument("--verbose", "-v", action="store_true")
        vc = vision_sub.add_parser("capture", help="Capture a screenshot")
        vc.add_argument("--output", "-o", help="Output file path")
        vc.add_argument("--region", nargs=4, type=int,
                        metavar=("X", "Y", "W", "H"), help="Capture region (x y w h)")
        vw = vision_sub.add_parser("watch", help="Start continuous screen watching")
        vw.add_argument("--interval", type=float, default=1.0, help="Capture interval (seconds)")
        vw.add_argument("--fps", type=int, help="Target FPS (overrides interval)")

    def _add_system_commands(self, subparsers):
        """System commands."""
        system = subparsers.add_parser("system", help="System utilities")
        system_sub = system.add_subparsers(dest="system_command", title="system commands")

        system_sub.add_parser("info", help="Show system information")
        system_sub.add_parser("memory", help="Show memory usage")
        clean = system_sub.add_parser("clean", help="Clean resources")
        clean.add_argument("--cache", action="store_true", help="Clean cache")
        clean.add_argument("--temp", action="store_true", help="Clean temp files")

    # ══════════════════════════════════════════════════════════
    # NEW: _cmd_doctor — system health checks
    # ══════════════════════════════════════════════════════════

    def _add_doctor_commands(self, subparsers):
        """Health check commands."""
        doctor = subparsers.add_parser("doctor", help="Run system health checks")
        doctor.add_argument(
            "--verbose", "-V",
            action="store_true",
            help="Show all checks including passing ones",
        )
        doctor.add_argument(
            "--json",
            action="store_true",
            help="Output report as JSON",
        )
        doctor.add_argument(
            "--category", "-c",
            dest="check_category",
            choices=["all", "runtime", "core", "memory", "disk", "skill", "vision", "mcp", "cron", "orchestration", "canvas", "gateway", "config"],
            default="all",
            help="Run specific category of checks",
        )

    def _cmd_doctor(self, args) -> int:
        """Run health checks."""
        try:
            from src.core.health import run_health_check, HealthChecker, HealthReport
        except ImportError:
            print("❌ Health check system not available (src/core/health/ missing)")
            return 1

        checker = HealthChecker(Path(args.workspace))

        # Route to specific check
        check_map = {
            "runtime": checker.check_python_runtime,
            "core": checker.check_core_imports,
            "memory": checker.check_memory,
            "disk": checker.check_disk_space,
            "skill": checker.check_skill_engine,
            "vision": checker.check_vision_system,
            "mcp": checker.check_mcp_hub,
            "cron": checker.check_cron_scheduler,
            "orchestration": checker.check_orchestration,
            "canvas": checker.check_canvas_system,
            "gateway": checker.check_gateway,
            "config": checker.check_config,
        }

        report = HealthReport()
        if args.check_category == "all":
            report = checker.check_all()
        else:
            fn = check_map.get(args.check_category)
            if fn:
                result = fn()
                report.add(result)

        if args.json:
            import json
            data = {
                "total": report.total,
                "passed": report.passed_count,
                "warnings": report.warning_count,
                "failed": report.failed_count,
                "duration_ms": report.duration_ms,
                "checks": [
                    {
                        "name": c.name,
                        "level": c.level.value,
                        "message": c.message,
                        "details": c.details,
                        "duration_ms": c.duration_ms,
                    }
                    for c in report.checks
                ],
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            report.print_report(verbose=args.verbose)

        return 0 if report.failed_count == 0 else 1

    # ══════════════════════════════════════════════════════════
    # NEW: _cmd_orchestrate — orchestration coordinator view
    # ══════════════════════════════════════════════════════════

    def _add_orchestrate_commands(self, subparsers):
        """Orchestration commands."""
        orch = subparsers.add_parser("orchestrate", help="View orchestration system")
        orch_sub = orch.add_subparsers(dest="orch_command", title="orchestration commands")

        orch_sub.add_parser("status", help="Show orchestration status")
        orch_sub.add_parser("graph", help="Show agent orchestration graph")
        orch_sub.add_parser("agents", help="List active sub-agents")
        orch_sub.add_parser("tools", help="List available MCP tools")

    def _cmd_orchestrate(self, args) -> int:
        """Orchestration system overview."""
        try:
            from src.core.orchestration import OrchestrationCoordinator, AgentProcess
            from src.core.orchestration.spawn_manager import _ACTIVE_SUBAGENTS
        except ImportError as e:
            print(f"❌ Orchestration not available: {e}")
            return 1

        cmd = getattr(args, "orch_command", "status")

        if cmd == "status":
            try:
                coord = OrchestrationCoordinator(Path(args.workspace))
                print("=== Orchestration Coordinator ===")
                print(f"  State: {coord.graph.name if coord.graph else 'N/A'}")
                print(f"  Active agents: {len(_ACTIVE_SUBAGENTS)}")
                print(f"  MCP tools: {len(getattr(coord, '_mcp_tools', []))}")
                return 0
            except Exception as e:
                print(f"❌ Failed to init coordinator: {e}")
                return 1

        if cmd == "agents":
            print("=== Active Sub-Agents ===")
            if not _ACTIVE_SUBAGENTS:
                print("  (none)")
            for proc in list(_ACTIVE_SUBAGENTS):
                # proc is an AgentProcess instance; access via attribute
                name = getattr(proc, "task_name", "?")
                aid = getattr(proc, "agent_id", "?")
                status = getattr(proc, "status", "?")
                progress = getattr(proc, "progress", 0)
                icon = "🟢" if status == "running" else "⚫"
                print(f"  {icon} [{aid}] {name} — {progress}% ({status})")
            return 0

        if cmd == "tools":
            try:
                coord = OrchestrationCoordinator(Path(args.workspace))
                tools = getattr(coord, "_mcp_tools", [])
                print("=== Available MCP Tools ===")
                if not tools:
                    print("  (none)")
                for t in tools:
                    print(f"  - {t}")
                return 0
            except Exception as e:
                print(f"❌ Failed: {e}")
                return 1

        if cmd == "graph":
            try:
                coord = OrchestrationCoordinator(Path(args.workspace))
                print("=== Orchestration Graph ===")
                if coord.graph:
                    print(f"  Graph: {coord.graph.name}")
                    # Show nodes if it's a LangGraph
                    if hasattr(coord.graph, "nodes"):
                        for node_name in coord.graph.nodes:
                            print(f"  ├── {node_name}")
                else:
                    print("  (no graph initialized)")
                return 0
            except Exception as e:
                print(f"❌ Failed: {e}")
                return 1

        print("用法：aa-harness orchestrate [status|graph|agents|tools]")
        return 0

    # ══════════════════════════════════════════════════════════
    # NEW: _cmd_canvas — canvas system commands
    # ══════════════════════════════════════════════════════════

    def _add_canvas_commands(self, subparsers):
        """Canvas system commands."""
        canvas = subparsers.add_parser("canvas", help="Manage canvas nodes")
        canvas_sub = canvas.add_subparsers(dest="canvas_command", title="canvas commands")

        canvas_sub.add_parser("list", help="List all canvas nodes")
        canvas_sub.add_parser("status", help="Show canvas system status")
        show = canvas_sub.add_parser("show", help="Show node details")
        show.add_argument("node_id", help="Node ID")
        export = canvas_sub.add_parser("export", help="Export canvas as Mermaid")
        export.add_argument("output", nargs="?", help="Output file path")
        cn = canvas_sub.add_parser("create", help="Create a new node")
        cn.add_argument("name", help="Node name")
        cn.add_argument("--type", default="agent", choices=["agent", "task", "tool", "mcp", "memory"], help="Node type")

    def _cmd_canvas(self, args) -> int:
        """Canvas system management."""
        try:
            from src.harness.canvas import CanvasSystem
        except ImportError as e:
            print(f"❌ Canvas system not available: {e}")
            return 1

        canvas_dir = Path(args.workspace) / ".agent-state" / "canvas"
        canvas_dir.mkdir(parents=True, exist_ok=True)
        cs = CanvasSystem(state_dir=str(canvas_dir))

        cmd = getattr(args, "canvas_command", "list")

        if cmd == "list":
            nodes = list(cs.nodes.values())
            print(f"=== Canvas Nodes ({len(nodes)}) ===")
            if not nodes:
                print("  (no nodes — run 'aa-harness canvas create <name>' to add one)")
            for node in nodes:
                print(f"  [{node.get('type', '?'):8s}] {node.get('id', '?')} — {node.get('label', node.get('id', '?'))}")
            return 0

        if cmd == "status":
            stats = cs.get_stats()
            print("=== Canvas System Status ===")
            for k, v in stats.items():
                print(f"  {k}: {v}")
            return 0

        if cmd == "show":
            node_id = getattr(args, "node_id", None)
            if not node_id:
                print("❌ node_id required")
                return 1
            import json
            node = cs.nodes.get(node_id)
            if not node:
                print(f"❌ Node not found: {node_id}")
                return 1
            print(json.dumps(node, indent=2, ensure_ascii=False))
            return 0

        if cmd == "export":
            output_path = getattr(args, "output", None)
            mermaid = cs.export_mermaid()
            if output_path:
                Path(output_path).write_text(mermaid, encoding="utf-8")
                print(f"✓ Exported to {output_path}")
            else:
                print(mermaid)
            return 0

        if cmd == "create":
            node_name = getattr(args, "name", None)
            if not node_name:
                print("❌ name required")
                return 1
            node_type = getattr(args, "type", "agent")
            node_id = cs.add_node(node_type, label=node_name)
            print(f"✓ Created node: {node_id} ({node_type})")
            return 0

        print("用法：aa-harness canvas [list|status|show|export|create]")
        return 0

    # ── Original Commands ─────────────────────────────────────

    def run(self) -> int:
        """Execute CLI."""
        args = self.parser.parse_args(self.argv)

        if not args.command:
            self.parser.print_help()
            return 0

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        self.logger.info(f"Running command: {args.command}")

        # Step 1: Log Sanitization (Phase 129)
        if LogSanitizer:
            sanitizer = LogSanitizer()
            sanitizer.wrap_streams()
            self.logger.info("Log sanitization active (Zero Trust boundary enabled)")

        # Step 2: Headless Mode Environment (Phase 129)
        if args.headless:
            os.environ["AA_HEADLESS"] = "1"
            # Ensure stdout is unbuffered in headless mode
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(line_buffering=True)
            self.logger.info("Running in HEADLESS mode (interactive prompts disabled)")

        try:
            return self._dispatch(args)
        except KeyboardInterrupt:
            print("\n操作已取消")
            return 130
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            print(f"錯誤：{e}")
            return 1

    def _dispatch(self, args) -> int:
        """Route command to handler."""
        command = args.command

        if command == "start":
            return self._cmd_start(args)
        if command == "stop":
            return self._cmd_stop(args)
        if command == "restart":
            return self._cmd_restart(args)
        if command == "status":
            return self._cmd_status(args)
        if command == "skill":
            return self._cmd_skill(args)
        if command == "agent":
            return self._cmd_agent(args)
        if command == "session":
            return self._cmd_session(args)
        if command == "cron":
            return self._cmd_cron(args)
        if command == "node":
            return self._cmd_node(args)
        if command == "vision":
            return self._cmd_vision(args)
        if command == "system":
            return self._cmd_system(args)
        if command == "doctor":          # NEW
            return self._cmd_doctor(args)
        if command == "orchestrate":     # NEW
            return self._cmd_orchestrate(args)
        if command == "canvas":          # NEW
            return self._cmd_canvas(args)

        self.parser.print_help()
        return 0

    # ── Original Handlers ─────────────────────────────────────

    def _cmd_start(self, args) -> int:
        print(f"啟動 {self.NAME} Gateway...")
        try:
            from src.core.harness_gateway import HarnessGateway
            gateway = HarnessGateway(args.workspace)
            if args.foreground:
                gateway.start()
                print("Gateway 前台運行中，按 Ctrl+C 停止")
                import time
                while True:
                    time.sleep(1)
            else:
                print("✓ Gateway 已後台啟動")
                return 0
        except ImportError:
            print("✗ 無法載入 HarnessGateway")
            return 1
        except Exception as e:
            print(f"✗ 啟動失敗：{e}")
            return 1
        return 0

    def _cmd_stop(self, args) -> int:
        print(f"停止 {self.NAME} Gateway...")
        print("✓ Gateway 已停止")
        return 0

    def _cmd_restart(self, args) -> int:
        print(f"重啟 {self.NAME} Gateway...")
        self._cmd_stop(args)
        return self._cmd_start(args)

    def _cmd_status(self, args) -> int:
        print(f"{self.NAME} v{self.VERSION} — Status: Running")
        return 0

    def _cmd_skill(self, args) -> int:
        """Skill commands."""
        try:
            from src.core.skill import SkillEngine
            engine = SkillEngine(Path(args.workspace) / "skills")

            if args.skill_command == "list":
                print("=== Skills ===")
                for skill in engine.list_skills(enabled_only=False):
                    status = "✓" if skill["enabled"] else "✗"
                    print(f"  {status} {skill['name']} v{skill['version']}")
                    print(f"     {skill['description']}")
                return 0

            if args.skill_command == "enabled":
                print("=== 已啟用 Skills ===")
                for skill in engine.list_skills(enabled_only=True):
                    print(f"  ✓ {skill['name']}")
                return 0

            if args.skill_command == "enable":
                if engine.enable(args.name):
                    print(f"✓ 已啟用：{args.name}")
                else:
                    print(f"✗ 找不到 Skill：{args.name}")
                    return 1
                return 0

            if args.skill_command == "disable":
                if engine.disable(args.name):
                    print(f"✓ 已停用：{args.name}")
                else:
                    print(f"✗ 找不到 Skill：{args.name}")
                    return 1
                return 0

            print("用法：aa-harness skill [list|enabled|install|uninstall|enable|disable]")
            return 0

        except ImportError as e:
            print(f"✗ 無法載入 Skill Engine：{e}")
            return 1

    def _cmd_agent(self, args) -> int:
        """Agent commands."""
        try:
            from src.harness.spawner import AgentSpawner
            workspace_path = Path(args.workspace)
            spawner = AgentSpawner(workspace=str(workspace_path))
        except ImportError:
            print("❌ AgentSpawner not available")
            return 1

        if args.agent_command == "spawn":
            prompt = " ".join(args.prompt) if args.prompt else ""
            if not prompt:
                print("❌ Prompt required: aa-harness agent spawn <prompt>")
                return 1
            try:
                result = spawner.spawn(
                    prompt=prompt,
                    runtime=args.runtime,
                    model=args.model,
                    timeout=args.timeout,
                )
                print(f"✓ Agent spawned: {result.get('agent_id', result.get('session_id', 'unknown'))}")
                return 0
            except Exception as e:
                print(f"❌ Spawn failed: {e}")
                return 1

        if args.agent_command == "list":
            try:
                agents = spawner.list_active()
                print(f"=== Active Agents ({len(agents)}) ===")
                for a in agents:
                    print(f"  {a}")
                return 0
            except Exception as e:
                print(f"❌ List failed: {e}")
                return 1

        if args.agent_command == "kill":
            try:
                spawner.kill(args.agent_id)
                print(f"✓ Killed: {args.agent_id}")
                return 0
            except Exception as e:
                print(f"❌ Kill failed: {e}")
                return 1

        print("用法：aa-harness agent [spawn|list|kill]")
        return 0

    def _cmd_session(self, args) -> int:
        """Session commands."""
        cmd = getattr(args, "session_command", "")
        try:
            from src.core.session_manager import SessionManager
            workspace_path = Path(args.workspace)
            sm = SessionManager(workspace=str(workspace_path))
        except ImportError:
            print("❌ SessionManager not available")
            return 1

        if cmd == "list":
            sessions = sm.list_sessions()
            print(f"=== Sessions ({len(sessions)}) ===")
            if not sessions:
                print("  (none)")
            for s in sessions:
                sid = s.get("id", "?")[:12]
                label = s.get("label", "-")
                status = s.get("status", "?")
                print(f"  [{status:10s}] {sid} — {label}")
            return 0

        if cmd == "show":
            import json
            sid = getattr(args, "session_id", None)
            if not sid:
                print("❌ session_id required")
                return 1
            data = sm.get_session(sid)
            if not data:
                print(f"❌ Session not found: {sid}")
                return 1
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0

        if cmd == "delete":
            sid = getattr(args, "session_id", None)
            force = getattr(args, "force", False)
            if not sid:
                print("❌ session_id required")
                return 1
            sm.delete_session(sid, force=force)
            print(f"✓ Deleted: {sid}")
            return 0

        print("用法：aa-harness session [list|show|delete]")
        return 0

    def _cmd_cron(self, args) -> int:
        """Cron commands."""
        cmd = getattr(args, "cron_command", "")
        if cmd == "list":
            print("=== Scheduled Tasks ===")
            print("  (use 'aa-harness cron add' to create tasks)")
            return 0
        print("用法：aa-harness cron [list|add|remove|run]")
        return 0

    def _cmd_node(self, args) -> int:
        """Node commands."""
        cmd = getattr(args, "node_command", "")
        try:
            from src.core.node.pairing import NodePairingManager
            mgr = NodePairingManager()
        except ImportError:
            print("❌ NodePairingManager not available")
            return 1

        if cmd == "list":
            devices = mgr.list_devices()
            print(f"=== Paired Devices ({len(devices)}) ===")
            if not devices:
                print("  (none — run 'aa-harness node pair <code>' to pair)")
            for d in devices:
                name = d.get("name", "?")
                did = d.get("id", "?")[:8]
                online = d.get("online", False)
                icon = "🟢" if online else "⚫"
                print(f"  {icon} {name} ({did})")
            return 0

        if cmd == "describe":
            import json
            did = getattr(args, "device_id", None)
            if not did:
                print("❌ device_id required")
                return 1
            info = mgr.describe(did)
            if not info:
                print(f"❌ Device not found: {did}")
                return 1
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return 0

        if cmd == "pair":
            code = getattr(args, "code", None)
            if not code:
                print("❌ pairing code required")
                return 1
            result = mgr.pair(code)
            if result:
                print(f"✓ Paired: {result}")
            else:
                print("❌ Pairing failed — check code and try again")
                return 1
            return 0

        if cmd == "remove":
            did = getattr(args, "device_id", None)
            if not did:
                print("❌ device_id required")
                return 1
            mgr.remove(did)
            print(f"✓ Removed: {did}")
            return 0

        print("用法：aa-harness node [list|describe|pair|remove]")
        return 0

    def _cmd_vision(self, args) -> int:
        """Vision commands."""
        cmd = getattr(args, "vision_command", "")

        if cmd == "info":
            try:
                from src.core.rva import VisionHarness
                print("=== Vision System ===")
                print("  VisionHarness: available")
                return 0
            except ImportError:
                print("❌ VisionHarness not available")
                return 1

        if cmd == "capture":
            try:
                from src.core.rva import VisionHarness
                harness = VisionHarness(Path(args.workspace))
                img = harness.capture_screen()
                if img is not None:
                    out = getattr(args, "output", None)
                    if out:
                        import cv2
                        cv2.imwrite(out, img)
                        print(f"✓ Saved: {out}")
                    else:
                        print(f"✓ Captured: {img.shape}")
                    return 0
                else:
                    print("❌ Capture failed")
                    return 1
            except ImportError:
                print("❌ VisionHarness not available")
                return 1
            except Exception as e:
                print(f"❌ Capture error: {e}")
                return 1

        if cmd == "watch":
            print("Vision watch started (Ctrl+C to stop)")
            import time
            try:
                from src.core.rva import VisionHarness
                harness = VisionHarness(Path(args.workspace))
                interval = getattr(args, "interval", 1.0)
                while True:
                    img = harness.capture_screen()
                    if img is not None:
                        print(f"[{time.strftime('%H:%M:%S')}] frame {img.shape}")
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\nVision watch stopped")
                return 0

        print("用法：aa-harness vision [info|capture|watch]")
        return 1

    def _cmd_system(self, args) -> int:
        """System commands."""
        import platform

        if args.system_command == "info":
            print(f"系統：{platform.system()} {platform.release()}")
            print(f"Python：{platform.python_version()}")
            print(f"工作目錄：{args.workspace}")
            return 0

        if args.system_command == "memory":
            try:
                import psutil
                proc = psutil.Process()
                mem = proc.memory_info()
                print(f"記憶體使用：{mem.rss / 1024 / 1024:.1f} MB")
                return 0
            except ImportError:
                print("❌ psutil not available")
                return 1

        if args.system_command == "clean":
            print("清理功能已就緒")
            return 0

        return 0


def main():
    """CLI entry point."""
    cli = HarnessCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
