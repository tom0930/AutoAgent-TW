import os
import json
import hashlib
import re
import argparse
import logging
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("L3-Indexer")

DANGEROUS_PATTERNS = [
    r'\beval\s*\(',
    r'\bexec\s*\(',
    r'\bsubprocess\b',
    r'\bos\.system\s*\(',
    r'\bshutil\.rmtree\s*\(',
    r'\brequests\.post\s*\(.+(?:webhook|external)',
    r'\bopen\s*\(.+["\']w["\']\)',
    r'__import__\s*\(',
    r'\bimport\s+ctypes\b',
]

class L3Indexer:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.root = Path(self.config.get('l3_cache_root', 'D:\\git'))
        self.repos = self.config.get('repos', [])
        self.sanitizer_enabled = self.config.get('security', {}).get('enable_content_sanitizer', True)

    def sanitize_content(self, content: str) -> int:
        """Returns risk level: 0=safe, 1=caution, 2=blocked"""
        if not self.sanitizer_enabled:
            return 0
        
        matches = 0
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                matches += 1
        
        if matches >= 2:
            return 2
        elif matches == 1:
            return 1
        return 0

    def parse_skill_file(self, file_path: Path, repo_name: str) -> dict:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Simple YAML frontmatter parser
            fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            metadata = {}
            if fm_match:
                try:
                    metadata = yaml.safe_load(fm_match.group(1))
                except Exception:
                    pass
            
            skill_id = metadata.get('id') or file_path.parent.name
            if skill_id == "skills": # handle repo-root skills
                 skill_id = f"{repo_name}-{file_path.parent.name}"

            return {
                "id": skill_id,
                "name": metadata.get('name') or skill_id,
                "description": metadata.get('description') or "",
                "repo": repo_name,
                "path": str(file_path.relative_to(self.root / repo_name)),
                "abs_path": str(file_path),
                "category": metadata.get('category') or "general",
                "tags": metadata.get('tags') or [],
                "token_count": len(content) // 4,
                "content_hash": hashlib.sha256(content.encode('utf-8')).hexdigest(),
                "risk": self.sanitize_content(content),
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
            }
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None

    def build_index(self):
        all_entries = []
        
        for repo in self.repos:
            if not repo.get('enabled', True):
                continue
            
            repo_path = self.root / repo['name']
            if not repo_path.exists():
                logger.warning(f"Repo path not found: {repo_path}")
                continue
            
            logger.info(f"Scanning repo: {repo['name']}...")
            skill_files = list(repo_path.rglob("SKILL.md"))
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(self.parse_skill_file, f, repo['name']) for f in skill_files]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        all_entries.append(result)

        master_index = {
            "version": "1.0.0",
            "built_at": datetime.now().isoformat(),
            "total_skills": len(all_entries),
            "entries": all_entries
        }

        output_path = Path("z:/AutoAgent-TW/data/l3_master_index.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(master_index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Master index built with {len(all_entries)} skills at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="L3 Master Index Builder")
    parser.add_argument("--root", type=str, help="Override L3 cache root path")
    args = parser.parse_args()

    config_path = "z:/AutoAgent-TW/config/l3_config.json"
    indexer = L3Indexer(config_path)
    if args.root:
        indexer.root = Path(args.root)
    
    indexer.build_index()
