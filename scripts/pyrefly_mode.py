#!/usr/bin/env python3
"""
AutoAgent-TW Pyrefly Mode Manager
=====================================
控制 Pyrefly 的運作模式：
  - daemon : LSP 常駐模式（IDE 整合，1-4GB RAM）
  - oneshot: CLI 一次性模式（/aa-qa 按需執行，0MB 常駐）

用法:
    python scripts/pyrefly_mode.py status      # 查看目前狀態
    python scripts/pyrefly_mode.py disable     # 停用 LSP daemon（節省 1-4GB）
    python scripts/pyrefly_mode.py enable      # 重新啟用 LSP daemon
    python scripts/pyrefly_mode.py kill        # 立即 kill 當前 pyrefly 進程
"""

import os
import sys
import shutil
import psutil
from pathlib import Path

PYREFLY_EXE = Path(r"c:\Users\TOM\.antigravity\extensions\meta.pyrefly-0.62.0-win32-x64\bin\pyrefly.exe")
PYREFLY_EXE_DISABLED = PYREFLY_EXE.with_suffix(".exe.disabled")


def get_running_procs():
    """Return list of running pyrefly processes."""
    procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            if "pyrefly" in proc.info["name"].lower():
                mb = proc.info["memory_info"].rss / 1024 / 1024
                procs.append((proc.pid, proc.info["name"], mb))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return procs


def kill_all():
    """Kill all pyrefly processes."""
    killed = 0
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = proc.info.get("name", "").lower()
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            if "pyrefly" in name or "pyrefly" in cmdline:
                proc.kill()
                print(f"  ✅ Killed PID {proc.pid} ({proc.info.get('name')})")
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed


def cmd_status():
    procs = get_running_procs()
    exe_exists = PYREFLY_EXE.exists()
    disabled_exists = PYREFLY_EXE_DISABLED.exists()

    print("=" * 50)
    print("  Pyrefly Mode Manager — Status")
    print("=" * 50)

    if exe_exists:
        print(f"  Executable : ✅ ACTIVE  ({PYREFLY_EXE})")
    elif disabled_exists:
        print(f"  Executable : ⛔ DISABLED ({PYREFLY_EXE_DISABLED})")
    else:
        print(f"  Executable : ❓ NOT FOUND")

    if procs:
        print(f"  Processes  : 🔴 RUNNING ({len(procs)} instance(s))")
        for pid, name, mb in procs:
            print(f"               PID {pid} — {mb:.0f} MB")
    else:
        print(f"  Processes  : 🟢 NOT RUNNING (memory free)")

    print()
    if exe_exists and procs:
        print("  Current mode: LSP DAEMON (high memory)")
        print("  → Run: python scripts/pyrefly_mode.py disable")
    elif not exe_exists:
        print("  Current mode: ONE-SHOT CLI (memory efficient)")
        print("  → Type check: python scripts/shadow_check.py --action check --kill-after")
    else:
        print("  Executable exists but not running — IDE will restart on next .py open")


def cmd_disable():
    print("[Pyrefly Mode] Switching to ONE-SHOT CLI mode...")

    # Step 1: Kill running processes
    procs = get_running_procs()
    if procs:
        print(f"  Killing {len(procs)} running process(es)...")
        kill_all()
    else:
        print("  No running processes.")

    # Step 2: Rename exe to prevent IDE restart
    if PYREFLY_EXE.exists():
        try:
            PYREFLY_EXE.rename(PYREFLY_EXE_DISABLED)
            print(f"  Renamed: pyrefly.exe → pyrefly.exe.disabled")
            print(f"  ✅ Pyrefly LSP daemon DISABLED. IDE cannot restart it.")
        except PermissionError:
            print(f"  ⚠️  Could not rename exe (process may still be running).")
            print(f"  Try again in a few seconds.")
            sys.exit(1)
    elif PYREFLY_EXE_DISABLED.exists():
        print(f"  Already disabled (pyrefly.exe.disabled exists).")

    print()
    print("  Memory savings: ~1-4 GB freed")
    print("  To run type check: python scripts/shadow_check.py --action check --kill-after")
    print("  To re-enable:      python scripts/pyrefly_mode.py enable")


def cmd_enable():
    print("[Pyrefly Mode] Switching to LSP DAEMON mode...")

    if PYREFLY_EXE_DISABLED.exists():
        try:
            PYREFLY_EXE_DISABLED.rename(PYREFLY_EXE)
            print(f"  Renamed: pyrefly.exe.disabled → pyrefly.exe")
            print(f"  ✅ Pyrefly LSP daemon ENABLED.")
            print(f"  Reopen a .py file to trigger IDE restart of Pyrefly.")
        except PermissionError:
            print(f"  ⚠️  Could not rename file.")
            sys.exit(1)
    elif PYREFLY_EXE.exists():
        print(f"  Already enabled.")
    else:
        print(f"  ❌ Neither pyrefly.exe nor pyrefly.exe.disabled found at expected path.")
        print(f"     Path: {PYREFLY_EXE.parent}")


def cmd_kill():
    print("[Pyrefly Mode] Killing all pyrefly processes...")
    count = kill_all()
    if count == 0:
        print("  No pyrefly processes found.")
    else:
        print(f"  ✅ Killed {count} process(es). Memory freed.")


COMMANDS = {
    "status": cmd_status,
    "disable": cmd_disable,
    "enable": cmd_enable,
    "kill": cmd_kill,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print(f"Available commands: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    COMMANDS[sys.argv[1]]()
