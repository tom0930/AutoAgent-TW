import os
import shutil
import time
from typing import Dict, Any, List, Optional

class SkillRollbackManager:
    """
    AutoSkills Rollback Manager (Phase 2 - Task 3.3).
    Ensures that every skill update creates an archive for disaster recovery.
    """
    def __init__(self, skills_dir: str = ".agents/skills"):
        self.skills_dir = skills_dir

    def backup_for_update(self, skill_name: str, version: str) -> str:
        """Backs up the current skill to an archive folder before an update."""
        skill_path = os.path.join(self.skills_dir, skill_name)
        archive_dir = os.path.join(skill_path, "archive")
        version_dir = os.path.join(archive_dir, f"v{version}-{int(time.time())}")
        
        os.makedirs(version_dir, exist_ok=True)
        
        # Copy everything except the archive folder itself
        for item in os.listdir(skill_path):
            if item == "archive": continue
            s = os.path.join(skill_path, item)
            d = os.path.join(version_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        return version_dir

    def rollback(self, skill_name: str, target_version_dir: Optional[str] = None) -> bool:
        """Rolls back the skill to the latest (or specified) archive version."""
        skill_path = os.path.join(self.skills_dir, skill_name)
        archive_dir = os.path.join(skill_path, "archive")
        
        if not os.path.exists(archive_dir):
            # pyrefly: ignore [bad-return]
            return False, "No archive found for this skill."
            
        if not target_version_dir:
            # Pick latest
            versions = sorted(os.listdir(archive_dir))
            # pyrefly: ignore [bad-return]
            if not versions: return False, "No versions found in archive."
            target_version_dir = os.path.join(archive_dir, versions[-1])
            
        print(f"[{skill_name}] Rolling back to version: {os.path.basename(target_version_dir)}")
        
        # 1. Clear current files except archive
        for item in os.listdir(skill_path):
            if item == "archive": continue
            path = os.path.join(skill_path, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
                
        # 2. Restore from archive
        for item in os.listdir(target_version_dir):
            s = os.path.join(target_version_dir, item)
            d = os.path.join(skill_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
                
        # pyrefly: ignore [bad-return]
        return True, f"Successfully rolled back '{skill_name}' to archived version."

if __name__ == "__main__":
    print("Testing Skill Rollback Manager...")
    # Mock some data
    skill_dir = ".agents/skills/dummy-skill"
    os.makedirs(skill_dir, exist_ok=True)
    with open(os.path.join(skill_dir, "test.txt"), "w") as f: f.write("Version 1")
    
    mgr = SkillRollbackManager()
    mgr.backup_for_update("dummy-skill", "1.0.0")
    
    # Modify current
    with open(os.path.join(skill_dir, "test.txt"), "w") as f: f.write("Version 2 - Broken")
    print(f"Current state: {open(os.path.join(skill_dir, 'test.txt')).read()}")
    
    # Rollback
    mgr.rollback("dummy-skill")
    print(f"Rollback state: {open(os.path.join(skill_dir, 'test.txt')).read()}")
