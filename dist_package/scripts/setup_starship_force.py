import os

def force_fix_starship():
    doc_path = os.path.join(os.path.expanduser("~"), "OneDrive", "文件")
    if not os.path.exists(doc_path):
        # Fallback to standard Documents
        doc_path = os.path.join(os.path.expanduser("~"), "Documents")
    
    # Target profiles
    profiles = [
        os.path.join(doc_path, "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1"),
        os.path.join(doc_path, "PowerShell", "Microsoft.PowerShell_profile.ps1")
    ]
    
    # Absolute path to Starship (Force)
    starship_exe = r"C:\Users\TOM\AppData\Local\Microsoft\WinGet\Packages\Starship.Starship_Microsoft.Winget.Source_8wekyb3d8bbwe\starship.exe"
    config_path = r"z:\autoagent-TW\.config\starship.toml"
    
    config_block = f"""
# --- Starship Integration (Forced Absolute Path) ---
$env:STARSHIP_CONFIG = "{config_path}"
function starship_init {{
    if (Test-Path "{starship_exe}") {{
        Invoke-Expression (& "{starship_exe}" init powershell)
    }}
}}
starship_init
# --- End Starship ---
"""

    for p in profiles:
        p_dir = os.path.dirname(p)
        if not os.path.exists(p_dir):
            os.makedirs(p_dir, exist_ok=True)
            
        print(f"Targeting profile: {p}")
        
        # Read existing or create new
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
            
        # Remove old blocks if any, and append new one
        # To avoid double entries, let's just keep it simple
        if "# --- Starship Integration" not in content:
            with open(p, 'a', encoding='utf-8') as f:
                f.write(config_block)
            print(f"Successfully injected into: {p}")
        else:
            # Overwrite if it exists to update path
            # For simplicity, we just say skip if it exists for now, 
            # but I'll update it to be sure.
            with open(p, 'w', encoding='utf-8') as f:
                # Basic placeholder replacement logic
                if "# --- Starship Integration" in content:
                    # Clean up old block (basic string split)
                    parts = content.split("# --- Starship Integration")
                    header = parts[0]
                    footer = parts[1].split("# --- End Starship ---")[-1] if "# --- End Starship ---" in parts[1] else ""
                    new_content = header + config_block + footer
                else:
                    new_content = content + config_block
                f.write(new_content)
            print(f"Updated config in: {p}")

if __name__ == "__main__":
    force_fix_starship()
