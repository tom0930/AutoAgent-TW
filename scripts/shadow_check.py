import argparse
import subprocess
import sys
import time
import os
import psutil
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# AutoAgent-TW Shadow Check v2.0
#
# Architecture: Pyrefly as CLI One-Shot, NOT LSP Daemon
#
#   IDE startup  → kill pyrefly LSP (via tasks.json)
#   /aa-qa       → shadow_check.py --action check [--kill-after]
#   pre-commit   → shadow_check.py --action check --kill-after
#   manual       → shadow_check.py --action kill
#
PYREFLY_EXE = r"c:\Users\TOM\.antigravity\extensions\meta.pyrefly-0.62.0-win32-x64\bin\pyrefly.exe"
PYREFLY_EXE_DISABLED = r"c:\Users\TOM\.antigravity\extensions\meta.pyrefly-0.62.0-win32-x64\bin\pyrefly.exe.disabled"
# ─────────────────────────────────────────────────────────────


def find_pyrefly() -> str:
    """Locate pyrefly executable: bundled Antigravity > PATH fallback."""
    if os.path.isfile(PYREFLY_EXE):
        return PYREFLY_EXE
    if os.path.isfile(PYREFLY_EXE_DISABLED):
        return PYREFLY_EXE_DISABLED
    # Fallback: search PATH
    import shutil
    found = shutil.which("pyrefly")
    if found:
        return found
    raise FileNotFoundError(
        "[Shadow Check] pyrefly not found. "
        f"Expected: {PYREFLY_EXE} or {PYREFLY_EXE_DISABLED}"
    )


def kill_pyrefly(verbose: bool = True) -> int:
    """Kill ALL pyrefly processes (LSP daemon + any stray CLI instances)."""
    killed = 0
    current_pid = os.getpid()
    parent_pid = psutil.Process(current_pid).ppid()

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            pid = proc.pid
            if pid in (current_pid, parent_pid):
                continue

            name = proc.info.get("name", "").lower()
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            
            # Only kill actual pyrefly.exe or LSP daemon, not this script
            if ("pyrefly.exe" in name or "pyrefly.exe" in cmdline) and "python" not in cmdline:
                proc.kill()
                killed += 1
                if verbose:
                    print(f"[Shadow Reaper] Killed pyrefly PID {pid} ({proc.info.get('name', '?')})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed == 0 and verbose:
        print("[Shadow Reaper] No pyrefly processes found. Already clean.")
    elif killed > 0 and verbose:
        print(f"[Shadow Reaper] Total killed: {killed}. Memory reclaimed.")
    return killed


def run_check(
    target_path: str | None = None,
    threads: int = 2,
    config: str | None = None,
    output_file: str | None = None,
    kill_after: bool = False,
) -> int:
    """
    Run pyrefly in one-shot CLI mode (NOT lsp).
    Handles temporarily enabling the .exe if it was disabled.
    """
    exe_path = find_pyrefly()
    temp_enabled = False

    # If it's the .disabled path, rename it back temporarily
    if exe_path.endswith(".disabled"):
        try:
            os.rename(exe_path, PYREFLY_EXE)
            exe_path = PYREFLY_EXE
            temp_enabled = True
            print("[Shadow Check] Temporarily enabling pyrefly.exe for one-shot audit...")
        except Exception as e:
            print(f"[Shadow Check] ❌ Failed to enable pyrefly.exe: {e}")
            return 1

    cmd = [exe_path, "check", "-j", str(threads)]

    if config:
        cmd += ["-c", config]

    if target_path:
        cmd.append(target_path)

    print(f"[Shadow Check] Running: {' '.join(cmd)}")
    print("[Shadow Check] Starting one-shot type audit (this may take 10-30s)...")
    t_start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=False,   # stream stdout directly to terminal
            text=True,
            cwd=str(Path(__file__).parent.parent),  # project root
        )
        elapsed = time.time() - t_start
        exit_code = result.returncode

        if exit_code == 0:
            print(f"[Shadow Check] ✅ Pyrefly audit PASSED ({elapsed:.1f}s)")
        else:
            print(f"[Shadow Check] ⚠️  Pyrefly audit found issues (exit={exit_code}, {elapsed:.1f}s)")

        # Restore disabled state if we temporarily enabled it
        if temp_enabled and kill_after:
            print("[Shadow Check] Restoring disabled state (renaming back to .disabled)...")
            try:
                # Ensure process is fully closed before renaming
                time.sleep(1) 
                os.rename(PYREFLY_EXE, PYREFLY_EXE_DISABLED)
            except Exception as e:
                print(f"[Shadow Check] ⚠️ Failed to restore disabled state: {e}")

        return exit_code

    except FileNotFoundError as e:
        print(f"[Shadow Check] ❌ {e}")
        return 0  # Don't block CI if tool is missing


def main():
    parser = argparse.ArgumentParser(
        description="AutoAgent-TW Shadow Checker v2.0 - Pyrefly as CLI One-Shot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/shadow_check.py --action check              # type check project
  python scripts/shadow_check.py --action check --kill-after # check then kill daemon
  python scripts/shadow_check.py --action kill               # kill LSP daemon only
  python scripts/shadow_check.py --action check src/core/reaper.py  # check single file
""",
    )
    parser.add_argument(
        "--action",
        choices=["check", "kill"],
        required=True,
        help="'check' = run one-shot type check | 'kill' = kill pyrefly daemon",
    )
    parser.add_argument(
        "--kill-after",
        action="store_true",
        default=False,
        help="Kill pyrefly daemon after check completes (recommended for CI/aa-qa)",
    )
    parser.add_argument(
        "--path",
        default=None,
        help="File or directory to check (default: whole project via pyrefly.toml)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=2,
        help="Number of threads (default: 2, lower = less memory spike)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to pyrefly.toml (default: auto-discover from project root)",
    )
    args = parser.parse_args()

    exit_code = 0

    if args.action == "kill":
        kill_pyrefly(verbose=True)
        sys.exit(0)

    if args.action == "check":
        exit_code = run_check(
            target_path=args.path,
            threads=args.threads,
            config=args.config,
            kill_after=args.kill_after,
        )
        if args.kill_after:
            print("\n[Shadow Reaper] --kill-after: terminating pyrefly daemon to conserve memory...")
            time.sleep(0.5)  # brief pause to let check process fully exit
            kill_pyrefly(verbose=True)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
