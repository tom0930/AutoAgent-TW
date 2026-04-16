import os
import sys

def setup_starship():
    # Use environment variables and standard library to find profile
    # PowerShell profile path logic: Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
    
    # Try multiple ways to find Documents
    try:
        from win32com.shell import shell, shellcon
        doc_path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
    except ImportError:
        # Fallback to home/Documents or environment
        doc_path = os.path.join(os.path.expanduser("~"), "Documents")
        # Check if OneDrive redirection is active
        onedrive_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Documents")
        if not os.path.exists(doc_path) and os.path.exists(onedrive_path):
            doc_path = onedrive_path

    # The user's path seems to be OneDrive/文件 (or similar)
    # Let's try to find 'WindowsPowerShell' directory recursively under OneDrive if simple paths fail
    
    profile_dir = os.path.join(doc_path, "WindowsPowerShell")
    profile_path = os.path.join(profile_dir, "Microsoft.PowerShell_profile.ps1")
    
    # If the above fails, let's look at the reported profile path from user's environment
    reported_profile = r"C:\Users\TOM\OneDrive\文件\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
    # Wait, I'll try to get it from environment or shell
    
    config_path = r"z:\autoagent-TW\.config\starship.toml"
    config_block = f"""
# --- Starship Integration (AutoAgent-TW Optimized) ---
if (Test-Path "{config_path}") {{
    $env:STARSHIP_CONFIG = "{config_path}"
}}
if (Get-Command starship -ErrorAction SilentlyContinue) {{
    Invoke-Expression (&starship init powershell)
}}
# --- End Starship ---
"""

    # Final attempt: use the path reported earlier but handle the broken character
    # Actually, let's just use the doc_path we found
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir, exist_ok=True)
    
    if os.path.exists(profile_path):
        with open(profile_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
        
    if "starship init" not in content:
        with open(profile_path, 'a', encoding='utf-8') as f:
            f.write(config_block)
        print(f"Successfully updated profile at: {profile_path}")
    else:
        print("Starship already configured.")

if __name__ == "__main__":
    setup_starship()
