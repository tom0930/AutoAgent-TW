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
