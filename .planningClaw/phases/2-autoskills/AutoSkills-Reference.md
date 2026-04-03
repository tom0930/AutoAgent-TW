```markdown
# AutoSkills.md

**File**: `.planning/phases/AutoSkills.md`  
**Version**: 1.0 (2026 Q2)  
**Status**: Proposed Architecture  
**Owner**: OpenClaw Core Team  
**Related**: `.planning/STATE.md`, ClawHub, Skill Manifest RFC (#28360), skill-creator skill

## 1. Overview / Vision

**Automated Skills** 是 OpenClaw 從「被動工具集」進化成「自我成長能力層」的核心模組。

目標：讓 Agent 在面對新任務時，能**自動發現、安裝、生成、演化** Skill，無需人類手動介入（僅在高風險操作時請求一次性批准）。

這讓 OpenClaw 真正實現 **Self-Evolving Platform**：  
- Agent 遇到未知需求 → 自動搜尋 ClawHub 或動態生成新 Skill → 安裝並立即使用 → 長期監控並自動優化。

### 核心原則
- **Intent-driven**：一切以 Agent 的當前 Goal 為中心。
- **Safe-by-Default**：所有自動操作都有明確的 Permission Manifest + Sandbox + Human-in-the-Loop 梯度。
- **Versioned & Traceable**：每個 Skill 都有完整歷史、可 rollback。
- **ClawHub-First**：優先重用社群技能，減少重複生成。

## 2. High-Level Architecture

```mermaid
graph TD
    A[Agent<br/>Goal Analyzer] --> B{Skill Discovery}
    B --> C[ClawHub Search API]
    B --> D[Local Skill Index]
    C --> E[Intent-based Auto-Install]
    D --> E

    E --> F[Dynamic Skill Generator]
    F --> G[Skill Package Builder<br/>(manifest.json + SKILL.md + tests + UI)]
    G --> H[Skill Sandbox Tester]
    H --> I[User Approval Gate<br/>(one-time)]
    I --> J[Skill Installer + Loader]

    J --> K[Runtime Executor<br/>(Gateway + Node Sandbox)]
    K --> L[Skill Health Monitor<br/>(Cron + Metrics)]
    L --> M[Skill Evolution Engine]
    M --> N[Auto-Update / Regenerate]
    N --> J
```

**主要元件**：
- **Skill Discovery Engine**（新）
- **Dynamic Skill Generator**（新，基於 skill-creator 擴展）
- **Skill Package Spec v2**（manifest.json + 完整結構）
- **Skill Runtime Sandbox**（已規劃的 #28360 強化版）
- **Skill Health & Evolution System**（新，cron-driven）
- **ClawHub API 擴展**（search/preview/install with intent scoring）

## 3. Skill Package 完整規格（v2）

一個完整的 Skill Package 位於：
```
~/.openclaw/skills/<skill-name>/
├── manifest.json          # 核心宣告（新）
├── SKILL.md               # 主提示 + 行為描述
├── prompts/               # 額外 prompt 檔案（AGENTS.md, TOOLS.md 等）
├── tests/                 # 自動化測試案例（JSON + expected output）
├── scripts/               # 可執行腳本（Python, TS, PowerShell 等）
├── ui/                    # A2UI / Canvas / Tray 整合（可选）
├── references/            # 外部文件或範例
├── .env.example           # 憑證模板（更新時保留）
└── LICENSE
```

**manifest.json 範例**（擴展自 RFC #28360）：
```json
{
  "name": "windows-gui-automation",
  "version": "2.1.0",
  "description": "Native Windows GUI control via FlaUI + Vision fallback",
  "author": "openclaw-community",
  "entry": "SKILL.md",
  "permissions": {
    "fs": { "read": ["**"], "write": ["cache/**"] },
    "system": { "run": ["powershell", "uiautomation"] },
    "gui": { "click": true, "type": true, "capture": true },
    "network": false
  },
  "requires": ["vision-model", "windows-node"],
  "tests": ["tests/basic-click.json"],
  "ui_integration": "canvas",
  "auto_evolve": true
}
```

## 4. 三大自動化流程詳細設計

### 4.1 Skill Discovery（Intent-based Auto-Install）

**觸發時機**：
- Agent 在 Planner 階段分析 Goal 時，發現缺少能力（`available_skills` 中無匹配）。

**流程**：
1. Agent 呼叫內建 Tool `skills.discover(intent)`。
2. Discovery Engine：
   - 查詢 Local Skill Index（向量嵌入 + 關鍵字）。
   - 若無 → 呼叫 ClawHub Search API（新增 endpoint `/search?intent=...&score_threshold=0.85`）。
   - 取得 Top-3 候選 Skill + 預覽（description + permission summary）。
3. Agent 生成「安裝建議」並透過 `sessions_send` 或 WebSocket 推送給使用者：
   - 「我需要 'windows-gui-automation' skill 才能完成此任務，已找到最佳匹配。要現在安裝嗎？（Y/n）」
4. 使用者一次性批准 → 自動下載、解壓、驗證 manifest、安裝到 `~/.openclaw/skills/`。
5. Gateway 立即 hot-reload skill（無需重啟）。

**Fallback**：若 ClawHub 無結果，自動進入 Dynamic Generation。

### 4.2 Dynamic Skill Generation

**能力**：Agent 可以**完整自產**一個 Skill Package（不只是寫 Python）。

**流程**：
1. Agent 呼叫 `skills.generate(intent, requirements)`。
2. 使用專門的 **Skill Creator Agent**（基於現有 skill-creator skill 升級）：
   - 產生 `manifest.json`（自動推斷 permissions）。
   - 產生 `SKILL.md`（含 Tools、Examples、Error Handling）。
   - 產生 `tests/*.json`（至少 3 個測試案例）。
   - 產生 `scripts/` 或 `ui/`（若需要 GUI）。
3. 進入 **Skill Sandbox Tester**：
   - 在隔離 Docker / Node Sandbox 中執行所有 tests。
   - 驗證 permission 合規性與安全性。
4. 通過測試 → 打包成 zip → 請求使用者批准安裝。
5. 安裝後立即註冊到 Agent 的 `available_skills`。

**進階**：支援「fork 現有 skill」並演化（e.g., 從 `browser-control` fork 出 `multi-tab-auth-browser`）。

### 4.3 Skill Evolution（Health Check + Auto-Update）

**背景 Cron Job**（每週日 02:00，由 Gateway 執行）：
- 掃描所有已安裝 Skill（含 `auto_evolve: true`）。
- 收集最近 30 天執行指標（來自 Gateway Metrics）：
  - success_rate（成功率）
  - avg_latency
  - error_types
  - usage_count

**演化決策**：
- success_rate < 85% 或有新版本 → 觸發 Evolution Engine。
- Evolution Engine 會：
  1. 檢查 ClawHub 是否有更新版本。
  2. 若無 → 呼叫 Dynamic Skill Generator 產生「vNext」改進版（帶上歷史失敗 log 作為 context）。
  3. 在 Sandbox 測試新版本。
  4. 產生「Evolution Report」並請求使用者批准更新（或設定 auto-approve low-risk）。
- 更新時保留 `.env` 與 user-specific cache（解決目前 issue #17458）。

**Rollback**：每次更新前自動備份舊版本至 `skills/<name>/archive/v1.0.0/`。

## 5. 安全與治理

- **Permission Manifest**：強制，所有 Skill 必須宣告，違反即拒絕安裝。
- **Runtime Sandbox**：Python/TS 腳本跑在 isolated context（無 fs 逃逸）。
- **Approval Gradient**：
  - Low-risk（read-only）→ 自動安裝（可設定）。
  - Medium-risk（gui/system.run）→ 一次性確認。
  - High-risk（network + credential）→ 每次執行都要確認。
- **Audit Log**：所有 discovery/generate/evolve 操作記錄到 `~/.openclaw/logs/autoskills.log`。
- **Human Override**：隨時可用 `openclaw skills freeze <name>` 停止自動演化。

## 6. Agent 可呼叫的 Tools（新增）

```yaml
- skills.discover(intent: string) → search results
- skills.generate(intent: string, requirements?: object) → package draft
- skills.install(skill_id: string, version?: string) → status
- skills.health_report(skill_name: string) → metrics + suggestions
- skills.evolve(skill_name: string, force?: boolean) → evolution plan
```

## 7. 實施 Roadmap（Q2）

- **Week 1-2**：實作 Skill Discovery Engine + ClawHub intent search API
- **Week 3-4**：Dynamic Skill Generator + Sandbox Tester
- **Week 5-6**：Skill Evolution cron + Health Metrics 收集
- **Week 7**：manifest.json v2 強制 + UI 面板整合（Control UI 新增 AutoSkills 頁籤）
- **Week 8**：測試 + 推出 `openclaw skills auto --enable`

---

**下一步建議**：
1. 將此文件合併到 `.planning/STATE.md` 作為 Q2 主要 Phase。
2. 開啟 GitHub Issue 追蹤 AutoSkills 實作（可直接引用本文件）。
3. 需要我再產出 **manifest.json 完整 schema** 或 **Skill Sandbox 技術細節**，還是 **Multi-Agent Orchestrator 如何與 AutoSkills 配合**？

這個架構已完全相容目前 OpenClaw（ClawHub、SKILL.md、Gateway hot-reload），並直接解決社群現有痛點（自動安裝、更新保留 .env、安全 sandbox）。  
準備好就直接複製成 `.planning/phases/AutoSkills.md` 使用！  
有任何想調整的部分嗎？（例如更強調 Windows GUI Skill、Vision 整合等）



以下是針對 **AutoSkills** 系統的**完整安全機制細節**，以 `.planning/phases/AutoSkills-Security.md` 的形式撰寫，與先前提出的 AutoSkills 架構完全對應。

```markdown
# AutoSkills Security Framework

**File**: `.planning/phases/AutoSkills-Security.md`  
**Version**: 1.0 (2026 Q2)  
**Status**: Proposed Detailed Design  
**Related**: AutoSkills.md, RFC #10890 (Skill Security Framework), Issue #28360 (Skill manifest.json + runtime sandbox), Gateway Security Guide

## 1. 安全設計原則 (Security Principles)

AutoSkills 的安全目標是：在**最大化自動化便利性**的同時，達到 **Defense-in-Depth**（多層防禦），避免單一惡意或有缺陷的 Skill 導致系統性風險。

核心原則：
- **Least Privilege**：每個 Skill 只獲得明確宣告且必要的最小權限。
- **Explicit Consent**：自動發現/生成/更新都需明確的 Permission Manifest + 使用者審核梯度。
- **Sandbox First**：所有動態生成與執行都預設在隔離環境中。
- **Auditability & Traceability**：所有操作都有不可竄改的日誌與版本歷史。
- **Fail-Safe Default**：未知或高風險操作一律阻擋，直到使用者明確批准。
- **Human-in-the-Loop Gradient**：根據風險等級自動調整審核強度。

## 2. 多層安全架構

### 2.1 Layer 1: Skill Manifest 宣告機制（靜態權限聲明）
每個 Skill Package 必須包含 `manifest.json`（強制）：

```json
{
  "name": "windows-gui-automation",
  "version": "2.1.0",
  "author": "openclaw-community",
  "description": "...",
  "permissions": {
    "fs": {
      "read": ["~/.openclaw/skills/**", "~/Documents/allowed/**"],
      "write": ["~/.openclaw/skills/*/cache/**"]
    },
    "system": {
      "run": ["powershell", "FlaUI", "uiautomation"]
    },
    "gui": {
      "click": true,
      "type": true,
      "capture": true,
      "mouse_move": true
    },
    "network": {
      "allow_domains": ["api.example.com"],
      "deny_all": false
    },
    "tools": ["browser", "exec", "vision_analyze"]
  },
  "sandbox_required": true,
  "risk_level": "medium",          // low / medium / high
  "auto_evolve": true
}
```

- **安裝前檢查**：Discovery / Generator 階段會驗證 manifest 是否完整、權限是否合理（例如禁止無故請求 `/etc/` 或系統密鑰路徑）。
- **簽章支援**（未來）：支援 ClawHub 官方簽章或 trusted author 清單，降低供應鏈攻擊風險。

### 2.2 Layer 2: 安裝與審核閘道 (Installation Gate)

**流程安全控制**：
1. **Intent-based Discovery** → 顯示權限摘要（人類可讀）：
   - 「此 Skill 需要：讀取你的 Documents 資料夾、執行 PowerShell、控制滑鼠點擊。」
2. **Approval Gradient**（依 risk_level 自動調整）：
   - **Low**：可設定 auto-approve（僅限 read-only 或官方 ClawHub 技能）。
   - **Medium**（大多數 GUI / exec 技能）：一次性使用者確認（Y/n）。
   - **High**（network + credential + full fs）：必須手動審核 manifest + 測試報告。
3. **Pre-install Scan**：
   - 靜態分析：檢查 prompt injection 模式、危險指令（`rm -rf /`, `curl` to unknown domains 等）。
   - ClawHub 評分 + 社群信任指標。
4. **安裝後隔離**：Skill 預設安裝到 `~/.openclaw/skills/<name>/`，並立即進入 Sandbox 測試。

### 2.3 Layer 3: Runtime Sandbox（執行時隔離）

- **預設 Sandbox 模式**：
  - Dynamic Generated Skill：強制使用 **per-session Docker sandbox** 或 **Node.js isolated vm**。
  - 從 ClawHub 安裝的 Skill：可設定 `sandbox_required: true` 則強制 sandbox。
- **Sandbox 限制**（可由 manifest 進一步收窄）：
  - Filesystem：僅允許 manifest 中宣告的路徑（read/write）。
  - Network：僅允許宣告的 domains，或完全 deny。
  - Exec：僅允許 manifest 中列出的可執行檔（powershell、特定 binary）。
  - GUI 操作：透過專用 GUI Provider Proxy（非直接系統呼叫），所有 click/type 都記錄座標與目標視窗。
  - 記憶體與其他 Skill 隔離：不同 Skill 無法互相存取狀態。
- **Windows Node 專屬**：
  - GUI 操作透過 **FlaUI / UI Automation** 在受控 proxy 中執行。
  - 避免直接 SendKeys 或 raw Win32 API。
  - 結合 Vision 時，screenshot 僅暫存於 sandbox 內部暫存區。

### 2.4 Layer 4: Skill Evolution 安全控制

- **Health Check** 只讀取 Metrics，不修改 Skill 本身。
- **產生新版本** 時：
  - 在全新 Sandbox 中測試（包含 fuzz testing）。
  - 比較新舊版本的 manifest 差異，若權限範圍擴大，必須重新走 Approval Gate。
- **Auto-Update**：僅限 low-risk 且 success_rate 明顯提升的情況；否則產生報告等待人工批准。
- **Rollback**：每次更新前自動備份完整舊版本（含 manifest）。

### 2.5 Layer 5: 監控、稽核與緊急應變

- **全域稽核日誌**：`~/.openclaw/logs/autoskills-audit.log`
  - 記錄：discovery 時間、manifest 內容、使用者批准細節、sandbox 執行結果、evolution 決策。
- **Real-time Alert**：
  - 偵測異常行為（例如 Skill 突然請求未宣告權限、大量 network 呼叫）。
  - 可整合外部 notifier（Telegram、email）。
- **緊急停用**：
  - `openclaw skills block <name>`：立即撤銷所有權限、隔離檔案、阻止呼叫。
  - Gateway hot-reload 支援即時生效。
- **Global Policy Override**：
  - 在 `openclaw.json` 中可設定全域 `skills.sandbox.mode: "strict"`，強制所有 AutoSkills 使用最高隔離等級。

## 3. 風險等級分類與對應措施

| Risk Level | 範例技能類型                  | 審核方式               | Sandbox 強度     | 其他措施                  |
|------------|-------------------------------|------------------------|------------------|---------------------------|
| Low        | 純計算、天氣查詢              | Auto-approve 可開     | Medium           | -                         |
| Medium     | Browser 控制、Windows GUI     | 一次性確認            | High (Docker)    | 權限摘要顯示              |
| High       | Network + Credential、File 全存取 | 完整審核 + 测试報告   | Strict + Proxy   | 每次關鍵動作需確認        |

## 4. 與現有 OpenClaw 安全機制的整合

- 完全相容目前 **Gateway Sandbox**（non-main sessions 使用 Docker）。
- 延續 **dmPolicy**、**pairing code**、**channel allowlist** 等機制。
- Skill 權限會與 Agent 的 `tools` allow/deny list 合併檢查。
- 支援 `openclaw doctor` 擴展檢查 AutoSkills 安全狀態。

## 5. 已知風險與緩解（Threat Model）

- **惡意 Skill 從 ClawHub**：Manifest 審核 + Pre-install Scan + Sandbox。
- **Prompt Injection 導致權限升級**：Runtime Sandbox 限制 + 靜態分析。
- **Supply Chain Attack**：未來加入 Skill Signing + Trusted Author List。
- **Sandbox Bypass**：定期參考 Snyk 等外部研究，強化 Docker / Kernel 層隔離（例如 KnoxClaw-like 策略）。
- **User Fatigue**：提供清晰的權限摘要 UI、預設保守策略、自動建議。

---

這個安全框架直接解決目前 OpenClaw 社群最常討論的痛點（技能全權限、sandbox 不夠嚴格、手動審核疲勞），並為 AutoSkills 的「自動發現、動態生成、自動演化」提供堅實防護。

**下一步建議**：
- 是否需要我補充 **manifest.json 完整 JSON Schema**？
- 還是產出 **Pre-install Scanner** 的具體實現細節（靜態分析規則）？
- 或針對 **Windows GUI Skill** 的專屬安全 proxy 機制再細寫一份？

告訴我你想重點強化哪一部分，我可以立即調整或展開。這個設計已經可以直接實作在 2026 Q2 的 AutoSkills Phase 中。
