# RESEARCH: Code Review vs. Code-Review-Skill Comparison

## 1. 現狀分析 (Current State: Standard Code Review)
目前的 Code Review (CR) 主要由 AI 隨機觸發或透過 `gitlens_start_review` 進行：
- **核心能力**：發現 Bug、指出邏輯錯誤、簡單的風格建議。
- **缺點**：
    - 缺乏系統化的檢查清單 (Checklist)。
    - 反饋混亂，沒有區分「建議 (Suggestion)」與「阻斷 (Blocking)」。
    - 較少關注架構、文檔完整度及長期維護性。
    - 審核標準隨 Session 波動（不穩定）。

## 2. 目標分析 (Target State: Code-Review-Skill Enhanced)
加入 `code-review-skill` 後，CR 演進為專業審計模式：
- **全方位覆蓋**：從整體 PR 描述、代碼質量、架構設計、文檔註解到測試覆蓋。
- **反饋標準化**：使用明確的標籤 (`[Blocking]`, `[Suggestion]`, `[Nitpick]`)。
- **決策透明度**：明確定義 Approve 條件，確保每個 PR 達到上線品質。
- **知識分享**：強調「為什麼」而非僅是「做了什麼」。

## 3. 差異點總結
| 維度 | 現有 Code Review | 加入 Code-Review-Skill 後 |
| :--- | :--- | :--- |
| **審查深度** | 邏輯與語法層面 | 6 大維度全方位掃描 (SOP) |
| **反饋分類** | 統一描述 | 分類明確 (Blocking/Suggestion/Nitpick) |
| **安全性** | 偶爾提及 | 強制威脅建立與資安漏洞檢查 |
| **測試要求** | 基本驗證 | 強制檢查測試覆蓋率與 Regression |
| **團隊規範** | 個人主觀判斷 | 基於團隊通用 Checklist v1.0 |
| **文件管理** | 檢查是否有代碼 | 檢查 JSDoc/Swagger/README 的同步更新 |

## 4. 實施關鍵
將 `code-review-skill.md` 作為 CR 階段的底層協議，確保所有反饋都具備建設性且目標明確。
