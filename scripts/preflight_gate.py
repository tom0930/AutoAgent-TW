#!/usr/bin/env python3
"""
Preflight Gate — PR/Ship 合併前的風險評估腳本
==============================================
根據 risk-tiers.json 自動判定變更風險等級，
決定需要執行哪些檢查。

用法:
    python scripts/preflight_gate.py                    # 檢查目前 uncommitted changes
    python scripts/preflight_gate.py --against main     # 檢查相對 main 分支的差異
    python scripts/preflight_gate.py --files a.py b.py  # 檢查指定檔案

退出碼:
    0 = low/medium (可自動通過)
    1 = high (需要完整測試)
    2 = critical (需要人工審查)
    3 = 錯誤 (配置問題)

參考:
    Wisely Chen — Harness Engineering 架構全景
    https://ai-coding.wiselychen.com/harness-engineering-architecture-overview-ai-code-production-guardrails/
"""

import json
import subprocess
import sys
import os
import signal
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ── Constants ────────────────────────────────────────────────────────
TIMEOUT_SECONDS = 30
RISK_LEVELS = ["low", "medium", "high", "critical"]
EXIT_CODES = {"low": 0, "medium": 0, "high": 1, "critical": 2}

# ANSI Colors
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

RISK_ICONS = {
    "critical": f"{RED}🚨 CRITICAL{RESET}",
    "high": f"{YELLOW}⚠️  HIGH{RESET}",
    "medium": f"{CYAN}📋 MEDIUM{RESET}",
    "low": f"{GREEN}✅ LOW{RESET}",
}


def _timeout_handler(signum, frame):
    """防止無限循環 (STRIDE: DoS mitigation)"""
    print(f"\n{RED}❌ Preflight gate timed out after {TIMEOUT_SECONDS}s{RESET}")
    sys.exit(3)


def load_risk_contract(repo_root: Path) -> Optional[Dict]:
    """載入 risk-tiers.json"""
    contract_path = repo_root / "risk-tiers.json"
    if not contract_path.exists():
        print(f"{YELLOW}⚠️  risk-tiers.json not found — defaulting to 'medium'{RESET}")
        return None

    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"{RED}❌ Failed to parse risk-tiers.json: {e}{RESET}")
        sys.exit(3)


def get_changed_files(against: str = "HEAD") -> List[str]:
    """取得變更的檔案列表"""
    try:
        # 先嘗試 staged + unstaged
        result = subprocess.run(
            ["git", "diff", "--name-only", against],
            capture_output=True, text=True, timeout=10
        )
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # 加上 staged 的
        result2 = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10
        )
        staged = result2.stdout.strip().split("\n") if result2.stdout.strip() else []

        # 加上 untracked
        result3 = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, timeout=10
        )
        untracked = result3.stdout.strip().split("\n") if result3.stdout.strip() else []

        all_files = list(set(files + staged + untracked))
        return [f for f in all_files if f]  # 過濾空字串

    except subprocess.TimeoutExpired:
        print(f"{RED}❌ git diff timed out{RESET}")
        sys.exit(3)
    except FileNotFoundError:
        print(f"{RED}❌ git not found in PATH{RESET}")
        sys.exit(3)


def match_file_to_tier(filepath: str, tiers: Dict) -> str:
    """
    將檔案匹配到最高風險等級。
    使用 fnmatch glob 模式匹配。
    """
    # 從高到低匹配，取最高風險等級
    for level in reversed(RISK_LEVELS):
        tier = tiers.get(level, {})
        patterns = tier.get("paths", [])
        for pattern in patterns:
            # 支援 ** glob
            if fnmatch.fnmatch(filepath, pattern):
                return level
            # 也嘗試 basename 匹配 (e.g., "*.md" matches "README.md")
            if fnmatch.fnmatch(os.path.basename(filepath), pattern):
                return level
    return "low"


def assess_risk(files: List[str], contract: Optional[Dict]) -> Tuple[str, Dict[str, List[str]]]:
    """
    評估所有變更檔案的風險等級。
    回傳: (最高風險等級, {tier: [files]})
    """
    if not contract:
        return "medium", {"medium": files}

    tiers_config = contract.get("tiers", {})
    categorized: Dict[str, List[str]] = {level: [] for level in RISK_LEVELS}
    max_level = "low"

    for f in files:
        level = match_file_to_tier(f, tiers_config)
        categorized[level].append(f)
        if RISK_LEVELS.index(level) > RISK_LEVELS.index(max_level):
            max_level = level

    return max_level, categorized


def print_report(risk_level: str, categorized: Dict[str, List[str]], total_files: int):
    """輸出風險報告"""
    print(f"\n{'='*60}")
    print(f"{BOLD}  🛡️  Preflight Gate — Risk Assessment Report{RESET}")
    print(f"{'='*60}")
    print(f"  📊 Overall Risk Level: {RISK_ICONS.get(risk_level, risk_level)}")
    print(f"  📁 Total Changed Files: {total_files}")
    print(f"{'─'*60}")

    for level in reversed(RISK_LEVELS):
        files = categorized.get(level, [])
        if files:
            icon = RISK_ICONS.get(level, level)
            print(f"\n  {icon} ({len(files)} files):")
            for f in files[:10]:  # 最多顯示 10 個 (STRIDE: Info Disclosure mitigation)
                print(f"    • {f}")
            if len(files) > 10:
                print(f"    ... and {len(files) - 10} more")

    print(f"\n{'─'*60}")

    # 根據風險等級顯示要求
    if risk_level == "critical":
        print(f"  {RED}🚨 BLOCKED — Critical changes detected!{RESET}")
        print(f"  {RED}   → Requires 2+ reviewers + staging + rollback plan{RESET}")
        print(f"  {RED}   → Run: aa-review --tier critical{RESET}")
    elif risk_level == "high":
        print(f"  {YELLOW}⚠️  HIGH RISK — Full test suite required{RESET}")
        print(f"  {YELLOW}   → Run: python -m pytest tests/ --tb=short{RESET}")
    elif risk_level == "medium":
        print(f"  {CYAN}📋 MEDIUM — Lint + type check recommended{RESET}")
        print(f"  {CYAN}   → Run: python -m py_compile <changed_files>{RESET}")
    else:
        print(f"  {GREEN}✅ LOW RISK — Fast pass eligible{RESET}")

    print(f"{'='*60}\n")


def run_checks(risk_level: str, categorized: Dict[str, List[str]]) -> bool:
    """根據風險等級執行對應的檢查"""
    all_files = []
    for files in categorized.values():
        all_files.extend(files)

    py_files = [f for f in all_files if f.endswith(".py")]

    if not py_files:
        return True

    # 所有等級：至少做 py_compile
    print(f"\n  🔍 Running py_compile on {len(py_files)} Python files...")
    failed = []
    for f in py_files:
        if not os.path.exists(f):
            continue
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", f],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            failed.append((f, result.stderr.strip()))

    if failed:
        print(f"\n  {RED}❌ py_compile failed for {len(failed)} files:{RESET}")
        for f, err in failed:
            print(f"    • {f}: {err[:100]}")
        return False

    print(f"  {GREEN}✅ All {len(py_files)} Python files compile successfully{RESET}")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Preflight Gate — Risk-tiered change assessment"
    )
    parser.add_argument(
        "--against", default="HEAD",
        help="Git ref to diff against (default: HEAD)"
    )
    parser.add_argument(
        "--files", nargs="*",
        help="Explicit file list to assess (overrides git diff)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON (for CI integration)"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Also run py_compile checks"
    )
    args = parser.parse_args()

    # 設置 timeout (僅 Unix，Windows 上跳過)
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(TIMEOUT_SECONDS)

    # 定位 repo root
    repo_root = Path(__file__).resolve().parent.parent

    # 載入 risk contract
    contract = load_risk_contract(repo_root)

    # 取得變更檔案
    if args.files:
        changed_files = args.files
    else:
        changed_files = get_changed_files(args.against)

    if not changed_files:
        print(f"\n  {GREEN}✅ No changed files detected — nothing to assess.{RESET}\n")
        sys.exit(0)

    # 評估風險
    risk_level, categorized = assess_risk(changed_files, contract)

    # JSON 輸出模式 (for CI)
    if args.json:
        output = {
            "risk_level": risk_level,
            "exit_code": EXIT_CODES.get(risk_level, 0),
            "total_files": len(changed_files),
            "categorized": categorized,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        sys.exit(EXIT_CODES.get(risk_level, 0))

    # 人類可讀報告
    print_report(risk_level, categorized, len(changed_files))

    # 可選：執行檢查
    if args.check:
        if not run_checks(risk_level, categorized):
            sys.exit(3)

    sys.exit(EXIT_CODES.get(risk_level, 0))


if __name__ == "__main__":
    main()
