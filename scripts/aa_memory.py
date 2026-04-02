import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.memory.memory_store import MemoryStore

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Memory Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Memory commands")

    # List Command
    parser_list = subparsers.add_parser("list", help="List all memories")
    parser_list.add_argument("--level", type=str, default="L2", choices=["L1", "L2", "L3"])

    # Add Command
    parser_add = subparsers.add_parser("add", help="Add a new memory")
    parser_add.add_argument("content", type=str, help="Memory content")
    parser_add.add_argument("--level", type=str, default="L2", choices=["L1", "L2", "L3"])
    parser_add.add_argument("--tags", type=str, help="Comma separated tags")

    # Delete Command
    parser_delete = subparsers.add_parser("delete", help="Delete a memory")
    parser_delete.add_argument("id", type=str, help="Memory ID (or prefix)")
    parser_delete.add_argument("--level", type=str, default="L2", choices=["L1", "L2", "L3"])

    # Focus Command
    parser_focus = subparsers.add_parser("focus", help="Focus completely on one memory (ignore others)")
    parser_focus.add_argument("id", type=str, help="Memory ID ('clear' to remove focus)")
    parser_focus.add_argument("--level", type=str, default="L2", choices=["L1", "L2", "L3"])

    # Export Command
    parser_export = subparsers.add_parser("export", help="Export active context")
    parser_export.add_argument("--level", type=str, default="L2", choices=["L1", "L2", "L3"])

    args = parser.parse_args()
    store = MemoryStore(str(PROJECT_ROOT))

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list":
        memories = store.list_memories(args.level)
        print(f"--- {args.level} Memories ({len(memories)} items) ---")
        if not memories:
            print("  (Empty) - Use 'add' to create memories.")
        for m in memories:
            status = "[FOCUSED]" if m.get("focus") else ""
            print(f"- {m['id']} {status}:")
            print(f"  Content: {m['content']}")
            print(f"  Tags: {','.join(m.get('tags', [])) or 'None'} | Created: {m.get('timestamp', 'Unknown')}")
            print("-" * 20)
        
        print("\n[HINT] Use 'focus <ID>' to isolate a decision, or 'delete <ID>' to purge outdated context.")
        print("       Use 'focus clear' to restore full context awareness.")
    
    elif args.command == "add":
        tags = args.tags.split(",") if args.tags else []
        mid = store.add_memory(args.content, args.level, tags)
        print(f"[OK] Added memory {mid} to {args.level}")

    elif args.command == "delete":
        if store.delete_memory(args.id, args.level):
            print(f"[OK] Deleted memory {args.id} from {args.level}")
            print(f"[HINT] This context is now permanently removed and will won't affect future AI reasoning.")
        else:
            print(f"[ERROR] Memory {args.id} not found in {args.level}")
            print(f"[HINT] Check 'list' for valid short-IDs (first 8 characters).")

    elif args.command == "focus":
        if store.set_focus(args.id, args.level):
            if args.id.lower() == 'clear':
                print(f"[OK] Cleared all focuses in {args.level}")
                print(f"[HINT] AI will now see ALL memories in this level.")
            else:
                print(f"[OK] Focused on memory {args.id} in {args.level}.")
                print(f"[HINT] AI will ignore other memories to prevent context noise/distraction.")
        else:
            print(f"[ERROR] Memory {args.id} not found in {args.level}")
            print(f"[HINT] Use 'list' to verify the memory ID before focusing.")

    elif args.command == "export":
        print(store.export_context(args.level))

if __name__ == "__main__":
    main()
