# Plan: AutoSkills

## Wave 1: Skill Package v2 + Discovery Engine（Week 1-2）

### Task 1.1: manifest.json Schema 定義
- **目標**：定義 Skill Package v2 的 `manifest.json` 完整 schema。
- **步驟**：
  1. 在 `src/plugins/manifest.ts` 旁建立 `src/agents/skills/skill-manifest.ts`。
  2. 使用 Zod 定義 schema：`name`, `version`, `permissions`, `risk_level`, `auto_evolve`, `tests`, `requires`。
  3. 在 `skills-install.ts` 的安裝流程中加入 manifest 驗證（optional — 舊 Skill 無 manifest 也可安裝）。
- **預期變更**：`src/agents/skills/skill-manifest.ts`（新）, `src/agents/skills-install.ts`

### Task 1.2: Skill Discovery Tool
- **目標**：Agent 可呼叫 `skills.discover(intent)` 搜尋能力。
- **步驟**：
  1. 新增 `src/agents/tools/skills-discover-tool.ts`。
  2. 實作：先查 local workspace skills → 再查 ClawHub API。
  3. 回傳 Top-3 候選，含 name + description + risk_level + permission 摘要。
  4. 整合到 `createOpenClawTools()` 中。
- **預期變更**：`src/agents/tools/skills-discover-tool.ts`（新）, `src/agents/openclaw-tools.ts`

### Task 1.3: Auto-Install with Approval Gate
- **目標**：Agent 發現所需 Skill 後，一次性確認安裝。
- **步驟**：
  1. 新增 `src/agents/tools/skills-install-tool.ts`。
  2. 安裝前顯示權限摘要（人類可讀）。
  3. 依 risk_level 決定 approval 方式：low=auto, medium=一次確認, high=完整審核。
  4. 安裝後觸發 Gateway skill hot-reload。
- **預期變更**：`src/agents/tools/skills-install-tool.ts`（新）

## Wave 2: Dynamic Skill Generator（Week 3-4）

### Task 2.1: Skill Generator Tool
- **目標**：Agent 可呼叫 `skills.generate(intent, requirements)` 自動產生 Skill。
- **步驟**：
  1. 新增 `src/agents/tools/skills-generate-tool.ts`。
  2. 使用 subagent spawn 產生完整 Skill Package：
     - `manifest.json`（自動推斷 permissions）
     - `SKILL.md`（含 Tools, Examples, Error Handling）
     - `tests/*.json`（至少 3 個測試案例）
  3. 將產生的 package 寫入 temp dir。
- **預期變更**：`src/agents/tools/skills-generate-tool.ts`（新）

### Task 2.2: Skill Sandbox Tester
- **目標**：在安裝前自動驗證新產生的 Skill。
- **步驟**：
  1. 新增 `src/agents/skills/skill-sandbox-test.ts`。
  2. 在 Docker/Node sandbox 中執行 `tests/*.json`。
  3. 驗證 permission 合規性（manifest 中宣告的 vs 實際使用的）。
  4. 通過 → 走 Approval Gate → 安裝。
- **預期變更**：`src/agents/skills/skill-sandbox-test.ts`（新）

### Task 2.3: Pre-install Security Scanner
- **目標**：安裝前靜態分析 Skill 程式碼。
- **步驟**：
  1. 新增 `src/agents/skills/skill-security-scan.ts`。
  2. 檢查：prompt injection 模式、危險指令（`rm -rf`, `curl` to unknown domains）、未宣告的權限使用。
  3. 產生 scan report，High-risk 結果必須人工審核。
- **預期變更**：`src/agents/skills/skill-security-scan.ts`（新）

## Wave 3: Skill Evolution + Health Monitor（Week 5-6）

### Task 3.1: Skill Health Metrics 收集
- **目標**：追蹤每個 Skill 的執行指標。
- **步驟**：
  1. 在 Skill 執行路徑中加入 metrics hook（success/failure/latency/usage_count）。
  2. 持久化到 `~/.openclaw/state/skills/<name>/metrics.json`。
  3. 新增 `skills.health_report(skill_name)` tool 讓 Agent 查詢。
- **預期變更**：`src/agents/skills/skill-metrics.ts`（新）, `src/agents/tools/skills-health-tool.ts`（新）

### Task 3.2: Skill Evolution Cron Job
- **目標**：定期健檢並觸發自動更新/再生成。
- **步驟**：
  1. 新增 cron job 到 `src/cron/` — 每週掃描 `auto_evolve: true` 的 Skills。
  2. success_rate < 85% → 嘗試從 ClawHub 更新。
  3. 無 ClawHub 更新 → 呼叫 Dynamic Skill Generator 產生改進版。
  4. 在 sandbox 測試後產生 Evolution Report。
  5. low-risk auto-approve; 否則等待人工批准。
- **預期變更**：`src/cron/skill-evolution.ts`（新）

### Task 3.3: Rollback 機制
- **目標**：更新失敗時自動回到舊版本。
- **步驟**：
  1. 每次更新前備份至 `skills/<name>/archive/v<old>/`。
  2. 新增 `openclaw skills rollback <name>` CLI 指令。
  3. 新增 `openclaw skills freeze <name>` 停止自動演化。
- **預期變更**：`src/agents/skills-clawhub.ts`, `src/cli/`

## Wave 4: Integration with AutoAgent（Week 7-8）

### Task 4.1: 整合 aa-clawinfo 工作流
- **目標**：讓 `/aa-clawinfo` 報告 OpenClaw 當前與歷史活動。
- **步驟**：
  1. 建立 `aa-clawinfo.md` workflow。
  2. 查詢 Gateway sessions, tasks, cron jobs, skills 狀態。
  3. 產出結構化報告。
- **預期變更**：`global_workflows/aa-clawinfo.md`（新）

### Task 4.2: AutoSkills 與 Autonomous Agent Loop 整合
- **目標**：Agent 在 Goal 執行期間自動觸發 Skill Discovery。
- **步驟**：
  1. 在 Agent 的 tool execution error handler 中加入 "skill missing?" 偵測。
  2. 自動呼叫 `skills.discover` → 建議安裝 → 繼續執行。
- **預期變更**：`src/agents/pi-tool-definition-adapter.ts`

## 驗證標準 (UAT Criteria)
1. **Discovery**：Agent 接收到「幫我用 Selenium 測試網頁」→ 自動搜尋 ClawHub 「selenium-test」技能 → 建議安裝 → 安裝成功。
2. **Generation**：Agent 接收到「幫我建一個可以查匯率的工具」→ 自動產生 currency-converter skill → sandbox 測試通過 → 安裝成功。
3. **Evolution**：一個 success_rate 70% 的 Skill → cron 偵測 → 自動產生改進版 → sandbox 通過 → 報告等待批准。
4. **clawinfo**：`/aa-clawinfo` 正確報告 Gateway 運行中 sessions、最近 tasks、cron jobs、skills 狀態。
