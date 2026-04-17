import argparse
import subprocess
import time
import psutil
import sys

def kill_pyrefly():
    """Kills any pyrefly or pyre processes to reclaim memory."""
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info.get('name', '').lower()
            cmdline = " ".join(proc.info.get('cmdline', []) or []).lower()
            if 'pyrefly' in name or 'pyre.exe' in name or 'pyrefly' in cmdline:
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if killed_count > 0:
        print(f"[Shadow Reaper] Killed {killed_count} ghost process(es). Memory reclaimed.")

def run_check():
    """Runs the type check using Pyrefly/Pyre."""
    print("[Shadow Check] Starting deep security type audit via Pyrefly...")
    try:
        # On Windows, depending on the installer, it might be named `pyre` or `pyrefly`.
        # `uv tool install pyrefly` will use `pyrefly`. We use a shell=True fallback if needed, but subprocess should find it in PATH.
        subprocess.run(["pyrefly", "check"], check=True)
        print("[Shadow Check] ✅ Pyrefly deep audit passed.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"[Shadow Check] ❌ Pyrefly deep audit found issues (Exit code: {e.returncode}).")
        return e.returncode
    except FileNotFoundError:
        # Fallback to pyre if pyrefly executable is not mapped directly
        try:
            subprocess.run(["pyre", "check"], check=True)
            print("[Shadow Check] ✅ Pyre deep audit passed.")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"[Shadow Check] ❌ Pyre deep audit found issues (Exit code: {e.returncode}).")
            return e.returncode
        except FileNotFoundError:
            print("[Shadow Check] ⚠️ Pyrefly/Pyre not found in PATH. Make sure it was installed via: uv tool install pyrefly")
            return 0  # Warn but do not fail pre-commit if tool is absent

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Shadow Checker")
    parser.add_argument("--action", choices=["check", "kill"], required=True, help="Action to perform.")
    parser.add_argument("--kill-after", action="store_true", help="Kill pyrefly daemon immediately after check.")
    args = parser.parse_args()

    exit_code = 0

    if args.action == "kill":
        kill_pyrefly()
        sys.exit(0)

    if args.action == "check":
        exit_code = run_check()
        if args.kill_after:
            print("[Shadow Reaper] Terminating daemon to conserve memory...")
            kill_pyrefly()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
