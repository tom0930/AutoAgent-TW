import os
import sys
import json
import argparse
import subprocess
import re
from datetime import datetime
from pathlib import Path

LEDGER_PATH = Path("z:/AutoAgent-TW/data/l3_skill_ledger.jsonl")

class L3TraceHook:
    def __init__(self):
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, data: dict):
        data['timestamp'] = datetime.now().isoformat()
        with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def inject_trailer(self, skill_id, repo, score, content_hash):
        """Injects L3 metadata into the next/current commit message via trailers."""
        try:
            # We log the intent first
            self.log_event({
                "event": "used",
                "skill_id": skill_id,
                "repo": repo,
                "score": score,
                "hash": content_hash
            })
            
            # Instructions to user or subagent: 
            # Use 'git commit -m "msg" --trailer "L3-Skill: {skill_id}"'
            # Or this hook can be called by aa-ship to modify the message.
            print(f"L3-Skill: {skill_id}")
            print(f"L3-Repo: {repo}")
            print(f"L3-Score: {score}")
            print(f"L3-Hash: {content_hash}")
            
        except Exception as e:
            print(f"Error logging L3 usage: {e}", file=sys.stderr)

    def correlate_fix(self, commit_hash):
        """Correlates a fix commit with previous L3 skill usage."""
        try:
            # 1. Get commit message and files
            msg = subprocess.check_output(["git", "log", "-1", "--format=%B", commit_hash], text=True)
            files = subprocess.check_output(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash], text=True).splitlines()
            
            is_fix = any(word in msg.lower() for word in ["fix", "bug", "hotfix", "revert", "修正", "修復"])
            if not is_fix:
                return None

            # 2. Find L3 trailers in the last 30 commits
            logs = subprocess.check_output(["git", "log", "-n", "30", "--format=%H|%B"], text=True).splitlines()
            
            correlations = []
            for line in logs:
                if "|" not in line: continue
                h, b = line.split("|", 1)
                if h == commit_hash: continue
                
                skill_id_match = re.search(r"L3-Skill:\s*(.+)", b)
                if skill_id_match:
                    skill_id = skill_id_match.group(1).strip()
                    # Check file overlap
                    prev_files = subprocess.check_output(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", h], text=True).splitlines()
                    overlap = set(files).intersection(set(prev_files))
                    
                    if overlap:
                        corr = {
                            "event": "correlated_fix",
                            "fix_commit": commit_hash,
                            "skill_usage_commit": h,
                            "skill_id": skill_id,
                            "overlap_files": list(overlap),
                            "confidence": len(overlap) / max(len(files), 1)
                        }
                        self.log_event(corr)
                        correlations.append(corr)
            
            return correlations
        except Exception as e:
            print(f"Correlation failed: {e}", file=sys.stderr)
            return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="L3 Skill Traceability Hook")
    parser.add_argument("--inject", action="store_true", help="Log usage and print trailers")
    parser.add_argument("--skill", type=str, help="Skill ID")
    parser.add_argument("--repo", type=str, help="Repo Name")
    parser.add_argument("--score", type=float, default=0.0, help="Match Score")
    parser.add_argument("--hash", type=str, help="Content Hash")
    
    parser.add_argument("--correlate", type=str, help="Commit hash to analyze for bug correlation")
    
    args = parser.parse_args()
    hook = L3TraceHook()

    if args.inject:
        if not args.skill:
            print("Error: --skill is required for --inject", file=sys.stderr)
            sys.exit(1)
        hook.inject_trailer(args.skill, args.repo, args.score, args.hash)
    elif args.correlate:
        results = hook.correlate_fix(args.correlate)
        if results:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print("No correlation found.")
    else:
        parser.print_help()
