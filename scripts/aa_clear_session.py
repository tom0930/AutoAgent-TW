import os
import sys
import json
import time
import argparse
from pathlib import Path

# Add project root to path for imports
AA_CORE = Path(os.getenv("AA_CORE", Path(__file__).resolve().parent.parent))
sys.path.append(str(AA_CORE))

from src.core.context_guard import ContextGuard

def format_timestamp(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

def main():
    parser = argparse.ArgumentParser(
        description="AutoAgent-TW Context Clear & Session Resetter",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--session-key", "-s", type=str, help="Specific session key/id to prune")
    parser.add_argument("--preserve-messages", "-p", type=int, default=3, help="Number of latest messages to retain (default: 3)")
    parser.add_argument("--force", "-f", action="store_true", help="Force wipe even if session is active or busy")
    parser.add_argument("--all", "-a", action="store_true", help="Clean all active sessions")
    parser.add_argument("--sessions-dir", type=str, help="Path to sessions storage directory")
    
    args = parser.parse_args()
    
    # Locate sessions directory
    if args.sessions_dir:
        sessions_dir = Path(args.sessions_dir)
    else:
        sessions_dir = Path(os.getcwd()) / ".agent-state" / "sessions"
        if not sessions_dir.exists():
            # Fallback to standard sessions
            sessions_dir = Path(os.getcwd()) / "sessions"
            
    if not sessions_dir.exists():
        print(f"[-] Error: Session directory not found at {sessions_dir}")
        sys.exit(1)
        
    session_files = list(sessions_dir.glob("session_*.json"))
    if not session_files:
        print("[+] No active sessions found in storage.")
        return
        
    guard = ContextGuard()
    
    sessions_data = []
    for p in session_files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions_data.append((p, data))
        except Exception:
            pass
            
    if not sessions_data:
        print("[+] No readable session records found.")
        return
        
    # Print current token usage metrics as a beautiful table
    print("\n" + "="*95)
    print(f"{'ACTIVE SESSION DIAGNOSTICS':^95}")
    print("="*95)
    print(f"{'Session Key':<20} | {'Kind':<10} | {'Status':<10} | {'Messages':<8} | {'Tokens':<10} | {'Last Active'}")
    print("-"*95)
    
    total_tokens = 0
    total_messages = 0
    for p, s in sessions_data:
        key = s.get("key", p.stem)
        kind = s.get("kind", "main")
        status = s.get("status", "active")
        msg_count = len(s.get("messages", []))
        token_count = s.get("token_count", 0)
        
        # If token count is 0, estimate it dynamically for accurate reporting
        if token_count == 0 and msg_count > 0:
            for m in s.get("messages", []):
                token_count += guard.estimate_tokens(m.get("content", ""))
                
        total_tokens += token_count
        total_messages += msg_count
        
        last_active = s.get("last_active", 0)
        last_active_str = format_timestamp(last_active) if last_active > 0 else "-"
        
        print(f"{key:<20} | {kind:<10} | {status:<10} | {msg_count:<8} | {token_count:<10,} | {last_active_str}")
        
    print("-"*95)
    print(f"{'TOTAL':<20} | {'-':<10} | {'-':<10} | {total_messages:<8} | {total_tokens:<10,} | {'-'}")
    print("="*95 + "\n")
    
    # Identify target sessions
    targets = []
    if args.session_key:
        for p, s in sessions_data:
            if s.get("key") == args.session_key or p.stem == args.session_key or args.session_key in s.get("key", ""):
                targets.append((p, s))
        if not targets:
            print(f"[-] Error: Specific session key '{args.session_key}' not found.")
            sys.exit(1)
    elif args.all:
        targets = sessions_data
    else:
        # Prompt user or default to all if force
        if args.force:
            targets = sessions_data
        else:
            print("[?] Please specify a target session with -s, clean all with -a, or confirm wipe with -f.")
            return
            
    # Perform prune
    now = time.time()
    pruned_count = 0
    
    for p, s in targets:
        key = s.get("key", p.stem)
        status = s.get("status", "active")
        last_active = s.get("last_active", 0)
        
        # Busy check
        is_busy = (status.lower() == "busy") or (now - last_active < 15.0)
        if is_busy and not args.force:
            print(f"[!] Warning: Session '{key}' appears to be BUSY/Active (last active {now - last_active:.1f}s ago). Skipping. Use -f/--force to override.")
            continue
            
        messages = s.get("messages", [])
        system_msgs = [m for m in messages if m.get("role") == "system"]
        other_msgs = [m for m in messages if m.get("role") != "system"]
        
        # Keep only the last N non-system messages
        keep_count = max(0, args.preserve_messages)
        retained_others = other_msgs[-keep_count:] if keep_count > 0 else []
        
        retained_messages = system_msgs + retained_others
        
        # Calculate new token count
        new_token_count = 0
        for m in retained_messages:
            new_token_count += guard.estimate_tokens(m.get("content", ""))
            
        # Update session fields
        s["messages"] = retained_messages
        s["message_count"] = len(retained_messages)
        s["token_count"] = new_token_count
        s["status"] = "active"  # Reset busy status if forced clean
        s["last_active"] = time.time()
        
        # Atomic write back
        temp_path = p.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(s, f, indent=2, ensure_ascii=False)
            if p.exists():
                p.unlink()
            temp_path.rename(p)
            print(f"[+] Successfully pruned session '{key}': Retained {len(retained_messages)}/{len(messages)} messages. Token budget reset to {new_token_count:,} tokens.")
            pruned_count += 1
        except Exception as e:
            print(f"[-] Error: Failed to write session file {p}: {e}")
            if temp_path.exists():
                temp_path.unlink()
                
    print(f"\n[+] Task completed. Cleaned {pruned_count} session files successfully.")

if __name__ == "__main__":
    main()
