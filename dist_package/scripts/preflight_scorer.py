import os
import re
import sys
import json
from pathlib import Path

class PreflightScorer:
    def __init__(self, plan_path):
        self.plan_path = Path(plan_path)
        self.content = ""
        if self.plan_path.exists():
            try:
                self.content = self.plan_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback to utf-16 for Windows PowerShell redirected output
                try:
                    self.content = self.plan_path.read_text(encoding='utf-16')
                except:
                    self.content = ""
        self.score = 0
        self.details = []

    def calc_dependency_risk(self):
        """維度 1: 外部相依性 (OAuth, Network, Mounts)"""
        risk_keywords = [r'login', r'auth', r'mount', r'rclone', r'browser', r'oauth', r'token']
        found = []
        for kw in risk_keywords:
            if re.search(kw, self.content, re.IGNORECASE):
                found.append(kw)
        
        risk = len(found) * 1.5
        self.score += min(risk, 4)
        if found:
            self.details.append(f"Detected external dependencies: {found}")

    def calc_context_span(self):
        """維度 2: 上下文廣度 (檔案數量)"""
        # 尋找 [MODIFY] 或檔案路徑格式
        files = re.findall(r'[`\[]([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)[`\]]', self.content)
        unique_files = set(f for f in files if '.' in f and '/' in f or '\\' in f)
        
        count = len(unique_files)
        if count > 5:
            self.score += 3
            self.details.append(f"High context span: {count} files touched.")
        elif count > 2:
            self.score += 1.5

    def calc_skill_gap(self):
        """維度 3: 技能缺口 (SOP 覆蓋率)"""
        # 簡單邏輯：如果內容包含 "research" 或 "investigate"，視為高缺口
        if re.search(r'research|investigate|unknown|study', self.content, re.IGNORECASE):
            self.score += 2
            self.details.append("Work contains research tasks (Skill Gap).")

    def calc_cost_forecast(self):
        """維度 4: Token 與成本預估 (啟發式)"""
        char_count = len(self.content)
        # 假設每 1000 字元預示著更複雜的生成
        if char_count > 5000:
            self.score += 2
            self.details.append(f"Large plan size: {char_count} chars (Cost Risk).")

    def evaluate(self):
        self.calc_dependency_risk()
        self.calc_context_span()
        self.calc_skill_gap()
        self.calc_cost_forecast()
        
        result = {
            "total_score": round(self.score, 2),
            "recommendation": self.get_recommendation(),
            "details": self.details
        }
        return result

    def get_recommendation(self):
        if self.score >= 10:
            return "HUMAN_INTERVENTION_REQUIRED"
        elif self.score >= 7:
            return "SWITCH_TO_ORCHESTRATE"
        else:
            return "PROCEED_WITH_PIPELINE"

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else ".planning/PLAN.md"
    scorer = PreflightScorer(path)
    report = scorer.evaluate()
    print(json.dumps(report, indent=2, ensure_ascii=False))
