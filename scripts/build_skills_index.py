import os
import json
import yaml
import pathlib
from typing import List, Dict

LIB_DIR = r"C:\Users\TOM\.gemini\antigravity\skills_library"
INDEX_PATH = r"C:\Users\TOM\.gemini\antigravity\skills\data\skills_index.json"

def parse_skill_md(file_path: str) -> Dict:
    """Parses SKILL.md for frontmatter metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if content.startswith('---'):
            _, frontmatter, _ = content.split('---', 2)
            data = yaml.safe_load(frontmatter)
            return data
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    return {}

def build_index():
    index = []
    lib_path = pathlib.Path(LIB_DIR)
    
    print(f"Scanning {LIB_DIR} for skills...")
    
    for skill_dir in lib_path.iterdir():
        if not skill_dir.is_dir():
            continue
            
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            metadata = parse_skill_md(str(skill_file))
            
            entry = {
                "id": skill_dir.name,
                "name": metadata.get("name", skill_dir.name),
                "description": metadata.get("description", "No description available"),
                "path": str(skill_dir),
                "categories": metadata.get("categories", [])
            }
            index.append(entry)
            
    # Create data directory if not exists
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        
    print(f"Index built with {len(index)} skills at {INDEX_PATH}")

if __name__ == "__main__":
    build_index()
