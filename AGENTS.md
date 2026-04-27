# AGENTS.md — AutoAgent-TW Agent Work Protocol v1.0

> **格式**: [AGENTS.md Open Standard](https://agents.md/) (Linux Foundation AAIF)
> **最後更新**: 2026-04-27
> **維護者**: Tom (Senior Architect)

---

## 架構原則

- **分層架構**: Types → Config → Core → Harness → Scripts → Skills
- 每一層只能往「下方」依賴，**不可反向 import**
- 詳見 [ARCHITECTURE.md](ARCHITECTURE.md)

## 禁止事項

> [!CAUTION]
> 以下行為將觸發 Preflight Gate 攔截，無論提交者是誰。

1. **不可刪除或重建 infrastructure** — 修復而非重建 (repair, not reset)
2. **不可直接修改 `.env` / `SECURITY.md`** — 必須經過 critical-tier 審查
3. **不可新增未經審批的外部依賴** — 所有 pip install 必須記錄在 `requirements.txt`
4. **不可在 `src/core/` 中 import `scripts/` 或 `_agents/`** — 禁止反向依賴
5. **不可繞過 `aa-ship` 直接 push** — 所有代碼變更必須經過 Preflight Gate
6. **不可在 commit 中包含 API Key / Token / 密碼** — 自動掃描攔截
7. **不可修改 `risk-tiers.json` 或 `AGENTS.md` 而不經 critical-tier review**

## 風險分級

- 風險等級定義見 [risk-tiers.json](risk-tiers.json)
- **critical** 路徑變更需要多人簽核 + staging 驗證 + rollback plan
- **high** 路徑變更需要至少 1 人 review + 完整測試
- **medium** 路徑變更需要 lint + type check
- **low** 路徑變更 (docs/tests) 可快速通過

## 測試要求

- 所有 `src/core/` 變更必須通過 `py_compile` 驗證
- 所有 `scripts/` 變更必須通過 lint 檢查
- 覆蓋率不可低於現有水平 (ratchet principle)
- 測試指南見 [tests/](tests/)

## 程式碼風格

- Python: PEP 8 + Type Hints (PEP 484)
- Git Commit: [Conventional Commits](https://www.conventionalcommits.org/) 格式
- Scope: `gateway`, `session`, `skill`, `vision`, `mcp`, `cron`, `security`, `harness`

## GSD 工作流程

- 所有功能開發必須遵循 5 階段: **Discuss → Plan → Execute → QA → Ship**
- 不允許跳步，每階段必須有對應文件產出
- 詳見 [_agents/workflows/](/_agents/workflows/)

## 記憶體與資源限制

- 工作集記憶體 < 250MB (Stealth Mode 要求)
- 不可啟動常駐 Daemon 而不提供關閉機制
- 所有 background process 必須有 TTL 或 reaper 機制

---

## ❌ 禁止寫法（反面示例）

> 以下錯誤寫法將觸發 Preflight Gate 攔截，請勿嘗試。

### 危險操作

```python
# ❌ 錯誤：禁止刪除整個目錄
import shutil
shutil.rmtree('/')  # 絕對禁止！

# ✅ 正確：只刪除當前專案的 temp 目錄
import shutil
import Path
temp_dir = Path(__file__).parent.parent / 'temp'
if temp_dir.exists():
    shutil.rmtree(temp_dir)
```

```python
# ❌ 錯誤：禁止刪除資料庫所有表
cursor.execute("DROP TABLE IF EXISTS *")

# ✅ 正確：使用 migration 脚本，只刪除特定表
from alembic import command
command.downgrade(revision, '-1')  # 回滾上一個 migration
```

### 架構違規

```python
# ❌ 錯誤：src/core/ 不可直接 import scripts/
# src/core/harness_gateway.py
from scripts.preflight_gate import run_check  # 禁止反向依賴！

# ✅ 正確：通過 Bridge API 調用
from src.bridge.script_runner import run_script
```

```typescript
// ❌ 錯誤：禁止繞過 permission_engine
// openclaw/src/agents/bash-tools.ts
if (user.isAdmin) {
  exec('rm -rf /');  // 危險！繞過了 gatekeeper
}

// ✅ 正確：所有操作必須經過 permission_engine
const result = await permission_engine.check(user, 'bash:exec', { cmd: 'rm' });
if (result.allowed) {
  await bash_execute(params);
}
```

### 配置違規

```bash
# ❌ 錯誤：禁止直接修改 .env
# .env
DATABASE_PASSWORD=secret123  # 禁止直接寫入！

# ✅ 正確：使用 aa config set
# Terminal
aa config set DATABASE_PASSWORD --value="secret123"  # 通過安全 API
```

---

## 📍 路徑限定規則 (Path-specific Rules)

> 不同路徑有不同的規則約束，請根據修改的檔案位置對號入座。

### `src/core/**/*.py` — 最高風險

- 禁止使用 `eval()`, `exec()`
- 禁止直接操作檔案系統（必須通過安全 API）
- 必須有完整的類型註解 (PEP 484)
- 禁止網路請求（只能通過 `src.bridge.network`）

### `scripts/**/*.py` — 中高風險

- 禁止訪問 `.env` 中的 secrets（使用 `os.getenv` + 白名單）
- 所有外部 API 調用必須通過 `agent_gateway`
- 禁止執行 `subprocess` 調用系統命令（使用 `aa-cli` 包裝）

### `openclaw/src/agents/**` — TypeScript 約束

- 禁止繞過 `permission_engine`
- 所有工具調用必須經過 `gatekeeper`
- 禁止在工具中直接 `process.exit()`
- 新增工具必須同時新增測試

### `tests/**/*.py` / `tests/**/*.ts` — 測試約束

- 禁止依賴真實 API（使用 mock）
- 禁止 `time.sleep()` 等待（使用 mock time）
- 每個測試必須有 `teardown` 清理

---

## 💡 核心決策原因

> 了解「為什麼」比知道「怎麼做」更重要，這些規則背後都有真實的代價。

| 規則 | 原因 | 代價 |
|------|------|------|
| 禁止刪除 infrastructure | 重建需要重新配置所有連接，無法追蹤歷史狀態 | 平均 4 小時恢復，期間服務中斷 |
| 禁止直接修改 .env | 可能包含生產環境凭證，直接修改導致配置飄移 | 曾有案例導致 2 小時生產事故 |
| 禁止反向依賴 core→scripts | 破壞分層架構，導致循環依賴 | 代碼難以測試和維護 |
| 禁止繞過 aa-ship | 繞過審查導致危險變更進入主分支 | 可能中斷 CI 或影響生產 |
| 覆蓋率 ratchet | 防止技術債務累積 | 不約束會導致測試逐漸被遺忘 |

---

## 📋 常見任務 SOP

> 當使用者說「幫我...」時，按照以下步驟執行。

### 「幫我新增一個 MCP Server」

1. 在 `src/mcp/` 底下建立 `mcp_xxx.py`
2. 在 `src/mcp/hub.py` 的 `init_map` 中註冊
3. 在 `tests/mcp/` 建立對應測試
4. 更新 `docs/mcp/registry.md`
5. **驗證**: 運行 `python scripts/preflight_gate.py --check`

### 「幫我修改 permission_engine」

1. 先看 `src/core/permission_engine.py` 的現有邏輯
2. 執行風險評估：`python scripts/preflight_gate.py --files src/core/permission_engine.py`
3. 如果是 critical tier，先諮詢 human
4. 修改後運行 `python -m py_compile src/core/permission_engine.py`
5. **驗證**: `python scripts/preflight_gate.py --check`

### 「幫我在 openclaw/src/agents/ 新增工具」

1. 檢查是否需要 `permission_engine` 等級（查看 `permission_engine.py` 的 `ToolRiskLevel`）
2. 在對應的 `agent-tools.ts` 中註冊
3. 建立對應的 `xxx.test.ts`
4. **驗證**: 運行 `pnpm test:channels`

### 「幫我解決一個 bug」

1. 先重現 bug（建立最小測試案例）
2. 定位問題（使用 `git bisect` 或二分法）
3. 修復（遵守「修復而非重建」原則）
4. 添加迴歸測試
5. **驗證**: 所有測試通過

---

## 🧹 Claude Cowork 每週排毒

> 為防止 AI 設定隨時間走鐘，每週自動維護。

### 排毒任務清單

每週一 09:00 自動執行（或手動觸發 `python scripts/cowork_maintenance.py`）：

- [ ] 檢查 `AGENTS.md` 與 `CLAUDE.md` 是否同步
- [ ] 驗證 `risk-tiers.json` paths 是否與實際架構一致
- [ ] 清理 30 天以上未更新的 temp 文件
- [ ] 產生「健康報告」並更新 `health-metrics.json`
- [ ] 檢查是否有孤兒 process（`scripts/agent_reaper.py --check`）

### 排毒腳本

```bash
# 手動觸發排毒
python scripts/cowork_maintenance.py

# 只檢查不同步問題
python scripts/cowork_maintenance.py --check-only

# 產生健康報告
python scripts/cowork_maintenance.py --report
```

---

**📝 更新記錄**

| 日期 | 更新內容 | 作者 |
|------|----------|------|
| 2026-04-27 | 新增反面示例、路徑限定規則、決策原因、常見任務SOP、排毒機制 | ai代可行 |
