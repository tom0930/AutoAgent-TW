# Research: AutoSkills

## 1. 現有 Skill 基礎設施分析

### ClawHub (src/agents/skills-clawhub.ts)
- `searchClawHubSkills({ query, limit, baseUrl })` — 搜尋 ClawHub 上的技能。
- `installSkillFromClawHub({ workspaceDir, slug, version })` — 下載、解壓、驗證 SKILL.md、安裝到 `skills/<name>/`。
- `updateSkillsFromClawHub({ workspaceDir, slug })` — 更新已追蹤的 Skill。
- Lockfile 管理：`.clawhub/lock.json` 追蹤已安裝版本。
- Origin 記錄：每個 Skill 目錄下 `.clawhub/origin.json`。

### 已有的 Skill Discovery 工具
- `skills.discover` 尚不存在 → **需新增**。
- 現有 `createWebSearchTool` 可用於搜尋 ClawHub API。
- `skills.ts` 提供 workspace skill loading（`loadWorkspaceSkillEntries`）。

### Skill Package 結構（現有 v1）
```
skills/<name>/
├── SKILL.md          # 主提示文件（必需）
├── scripts/          # 腳本
├── examples/         # 參考
└── resources/        # 額外資源
```
**缺少**：`manifest.json`（權限宣告）、`tests/`（自動測試）。

## 2. 實施方案

### 2.1 Skill Package v2（manifest.json 擴展）
- 新增 `manifest.json` 到 Skill 結構最頂層。
- 欄位：`name`, `version`, `description`, `permissions`, `requires`, `tests`, `auto_evolve`, `risk_level`。
- 向後相容：沒有 `manifest.json` 的 Skill 視為 `risk_level: "low"` + 無特殊權限。

### 2.2 Skill Discovery Engine（新增 Tool）
- 新增 `skills.discover(intent)` Agent Tool。
- 流程：查 Local Index → 查 ClawHub API → 回傳 Top-3 候選 + 權限摘要。
- 安裝時走 Approval Gate。

### 2.3 Dynamic Skill Generator（新增 Tool）
- 新增 `skills.generate(intent, requirements)` Agent Tool。
- 使用 subagent 執行：產生 manifest + SKILL.md + tests。
- 在 Sandbox 中驗證後安裝。

### 2.4 Skill Evolution Engine（Cron Job）
- 新增 cron job 定期健檢已安裝 Skill。
- 收集 metrics（success_rate, latency, usage_count）。
- 成功率 < 85% 觸發更新/再生成流程。

## 3. 依賴檢查
- **ClawHub API**：已存在（`src/infra/clawhub.ts`），需擴展 intent search。
- **Sandbox**：已存在（Docker / Node sandbox），需確保 Skill 執行在 sandbox 內。
- **Cron Service**：已存在（`src/cron/`），可新增 skill-health cron job。
- **subagent spawn**：已存在（`src/agents/subagent-spawn.ts`），Skill Generator 可用。

## 4. 已識別的陷阱
- **manifest.json 破壞向後相容**：必須 optional，舊 Skill 正常運作。
- **ClawHub API 變更需協調**：intent search 是新 endpoint，需確認 ClawHub 側支援。
- **Skill 測試環境差異**：sandbox 內 vs 本地環境可能有差異（PATH, deps）。
- **Evolution 無限循環**：Skill 一直低成功率 → 一直重新生成 → 要有 max retry 限制。
- **安全審核疲勞**：太多 approval prompts 讓使用者直接全部 yes → 需要好的 auto-approve 策略。
