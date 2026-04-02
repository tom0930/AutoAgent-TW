import os
import re
from pathlib import Path
import yaml

class SkillLoader:
    """
    動態載入 .agents/skills/ 下的 Markdown 技能
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.skills_dir = self.project_root / ".agents" / "skills"
        self.skills: dict[str, dict] = {}

    def discover(self) -> dict:
        """掃描目錄並解析所有 .md 技能檔案"""
        if not self.skills_dir.exists():
            print(f"[SkillLoader] Skills directory not found: {self.skills_dir}")
            return {}

        new_skills = {}
        for md_file in self.skills_dir.glob("*.md"):
            try:
                skill_def = self._parse_md_skill(md_file)
                if skill_def and "trigger" in skill_def:
                    new_skills[skill_def["trigger"]] = skill_def
            except Exception as e:
                print(f"[SkillLoader] Failed to parse {md_file.name}: {e}")
        
        self.skills = new_skills
        print(f"[SkillLoader] Discovered {len(self.skills)} custom skills.")
        return self.skills

    def _parse_md_skill(self, file_path: Path) -> dict:
        """解析 Markdown 中的 YAML Frontmatter 與 執行步驟"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取 YAML Frontmatter
        frontmatter_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not frontmatter_match:
            return None

        try:
            metadata = yaml.safe_load(frontmatter_match.group(1))
        except Exception:
            return None

        # 提取主體內容 (執行步驟)
        body = content[frontmatter_match.end():].strip()
        metadata["body"] = body
        metadata["file_path"] = str(file_path)
        
        return metadata

    def get_skill(self, trigger: str) -> dict:
        """根據觸發詞獲取技能定義"""
        return self.skills.get(trigger)

    def list_skills(self) -> list[dict]:
        """列出所有可用技能摘要"""
        return [{"trigger": k, "name": v.get("name"), "description": v.get("description")} 
                for k, v in self.skills.items()]
