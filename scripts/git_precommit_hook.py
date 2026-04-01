import subprocess
import os
from pathlib import Path
import sys
import io

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, 'detach'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')

def run_git(args):
    result = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8")
    return result.stdout

def get_categorized_manifest(files):
    """
    將檔案按照目錄分類，產生人類可讀的 Manifest
    """
    categories = {
        "🛠️ Logic": [],
        "🎨 UI/Dashboard": [],
        "🧪 Tests/Diag": [],
        "📝 Docs": [],
        "⚙️ Config": [],
        "📦 Other": []
    }
    
    for f in files:
        if "scripts" in f or ".py" in f:
            if "test" in f or "debug" in f: categories["🧪 Tests/Diag"].append(f)
            else: categories["🛠️ Logic"].append(f)
        elif "templates" in f or "status.html" in f or ".js" in f:
            categories["🎨 UI/Dashboard"].append(f)
        elif ".md" in f:
            categories["📝 Docs"].append(f)
        elif ".json" in f or "config" in f:
            categories["⚙️ Config"].append(f)
        else:
            categories["📦 Other"].append(f)
            
    manifest = ""
    for cat, items in categories.items():
        if items:
            manifest += f"\n  {cat}:\n"
            for item in items:
                manifest += f"    - {item}\n"
    return manifest

def main():
    print(">>> AutoAgent-TW Git Hook: Generating Humanized Manifest...")
    
    staged_files = run_git(["diff", "--staged", "--name-only"]).splitlines()
    if not staged_files:
        return

    manifest = get_categorized_manifest(staged_files)
    
    # 產出一個臨時的提示文件或直接回報
    highlights = "\n### ✨ Auto-Generated Manifest\n"
    message = highlights + manifest + "\n[Visual Doc]: Mermaid flow updated accordingly.\n"
    
    # 更專業的做法：讀取 Git 傳入的暫存訊息檔案路徑 (sys.argv[1])
    target_msg_file = sys.argv[1] if len(sys.argv) > 1 else ".git/COMMIT_EDITMSG"
    edit_msg_file = Path(target_msg_file)
    
    if edit_msg_file.exists():
        with open(edit_msg_file, "a", encoding="utf-8") as f:
            f.write(message)
    
    print(f"✅ Manifest added to {edit_msg_file.name}. You can check it in your editor.")

if __name__ == "__main__":
    main()
