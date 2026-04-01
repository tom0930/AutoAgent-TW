import json
import argparse
from pathlib import Path
from datetime import datetime

def bump_version(part="minor"):
    config_path = Path(".planning/config.json")
    if not config_path.exists():
        print("Error: config.json not found")
        return
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    old_version = config.get("version", "1.0.0")
    major, minor, patch = map(int, old_version.split("."))
    
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
        
    new_version = f"{major}.{minor}.{patch}"
    config["version"] = new_version
    # Also update project_name
    config["project_name"] = f"AutoAgent-TW-Resilience-v{new_version}"
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        
    print(f"Bumped version: {old_version} -> {new_version}")
    
    # Append template entry to version_list.md
    version_md = Path("version_list.md")
    if version_md.exists():
        with open(version_md, "a", encoding="utf-8") as f:
            f.write(f"\n\n## [v{new_version}] - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("### Added\n- \n")
            f.write("### Fixed\n- \n")
            
    print("Updated version_list.md template.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=["major", "minor", "patch"], default="patch")
    args = parser.parse_args()
    bump_version(args.part)
