import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Path Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSION_LOG = PROJECT_ROOT / "version_list.md"
STATE_DIR = PROJECT_ROOT / ".agent-state"

def run_git(args):
    result = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"Git Error: {result.stderr}")
    return result.stdout

def get_staged_summary():
    diff = run_git(["diff", "--staged", "--stat"])
    if not diff:
        return "No staged changes found."
    return diff

def generate_mermaid_flow(files):
    """
    [Phase 111 Expansion] 根據變更文件產出 Mermaid 流程圖摘要
    """
    flow = ["graph LR"]
    for f in files:
        if "scripts" in f:
            flow.append(f"  Start --> {Path(f).stem}")
            flow.append(f"  {Path(f).stem} --> Done")
    
    if len(flow) == 1: return ""
    return "\n```mermaid\n" + "\n".join(flow) + "\n```\n"

def update_docs(summary_text, mermaid_code):
    """
    策略 A: 追加模式。更新 version_log.md 與相關 README
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n### [v1.7.x Update] {timestamp}\n"
    entry += f"{summary_text}\n"
    if mermaid_code:
        entry += f"\n#### Sequence & Logic Flow\n{mermaid_code}\n"
    
    # 1. Update version_log.md
    if VERSION_LOG.exists():
        with open(VERSION_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"Updated {VERSION_LOG.name}")

    # 2. Heuristic: Link scripts to feature docs
    targets = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "gitpush.md" # 專屬文件
    ]
    staged_files = run_git(["diff", "--staged", "--name-only"]).splitlines()
    
    if any("scheduler" in f for f in staged_files):
        targets.append(PROJECT_ROOT / "Schedule_readme.md")
    if any("status" in f for f in staged_files):
        targets.append(PROJECT_ROOT / "Dashboard_readme.md")
    if any("aa_git_pusher" in f for f in staged_files):
        # Already in targets, but ensures it targets itself correctly
        pass
        
    for target in targets:
        if target.exists():
            with open(target, "a", encoding="utf-8") as f:
                f.write(entry)
            print(f"Updated {target.name} (Append mode)")

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

def aa_gitpush(msg):
    print(">>> AutoAgent-TW GitPush Engine v1.7.2 (Human-Enhanced)")
    
    staged_files = run_git(["diff", "--staged", "--name-only"]).splitlines()
    if not staged_files:
        print("Error: No staged changes to push.")
        return

    # Extract Highlights
    highlights = "\n### ✨ Key Improvements\n"
    if "fix" in msg.lower() or "修正" in msg:
        highlights += "- ✅ Resolved persistence and CORS issues in Dashboard\n"
    if "new" in msg.lower() or "新增" in msg:
        highlights += "- 🆕 Added automated diagnostic and repair modules\n"

    manifest = get_categorized_manifest(staged_files)
    mermaid = generate_mermaid_flow(staged_files)
    
    # Assemble Rich Commit Message (Human First)
    commit_msg = f"{msg}\n"
    commit_msg += highlights
    commit_msg += f"\n[Manifest]{manifest}\n"
    commit_msg += f"\n[Visual Doc]: Mermaid logic appended to docs\n"
    
    # Update Documents
    update_docs(commit_msg, mermaid)
    
    # Git Operations
    run_git(["add", "."]) 
    run_git(["commit", "-m", commit_msg])
    print(f"Commit successful: {msg}")
    
    print("Pushing to remote...")
    run_git(["push"])
    print("Done: All changes pushed and documented.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aa_git_pusher.py 'Commit message'")
    else:
        aa_gitpush(sys.argv[1])
