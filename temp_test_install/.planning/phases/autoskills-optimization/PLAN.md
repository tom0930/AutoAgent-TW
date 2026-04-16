# PLAN: AutoSkills 優化 — Bundle 精簡 + Bridge 架構

**Status**: EXECUTED (Phase A/B)  
**Phase**: autoskills-optimization

## 1. 任務拆解

- [x] **Task 1: 建立存檔庫**
  - 將 1505 個 skills 移至 `skills_library/`。
- [x] **Task 2: 恢復核心技能**
  - 從備份恢復 126 個自訂技能。
  - 激活 7 個社群 Bundle (~42 個技能)。
- [x] **Task 3: 建立索引系統**
  - [x] 撰寫 `scripts/build_skills_index.py`。
  - [x] 生成 `skills_index.json`。
- [x] **Task 4: 建置 Bridge Skill**
  - [x] 建立 `skills/antigravity-awesome-bridge/SKILL.md`。
  - [x] 實作意圖感知指令。
- [x] **Task 5: 升級 MCP 伺服器**
  - [x] 更新 `auto_skills_server.py` 實作 search/get/install 工具。

## 2. UAT 驗證準則

- [ ] **UAT 1: 數量驗證**
  - 活躍技能數應在 100-180 之間。
  - Library 技能數應維持 1500+。
- [ ] **UAT 2: 索引完整性**
  - `skills_index.json` 應包含 1500+ 個條目。
- [ ] **UAT 3: Bridge 功能測試**
  - 呼叫 `search_skills` 應能找到冷門技能（如 odoo）。
  - 呼叫 `get_skill_content` 應能讀取庫中內容。
- [ ] **UAT 4: 啟動效能測試**
  - 重啟後的技能掃描時間應顯著下降。

## 3. 執行指令

```powershell
# 驗證數量
(Get-ChildItem "$HOME\.gemini\antigravity\skills" -Directory).Count
(Get-ChildItem "$HOME\.gemini\antigravity\skills_library" -Directory).Count

# 驗證索引
python scripts/build_skills_index.py
```
