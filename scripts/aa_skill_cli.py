import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.skills.skill_loader import SkillLoader

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Skill Manager")
    subparsers = parser.add_subparsers(dest="command")

    # List skills
    subparsers.add_parser("list", help="列出所有已載入的自訂技能")

    # Test skill
    test_parser = subparsers.add_parser("test", help="測試執行指定技能")
    test_parser.add_argument("name", help="技能觸發詞 (如 /commit)")

    args = parser.parse_args()
    loader = SkillLoader(str(PROJECT_ROOT))
    loader.discover()

    if args.command == "list":
        skills = loader.list_skills()
        if not skills:
            print("目前沒有任何已載入的技能。請檢查 .agents/skills/ 目錄。")
            return
        
        print(f"\n{'觸發詞 (Trigger)':<20} {'名稱 (Name)':<30} {'描述 (Description)'}")
        print("-" * 80)
        for s in skills:
            print(f"{s['trigger']:<20} {s['name']:<30} {s['description']}")
        print()

    elif args.command == "test":
        skill = loader.get_skill(args.name)
        if not skill:
            print(f"找不到技能: {args.name}")
            return
        
        print(f"--- 測試技能: {skill.get('name')} ({skill.get('trigger')}) ---")
        print(f"檔案路徑: {skill.get('file_path')}")
        print("-" * 40)
        print(skill.get("body"))
        print("-" * 40)
        print("💡 在正式版中，觸發此指令將交由 Agent 讀取並執行上述步驟。")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
