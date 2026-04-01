import socket
import subprocess
import webbrowser
import os
import sys
import time
import io
from pathlib import Path

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, 'detach'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')

# Configuration
PORT = 9999
DASHBOARD_REL_PATH = ".agents/skills/status-notifier/templates/status.html"
URL = f"http://localhost:{PORT}/{DASHBOARD_REL_PATH}"

def is_port_active(port):
    """
    Checks if the specified port is open on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_background_server(port):
    """
    Starts a lightweight http.server in the project root as a background process.
    """
    print(f">>> Dashboard: Port {port} is inactive. Starting background server...")
    
    # Target: Project root
    project_root = Path(__file__).resolve().parent.parent
    
    # Command to start the server
    # We use CREATE_NO_WINDOW and CREATE_NEW_PROCESS_GROUP on Windows to dissociate from this console
    cmd = [sys.executable, "-m", "http.server", str(port)]
    
    creationflags = 0
    if os.name == 'nt':
        # 0x00000008: DETACHED_PROCESS 
        # 0x00000200: CREATE_NEW_PROCESS_GROUP
        # 0x08000000: CREATE_NO_WINDOW
        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | 0x08000000

    try:
        subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True
        )
        # Give the server a moment to bind to the port
        time.sleep(1.0)
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def open_dashboard():
    """
    Main execution flow: Detect -> Start (if needed) -> Open.
    """
    print(f"🚀 AutoAgent-TW Dashboard Automation (v1.8.0)")
    
    # 1. Check if server is running
    if not is_port_active(PORT):
        if not start_background_server(PORT):
            print("❌ Failed to initiate background server. Abandoning.")
            return
    else:
        print(f"✅ Dashboard server detected on port {PORT}.")

    # 2. Open webbrowser
    print(f"🌐 Opening Browser: {URL}")
    try:
        webbrowser.open_new_tab(URL)
        print("✨ Done. Welcome to the v1.8.0 Dashboard!")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")

if __name__ == "__main__":
    open_dashboard()
