"""
AutoAgent-TW Distribution Packaging Script
Author: Tom (Senior Architect)
Version: 1.0.0
Description: Sanitizes and packages the workspace into a clean installation bundle.
"""

import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AA-Packager")

def make_dist():
    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist_package"
    
    logger.info(f"Starting distribution packaging at {dist_dir}...")
    
    if dist_dir.exists():
        logger.info("Cleaning up existing dist directory...")
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Define what to include
    includes = [
        "src",
        "scripts",
        "bin",
        ".agents",
        "_agents",
        "doc",
        ".planning",
        "requirements.txt",
        "README.md",
        "ARCHITECTURE.md",
        "SECURITY.md",
        "ROADMAP.md",
        ".planning/PROJECT.md"
    ]
    
    # Define what to exclude (for sanitization)
    global_excludes = [
        "__pycache__",
        ".git",
        ".env",
        ".agent-state",
        "scratch",
        "temp",
        "credentials",
        "*.log",
        "*.png",
        "*.webp",
        "*.zip",
        "node_modules",
        "dist_package",
        ".planning/phases", # Exclude specific phase history
        ".planning/RESEARCH.md",
        ".planning/PLAN.md"
    ]
    
    def ignore_func(path, names):
        ignored_names = []
        for name in names:
            # Match global exclude patterns
            is_ignored = False
            for pattern in global_excludes:
                if pattern.startswith("*."):
                    if name.endswith(pattern[1:]): 
                        is_ignored = True
                        break
                elif name == pattern:
                    is_ignored = True
                    break
            
            if is_ignored:
                ignored_names.append(name)
        return ignored_names

    for item in includes:
        src = root_dir / item
        dst = dist_dir / item
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst, ignore=ignore_func)
                logger.info(f"✅ Copied Directory: {item}")
            else:
                shutil.copy2(src, dst)
                logger.info(f"✅ Copied File: {item}")
        else:
            logger.warning(f"⚠️ Missing source: {item}")

    # Create empty but necessary placeholders
    logger.info("Creating placeholders...")
    (dist_dir / ".agent-state").mkdir(exist_ok=True)
    with (dist_dir / ".agent-state" / "README.md").open("w", encoding="utf-8") as f:
        f.write("# Agent State Directory\nThis directory will store dynamic state and checkpoints during runtime.\n")

    # Final touch: Add common installer entry points to root
    shutil.copy2(root_dir / "scripts" / "install_env.ps1", dist_dir / "Install.ps1")
    
    logger.info("\n" + "="*50)
    print(f"🎉 PACKAGE COMPLETE: {dist_dir}")
    print("Ready for ZIP and distribution.")
    print("="*50 + "\n")

if __name__ == "__main__":
    make_dist()
