---
name: aa-ocr
description: Integrate Alibaba Open Code Review (ocr) for AutoAgent-TW. Performs deterministic rule matching, git diff targeted analysis, and supports Delegation Mode when API keys are not present.
---

# AutoAgent-TW Alibaba Open Code Review (aa-ocr) Skill

## Goal
為 AutoAgent-TW 提供基於 Alibaba Open Code Review (`ocr`) 的高精準度程式碼審查能力。透過「確定性工程＋LLM 混合架構」，過濾無關檔案噪訊，避免審查行號漂移，並提供無 API Key 時的 Delegation Mode 備援機制。

---

## 1. Prerequisites & Execution Modes

在執行審查前，自動進行環境與模式檢查：

```powershell
# 1. 檢測 ocr CLI 是否已安裝
ocr --version
```

若系統中未安裝 `ocr` CLI，可自動安裝：
```powershell
npm install -g @alibaba-group/open-code-review
```

### 模式判定 (Mode Resolution)
- **Direct Mode (有 API Key)**：若環境變數已設定 `OCR_LLM_TOKEN` / `OCR_LLM_URL`，調用 `ocr review --audience agent` 由 OCR 託管 LLM 執行。
- **Delegation Mode (無 API Key / 本地模式)**：若系統未配置 API Key，自動切換至 Delegation Mode。執行 `ocr delegate preview` 取得 Smart Bundling 檔案群組與 `.opencodereview/rule.json` 規則，由 AutoAgent 本身的大模型（Antigravity Agent）扮演 Reviewer 角色執行審查。

---

## 2. Review Workflows

### 2.1 Workspace Mode (當前變更審查)
審查所有 Staged, Unstaged 與 Untracked 的程式碼變更：
```powershell
ocr review --audience agent -b "AutoAgent-TW automated diff review"
```

### 2.2 Branch / Commit Mode (比對特定分支或 Commit)
```powershell
# 比對分支
ocr review --audience agent --from main --to feature-branch

# 審查特定 Commit
ocr review --audience agent --commit <commit-hash>
```

### 2.3 Delegation Preview Mode (取得過濾與規則)
```powershell
ocr delegate preview
```

---

## 3. Priority Classification & Auto-Fix Routing

將審查結果分類為 3 個優先級：
- **High Priority**：明顯 Bug、資安漏洞（如 Buffer Overflow、Race Condition、記憶體洩漏）或邏輯錯誤。
- **Medium Priority**：效能優化建議、規範與風格問題。
- **Low Priority**：過濾忽視（微小風格調整）。

### 閉環自動修正 (Auto-Fix Routing)
當審查發現 **High Priority** 議題時：
1. 產出 [REVIEW-REPORT.md](file:///z:/AutoAgent-TW/REVIEW-REPORT.md)。
2. 標記狀態為 `[REJECTED]`。
3. 自動引導進入 `/aa-fix` 進行微創手術等級修復與迴歸驗證。

---

## 4. Custom Project Rules
OCR 將自動加載專案目錄下的自訂規則檔 `.opencodereview/rule.json`（若存在）：
```json
{
  "rules": [
    {
      "path": "**/*.cpp",
      "rule": "確認所有指標調用皆包含 NULL 檢查與資源釋放 (RAII)。"
    },
    {
      "path": "**/*.py",
      "rule": "確認所有新增函式皆包含 PEP 484 Type Hints。"
    }
  ]
}
```
