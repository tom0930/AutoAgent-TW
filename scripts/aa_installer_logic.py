"""
AutoAgent-TW Professional Installer Logic
Author: Tom (Senior Architect)
Version: 2.4.1
License: Proprietary
"""

import os
import sys
import subprocess
import json
import shutil
import logging
import argparse
import winreg
from pathlib import Path
from typing import Optional, Dict, Any, List

# Configure logging for professional output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("AA-Installer")

def get_base_path() -> Path:
    """Returns the base path (bundled in EXE or local developer path)."""
    if getattr(sys, 'frozen', False):
        # pyrefly: ignore [missing-attribute]
        return Path(sys._MEIPASS)
    
    current_dir = Path(__file__).resolve().parent
    if current_dir.name == "scripts":
        return current_dir.parent
    return current_dir

def setup_git_config(auto: bool = False) -> None:
    """Confirms or resets global Git configuration with security awareness."""
    logger.info("Checking Git configuration...")
    try:
        current_name = subprocess.check_output(["git", "config", "--global", "user.name"], text=True).strip()
        current_email = subprocess.check_output(["git", "config", "--global", "user.email"], text=True).strip()
        logger.info(f"Detected Git Identity: {current_name} <{current_email}>")
        
        if auto:
            return

        change = input("Do you want to re-configure Git account for this system? (y/N): ").lower()
        if change == 'y':
            new_name = input("Enter Git User Name: ")
            new_email = input("Enter Git Email: ")
            if new_name and new_email:
                subprocess.run(["git", "config", "--global", "user.name", new_name], check=True)
                subprocess.run(["git", "config", "--global", "user.email", new_email], check=True)
                logger.info("✅ Git identity updated.")
    except Exception as e:
        logger.warning(f"Git not detected or configured: {e}")
        if not auto:
            new_name = input("Enter Git User Name: ")
            new_email = input("Enter Git Email: ")
            if new_name and new_email:
                subprocess.run(["git", "config", "--global", "user.name", new_name], check=True)
                subprocess.run(["git", "config", "--global", "user.email", new_email], check=True)

def setup_project_config(target_dir: Path, auto: bool = False, lang: str = "zh-TW") -> None:
    """Initializes workspace config with persistence and best practices."""
    logger.info("Initializing project configuration...")
    
    config_path = target_dir / ".planning" / "config.json"
    if config_path.exists() and not auto:
        overwrite = input(f"Config already exists at {config_path}. Overwrite? (y/N): ").lower()
        if overwrite != 'y': return

    proj_name = "AutoAgent_Workspace"
    if not auto:
        proj_name = input(f"Enter Project Name (default: '{proj_name}'): ") or proj_name
        print("\nSelect Language Mode:")
        print("[1] English (en-US)")
        print("[2] 繁體中文 (zh-TW)")
        choice = input("Choice (1/2): ")
        lang = "zh-TW" if choice == "2" else "en-US"

    config_data: Dict[str, Any] = {
        "project_name": proj_name,
        "version": "2.4.1",
        "mode": "PRO",
        "granularity": "TASK",
        "language": lang,
        "security_level": "High",
        "notifications": {
            "browser_panel": True,
            "line_notify": False,
            "voice_announcement": False
        },
        "locales": ["en-US", "zh-TW"]
    }
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Workspace configured: {proj_name} ({lang})")

def deploy_global_workflows(target_dir: Path) -> None:
    """Registers workflows in Antigravity's global context to ensure discoverability."""
    logger.info("Registering global workflows...")
    home = Path.home()
    global_wf_dir = home / ".gemini" / "antigravity" / "global_workflows"
    global_wf_dir.mkdir(parents=True, exist_ok=True)
    
    src_wf_dir = target_dir / "_agents" / "workflows"
    if not src_wf_dir.exists():
        src_wf_dir = target_dir / ".agents" / "workflows"

    if src_wf_dir.exists():
        count = 0
        for wf_file in src_wf_dir.glob("aa-*.md"):
            shutil.copy2(wf_file, global_wf_dir / wf_file.name)
            count += 1
        logger.info(f"✅ Registered {count} workflows in {global_wf_dir}")

def register_global_commands(target_dir: Path) -> None:
    """Creates CLI shims and handles PATH injection with safety checks."""
    logger.info("Registering global commands (autoagent, aa-tw)...")
    
    python_exe = target_dir / "venv" / "Scripts" / "python.exe" if os.name == "nt" else target_dir / "venv" / "bin" / "python"
    orchestrator_py = target_dir / "scripts" / "aa_orchestrate.py"
    
    cmds = ["autoagent.cmd", "aa-tw.cmd"]
    for cmd in cmds:
        cmd_path = target_dir / cmd
        with cmd_path.open("w", encoding="ascii") as f:
            f.write(f'@echo off\nSETLOCAL\nSET "PYTHONPATH={target_dir}"\n"{python_exe}" "{orchestrator_py}" %*\nENDLOCAL')
    
    if os.name == 'nt':
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
                try:
                    current_path, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    current_path = ""
                
                target_str = str(target_dir).lower()
                if target_str not in current_path.lower():
                    # Security: Use User-level environment to avoid needing Admin elevation
                    new_path = f"{current_path};{target_dir}" if current_path else str(target_dir)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    # Broadcast environment change
                    subprocess.run(["powershell", "-Command", "ls"], capture_output=True) # Trick to trigger some updates
                    logger.info(f"✅ Added {target_dir} to User PATH.")
        except Exception as e:
            logger.error(f"⚠️ PATH update failed: {e}. Please add {target_dir} to PATH manually.")

def deploy_openclaw(target_dir: Path) -> None:
    """Deploys OpenClaw core with dependency resolution logic (Phase 122)."""
    logger.info("Deploying OpenClaw ecosystem...")
    oc_dest = target_dir / "openclaw"
    
    # Check for source on dev machine (Z:\)
    oc_source = Path("Z:/openclaw")
    if oc_source.exists():
        logger.info(f"Syncing from dev source: {oc_source}")
        if oc_dest.exists(): shutil.rmtree(oc_dest)
        shutil.copytree(oc_source, oc_dest, ignore=shutil.ignore_patterns("node_modules", ".git", ".planning", "dist/*.map"))
        
        # Init registry
        logger.info("Initializing metadata registry (npm install)...")
        try:
            subprocess.run(["npm.cmd", "install"], cwd=oc_dest, check=True, shell=True, capture_output=True)
            logger.info("✅ OpenClaw registry initialized.")
        except Exception as e:
            logger.warning(f"OpenClaw npm install failed: {e}")
    
    # Create OpenClaw Shim
    oc_shim = target_dir / "openclaw.cmd"
    with oc_shim.open("w", encoding="ascii") as f:
        f.write(f'@echo off\nnode "{oc_dest / "openclaw.mjs"}" %*')

def setup_venv(target_dir: Path) -> Path:
    """Creates a high-performance virtual environment."""
    venv_dir = target_dir / "venv"
    if not venv_dir.exists():
        logger.info(f"Creating Venv at {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True, cwd=target_dir)
    
    return venv_dir / "Scripts" / "python.exe" if os.name == "nt" else venv_dir / "bin" / "python"

def main() -> None:
    parser = argparse.ArgumentParser(description="AutoAgent-TW Industrial Installer")
    parser.add_argument("--target", type=str, default=os.getcwd(), help="Installation directory")
    parser.add_argument("--auto", action="store_true", help="Non-interactive mode")
    parser.add_argument("--lang", type=str, default="zh-TW", help="Default language")
    args = parser.parse_args()

    target_dir = Path(args.target).resolve()
    
    print("\n" + "="*50)
    print("   🚀 AutoAgent-TW Industrial Installer v2.4.1")
    print("   Architecture by Tom (Senior Architect)")
    print("="*50 + "\n")

    try:
        # 1. Base files deployment (if running from bundled exe)
        # deploy_core_files(target_dir) # Logic omitted for brevity, handled by copytree if needed
        
        # 2. Virtual Env
        python_exe = setup_venv(target_dir)
        
        # 3. Dependencies
        req_file = target_dir / "requirements.txt"
        if req_file.exists():
            logger.info("Installing core dependencies...")
            subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True, capture_output=True)
            subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(req_file)], check=True)
        
        # 3.5 Toolchain Setup (uv, ty, pyrefly, pre-commit)
        logger.info("Setting up Python type-checker toolchain (Ty & Pyrefly)...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "uv"], check=False, capture_output=True)
        
        logger.info("Installing Ty (Astral) [Fast Provider]...")
        subprocess.run([str(python_exe), "-m", "uv", "tool", "install", "ty"], check=False, capture_output=True)
        
        logger.info("Installing Pyrefly (Meta) [Shadow Checker]...")
        subprocess.run([str(python_exe), "-m", "uv", "tool", "install", "pyrefly"], check=False, capture_output=True)

        git_dir = target_dir / ".git"
        if git_dir.exists():
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            pre_commit_path = hooks_dir / "pre-commit"
            hook_script = f'''#!/bin/sh
# AutoAgent-TW Shadow Check Hook
echo "[AutoAgent Guard] Running Shadow Check via Pyrefly..."
if [ -f "scripts/shadow_check.py" ]; then
    python scripts/shadow_check.py --action check --kill-after
else
    echo "⚠️ scripts/shadow_check.py not found. Skipping shadow check."
fi
'''
            with pre_commit_path.open("w", encoding="utf-8", newline='\n') as f:
                f.write(hook_script)
            logger.info("✅ Installed Git Pre-commit Hook for Shadow Check.")

        # 4. OpenClaw
        deploy_openclaw(target_dir)
        
        # 5. Configurations
        setup_git_config(auto=args.auto)
        setup_project_config(target_dir, auto=args.auto, lang=args.lang)
        
        # 6. Global Integration
        deploy_global_workflows(target_dir)
        register_global_commands(target_dir)
        
        # 7. Memory System (MemPalace)
        if (target_dir / "venv").exists():
            vault_marker = target_dir / "mempalace.yaml"
            if not vault_marker.exists():
                logger.info("Initializing MemPalace Memory Vault...")
                # Use -m to ensure venv context
                try:
                    subprocess.run([str(python_exe), "-m", "mempalace", "--palace", str(target_dir), "init", str(target_dir)], check=True, capture_output=True)
                    logger.info("✅ MemPalace initialized.")
                except Exception as e:
                    logger.warning(f"MemPalace init failed: {e}")
            else:
                logger.info("MemPalace Memory Vault verified (already exists).")
            
        print("\n" + "✅" * 20)
        print("🎉 INSTALLATION COMPLETE!")
        print(f"📍 Location: {target_dir}")
        print("💡 Commands ready: 'autoagent' and 'aa-tw'")
        print("⚠️  PLEASE RESTART YOUR TERMINAL FOR PATH CHANGES TO TAKE EFFECT.")
        print("✅" * 20 + "\n")

    except Exception as e:
        logger.error(f"FATAL: Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
