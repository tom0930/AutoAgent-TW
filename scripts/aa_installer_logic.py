import os
import sys
import subprocess
import json
import shutil
import time
import multiprocessing
import winreg
from pathlib import Path

def get_base_path():
    """Returns the base path (bundled in EXE or local developer path)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    # If we are running from scripts/, go up one level
    current_dir = os.path.abspath(os.path.dirname(__file__))
    if os.path.basename(current_dir) == "scripts":
        return os.path.dirname(current_dir)
    return current_dir

def setup_git_config():
    """Confirms or resets global Git configuration."""
    print("\n--- [Git Configuration] ---")
    try:
        current_name = subprocess.check_output(["git", "config", "--global", "user.name"], text=True).strip()
        current_email = subprocess.check_output(["git", "config", "--global", "user.email"], text=True).strip()
        print(f"Detected current Git: {current_name} <{current_email}>")
        change = input("Do you want to re-configure Git account for this system? (y/N): ").lower()
    except:
        change = 'y'
        print("Git user not detected.")

    if change == 'y':
        new_name = input("Enter Git User Name: ")
        new_email = input("Enter Git Email: ")
        if new_name and new_email:
            subprocess.run(["git", "config", "--global", "user.name", new_name])
            subprocess.run(["git", "config", "--global", "user.email", new_email])
            print("✅ Git account updated.")

def setup_project_config(target_dir):
    """Initializes a fresh config.json for the user's workspace."""
    print("\n--- [Project Initialization] ---")
    proj_name = input("Enter your Project Name (default: 'My_AutoAgent_Project'): ") or "My_AutoAgent_Project"
    
    print("\nSelect Language Mode / 選擇語言模式:")
    print("[1] English (en-US)")
    print("[2] 繁體中文 (zh-TW)")
    choice = input("Enter Choice (1 or 2): ")
    lang = "zh-TW" if choice == "2" else "en-US"
    
    config_data = {
        "project_name": proj_name,
        "version": "2.0.0",
        "mode": "PRO",
        "granularity": "TASK",
        "language": lang,
        "notifications": {
            "browser_panel": True,
            "line_notify": False,
            "voice_announcement": False
        },
        "locales": ["en-US", "zh-TW"]
    }
    
    planning_dir = os.path.join(target_dir, ".planning")
    os.makedirs(planning_dir, exist_ok=True)
    config_path = os.path.join(planning_dir, "config.json")
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created workspace config with Language: {lang}")

def deploy_global_workflows(target_dir):
    """Deploys workflow files to Antigravity's global workflows folder."""
    print("\n--- [Global Integration] ---")
    home = os.path.expanduser("~")
    global_wf_dir = os.path.join(home, ".gemini", "antigravity", "global_workflows")
    os.makedirs(global_wf_dir, exist_ok=True)
    
    # Priority: _agents/workflows, fallback to .agents/workflows
    src_wf_dir = os.path.join(target_dir, "_agents", "workflows")
    if not os.path.exists(src_wf_dir):
        src_wf_dir = os.path.join(target_dir, ".agents", "workflows")

    if os.path.exists(src_wf_dir):
        count = 0
        for wf_file in os.listdir(src_wf_dir):
            if wf_file.endswith(".md") and wf_file.startswith("aa-"):
                shutil.copy2(os.path.join(src_wf_dir, wf_file), os.path.join(global_wf_dir, wf_file))
                count += 1
        print(f"✅ Registered {count} global workflows in {global_wf_dir}")
    else:
        print(f"⚠️ No workflow directory found in {target_dir}")

def register_global_command(target_dir):
    """Creates a CLI shim and adds the target directory to user PATH."""
    cmd_path = os.path.join(target_dir, "autoagent.cmd")
    python_exe = os.path.join(target_dir, "venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(target_dir, "venv", "bin", "python")
    orchestrator_py = os.path.join(target_dir, "scripts", "aa_orchestrate.py")
    
    with open(cmd_path, "w") as f:
        f.write(f'@echo off\n"{python_exe}" "{orchestrator_py}" %*')
    
    if os.name == 'nt':
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            if target_dir.lower() not in current_path.lower():
                ps_command = f"[System.Environment]::SetEnvironmentVariable('Path', '{current_path};{target_dir}', 'User')"
                subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True)
                print(f"✅ Added {target_dir} to User PATH.")
        except Exception as e:
            print(f"⚠️ Could not update PATH automatically: {e}")

def deploy_core_files(target_dir):
    """Copies core files from base_path to target_dir."""
    base_path = get_base_path()
    if os.path.abspath(base_path) == os.path.abspath(target_dir):
        print("Skipping core file deployment (Source == Target)")
        return

    dirs = ["scripts", ".agents", "_agents"]
    files = ["requirements.txt", "README.md", "version_list.md"]
    
    for d in dirs:
        src, dest = os.path.join(base_path, d), os.path.join(target_dir, d)
        if os.path.exists(src):
            if os.path.exists(dest): shutil.rmtree(dest)
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".git", ".planning", ".agent-state"))
            print(f"Deployed {d}/")
    
    for f in files:
        src, dest = os.path.join(base_path, f), os.path.join(target_dir, f)
        if os.path.exists(src): shutil.copy2(src, dest)

def setup_venv(python_cmd, target_dir):
    """Creates a virtual environment using the REAL system python."""
    venv_path = os.path.join(target_dir, "venv")
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment in {venv_path} using {python_cmd}...")
        try:
            subprocess.run([python_cmd, "-m", "venv", "venv"], check=True, cwd=target_dir)
            print("Venv created successfully.")
        except Exception as e:
            print(f"Failed to create venv: {e}")
            raise

def find_python():
    """Attempts to find a valid system python command."""
    for cmd in ["python", "py", "python3"]:
        try:
            subprocess.run([cmd, "--version"], check=True, capture_output=True)
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None

def main():
    print("==========================================")
    print("   AutoAgent-TW Installer v2.0.1 PRO   ")
    print("   (Critical Path & Workflow Fixed)   ")
    print("==========================================")

    multiprocessing.freeze_support()
    
    python_cmd = find_python()
    if not python_cmd:
        print("Fatal Error: Python not found in system PATH.")
        sys.exit(1)

    try:
        target_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
        print(f"Install Location: {target_dir}")
        
        deploy_core_files(target_dir)
        setup_git_config()
        setup_project_config(target_dir)
        setup_venv(python_cmd, target_dir)
        
        pip_path = os.path.join(target_dir, "venv", "Scripts", "pip.exe") if os.name == "nt" else os.path.join(target_dir, "venv", "bin", "pip")
        if os.path.exists(os.path.join(target_dir, "requirements.txt")):
            print("Installing dependencies...")
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True, cwd=target_dir)
        
        deploy_global_workflows(target_dir)
        register_global_command(target_dir)
        
        print("\n" + "="*40)
        print("🎉 SUCCESS! AutoAgent-TW Installed.")
        print("⚠️  請務必重新啟動終端機 (Terminal) 或 IDE 以讓系統辨識 autoagent 全域指令！")
        print("="*40)
        
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")

    input("\nPress Enter to exit.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
