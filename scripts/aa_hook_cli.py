import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.hooks.hook_manager import HookManager

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Hook Manager")
    subparsers = parser.add_subparsers(dest="command")

    # List hooks
    subparsers.add_parser("list", help="列出所有生命週期鉤子與對應動作")

    # Add hook
    add_parser = subparsers.add_parser("add", help="手動新增鉤子配置")
    add_parser.add_argument("event", help="事件名稱 (如 PostToolUse)")
    add_parser.add_argument("id", help="唯一識別碼 (如 code-style-fix)")
    add_parser.add_argument("target", help="執行的指令 (如 ruff check --fix {file_path})")
    add_parser.add_argument("--desc", help="描述內容", default="")

    args = parser.parse_args()
    mgr = HookManager(str(PROJECT_ROOT))
    
    if args.command == "list":
        hooks = mgr.hooks
        if not hooks:
            print("目前沒有任何已載入的鉤子。")
            return
            
        print(f"\n{'事件名 (Event)':<15} {'識別碼 (ID)':<25} {'指令 (Target)'}")
        print("-" * 80)
        for event, hook_list in hooks.items():
            for h in hook_list:
                status = "[ON] " if h.get("enabled", True) else "[OFF]"
                print(f"{event:<15} {status}{h.get('id'):<25} {h.get('target')}")
        print()

    elif args.command == "add":
        new_hook = {
            "id": args.id,
            "description": args.desc,
            "type": "command",
            "target": args.target,
            "enabled": True
        }
        
        # Load existing
        data = {"hooks": {}}
        if mgr.hooks_file.exists():
            with open(mgr.hooks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        if args.event not in data["hooks"]:
            data["hooks"][args.event] = []
            
        # Check if ID exists, update if it does
        found = False
        for i, h in enumerate(data["hooks"][args.event]):
            if h.get("id") == args.id:
                data["hooks"][args.event][i] = new_hook
                found = True
                break
        
        if not found:
            data["hooks"][args.event].append(new_hook)
            
        # Write back
        with open(mgr.hooks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 成功新增/更新鉤子 [{args.id}] 到事件 '{args.event}'")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
