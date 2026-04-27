#!/usr/bin/env python3
"""
Diff Scope Validator — Surgical Change Enforcer
================================================
Checks that every changed file in a git diff traces back to the PLAN.md.
Flags unplanned modifications to prevent drive-by refactoring.

Usage:
    python scripts/diff_scope_check.py --plan .planning/phases/N-*/PLAN.md
    python scripts/diff_scope_check.py --plan PLAN.md --diff-range HEAD~3..HEAD
    python scripts/diff_scope_check.py --plan PLAN.md --staged

Exit codes:
    0 = All changes trace to plan
    1 = Unplanned changes detected
    2 = Error (missing files, parse failure)

Karpathy Principle: "Every changed line should trace directly to the user's request."
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple


def extract_planned_files(plan_path: str) -> Set[str]:
    """Extract file paths mentioned in PLAN.md.

    Looks for patterns like:
      - `src/core/xxx.py`
      - 修改 `filename.py`
      - file: path/to/file
      - 預期變更: path/to/file
    """
    plan_text = Path(plan_path).read_text(encoding="utf-8")
    patterns: list[str] = [
        r"`([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)`",       # backtick-wrapped paths
        r"file:\s*([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)",  # file: references
        r"修改\s*`?([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)", # 中文「修改」
        r"新增\s*`?([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)", # 中文「新增」
        r"刪除\s*`?([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)", # 中文「刪除」
    ]
    files: Set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, plan_text):
            candidate = match.group(1)
            # Filter out obvious non-files
            if "/" in candidate or candidate.count(".") == 1:
                files.add(candidate)
    return files


def get_changed_files(diff_range: str | None = None, staged: bool = False) -> Set[str]:
    """Get list of changed files from git."""
    cmd = ["git", "diff", "--name-only"]
    if staged:
        cmd.append("--staged")
    elif diff_range:
        cmd.append(diff_range)
    else:
        cmd.append("HEAD~1..HEAD")

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print(f"❌ git diff failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(2)

    return {
        f.strip() for f in result.stdout.strip().split("\n") if f.strip()
    }


def classify_changes(
    planned: Set[str], changed: Set[str]
) -> Tuple[Set[str], Set[str], Set[str]]:
    """Classify changed files into planned, unplanned, and planning-only.

    Returns: (matched, unplanned, planning_files)
    """
    # Always allow .planning/ and .agent-state/ changes
    auto_allowed = {".planning/", ".agent-state/", ".geminiignore"}

    planning_files: Set[str] = set()
    actual_changes: Set[str] = set()

    for f in changed:
        if any(f.startswith(prefix) for prefix in auto_allowed):
            planning_files.add(f)
        else:
            actual_changes.add(f)

    # Match: normalize paths for comparison
    normalized_planned = {p.replace("\\", "/").strip("/") for p in planned}

    matched: Set[str] = set()
    unplanned: Set[str] = set()

    for f in actual_changes:
        f_normalized = f.replace("\\", "/").strip("/")
        # Check exact match or suffix match (plan might use relative paths)
        if f_normalized in normalized_planned or any(
            f_normalized.endswith(p) or p.endswith(f_normalized)
            for p in normalized_planned
        ):
            matched.add(f)
        else:
            unplanned.add(f)

    return matched, unplanned, planning_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate git diff scope against PLAN.md"
    )
    parser.add_argument(
        "--plan", required=True, help="Path to PLAN.md file"
    )
    parser.add_argument(
        "--diff-range", default=None, help="Git diff range (e.g., HEAD~3..HEAD)"
    )
    parser.add_argument(
        "--staged", action="store_true", help="Check staged changes only"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit with error on any unplanned change"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    args = parser.parse_args()

    # Validate inputs
    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"❌ PLAN.md not found: {args.plan}", file=sys.stderr)
        sys.exit(2)

    # Extract and compare
    planned_files = extract_planned_files(str(plan_path))
    changed_files = get_changed_files(args.diff_range, args.staged)

    if not changed_files:
        print("ℹ️  No changes detected.")
        sys.exit(0)

    matched, unplanned, planning = classify_changes(planned_files, changed_files)

    # Output
    if args.json:
        import json
        result = {
            "status": "FAIL" if unplanned else "PASS",
            "planned_files": sorted(planned_files),
            "matched": sorted(matched),
            "unplanned": sorted(unplanned),
            "auto_allowed": sorted(planning),
            "total_changed": len(changed_files),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("🔬 Diff Scope Validator — Surgical Change Report")
        print("=" * 60)
        print(f"\n📋 Plan references {len(planned_files)} file(s)")
        print(f"📝 Git diff shows {len(changed_files)} changed file(s)")
        print(f"   ├── ✅ Planned:     {len(matched)}")
        print(f"   ├── 📁 Auto-allow:  {len(planning)} (.planning/)")
        print(f"   └── ⚠️  Unplanned:  {len(unplanned)}")

        if matched:
            print("\n✅ Planned changes:")
            for f in sorted(matched):
                print(f"   • {f}")

        if unplanned:
            print("\n⚠️  UNPLANNED changes (not in PLAN.md):")
            for f in sorted(unplanned):
                print(f"   • {f}")
            print(
                "\n💡 Karpathy: 'Every changed line should trace "
                "directly to the user\\'s request.'"
            )

    # Exit code
    if unplanned and args.strict:
        sys.exit(1)
    elif unplanned:
        print("\n⚠️  WARNING: Unplanned changes detected (non-strict mode)")
        sys.exit(0)
    else:
        print("\n✅ All changes trace to plan. Surgical precision confirmed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
