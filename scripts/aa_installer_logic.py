import os
import sys
import subprocess
import json
import shutil
import time

def check_env():
    print("Checking environment...")
    try:
        subprocess.run(["python", "--version"], check=True, capture_output=True)
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error: Required environment missing ({e})")
        return False

def setup_venv():
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Venv created.")
        
def install_deps():
    print("Installing dependencies...")
    pip_path = os.path.join("venv", "Scripts", "pip.exe") if os.name == "nt" else os.path.join("venv", "bin", "pip")
    if os.path.exists("requirements.txt"):
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)

def main():
    print("=== AutoAgent-TW Installer v1.7.0 ===")
    if check_env():
        setup_venv()
        install_deps()
        print("Setup complete. You can now use AutoAgent-TW!")
    else:
        print("Setup failed.")

if __name__ == "__main__":
    main()
