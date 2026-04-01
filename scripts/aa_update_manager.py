import os
import subprocess
import json

def fetch_remote():
    print("Fetching updates from remote...")
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        return True
    except:
        return False

def selective_checkout(paths):
    print(f"Selectively updating: {paths}")
    for path in paths:
        try:
            # Checkout specific paths from Remote
            subprocess.run(["git", "checkout", "origin/master", "--", path], check=True)
            print(f"Updated: {path}")
        except Exception as e:
            print(f"Failed to update {path}: {e}")

def update_version_log(msg):
    # This is normally handled by git-push, but for versionupdate
    # we want to record the update in the local version_list.md
    with open("version_list.md", "a", encoding="utf-8") as f:
        f.write(f"\n- [{os.popen('git rev-parse --short HEAD').read().strip()}] Update Applied: {msg}\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Target modules comma separated (skills,docs,scripts,configs)")
    args = parser.parse_args()
    
    if fetch_remote():
        targets = args.only.split(",") if args.only else ["scripts", ".agents/skills", "README.md", "gitpush.md"]
        # Map logical names to actual paths
        path_map = {
            "skills": ".agents/skills",
            "docs": ["README.md", "gitpush.md", "Schedule_readme.md"],
            "scripts": "scripts",
            "configs": [".planning", "config.json"]
        }
        
        final_paths = []
        for t in targets:
            if t in path_map:
                if isinstance(path_map[t], list): final_paths.extend(path_map[t])
                else: final_paths.append(path_map[t])
            else: final_paths.append(t)
            
        selective_checkout(final_paths)
        print("Selective update completed.")
