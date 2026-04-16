# CONTEXT: Antigravity Awesome Skills 優化 — Bundle 精簡 + AutoSkills Bridge

**Phase**: AutoSkills Optimization  
**Date**: 2026-04-14  
**Status**: DISCUSSED → READY FOR PLAN  
**Author**: Tom (AA-Consultant)

---

## 1. 問題定義 (Problem Statement)

### 1.1 現況
- 安裝了 `antigravity-awesome-skills` 後，`skills/` 目錄從 **126 → 1505** 個子目錄。
- Antigravity 在每次對話啟動時，會掃描所有 `skills/*/SKILL.md` 的 **name + description**，注入 system prompt。
- 1505 個 skill 的摘要（每個約 50-100 tokens）= **~75,000-150,000 tokens** 僅用於技能清單。
- 已觀察到的症狀：
  - Context window 嚴重擠壓，留給實際對話的空間大幅減少。
  - 技能清單過長導致 Agent 在選擇技能時產生「決策疲勞」。
  - 官方文件 `agent-overload-recovery.md` 明確警告「千萬不要全部 concat 進 system prompt」。

### 1.2 目標 (DoD - Definition of Done)
1. **立即止血**：將活躍 skills 數量從 1505 降至 **可控範圍（≤ 100-150）**。
2. **長期架構**：建立 AutoSkills Bridge，實現 **intent-based on-demand loading**。
3. **零知識損失**：所有 1400+ skills 保持可用，只是不預載入 system prompt。
4. **透明性**：每次動態載入 skill 時，向使用者明確提示。

---

## 2. 研究結論 (Research Findings)

### 2.1 官方推薦方案分析

| 方案 | 機制 | 優點 | 缺點 | 適用性 |
|------|------|------|------|--------|
| **Bundle Activation** (`activate-skills.bat`) | 僅暴露選定 bundle 的 skills 到 `skills/`，其他存入 `skills_library/` | 官方支援、立即可用 | 手動切換、無法跨 bundle 混搭 | ✅ **立即止血首選** |
| **Progressive Disclosure** | 啟動時只讀 index，按需讀 SKILL.md | 最優 token 效率 | 需修改 Antigravity 內部 loader | ❌ 需改核心代碼 |
| **AutoSkills Bridge** (我們的方案) | 註冊單一 bridge skill，internal semantic search + on-demand load | 最智慧、完全自動化 | 需要開發 bridge + index | ✅ **長期最佳** |

### 2.2 Bundle 生態分析 (來自 bundles.md)

官方定義了 **37 個 bundles**，每個 5-8 個 skills。根據 Tom 的實際工作流分析：

| Bundle | Skills 數 | 與 Tom 工作相關度 |
|--------|-----------|------------------|
| Essentials | 5 | ⭐⭐⭐⭐⭐ 必裝 |
| Agent Architect | 6 | ⭐⭐⭐⭐⭐ AI 相關 |
| Python Pro | 7 | ⭐⭐⭐⭐⭐ 主力語言 |
| Security Engineer | 7 | ⭐⭐⭐⭐⭐ 資安核心 |
| Full-Stack Developer | 6 | ⭐⭐⭐⭐ |
| DevOps & Cloud | 7 | ⭐⭐⭐⭐ |
| QA & Testing | 7 | ⭐⭐⭐ |
| Documents & Presentations | 7 | ⭐⭐⭐ 發票處理 |
| Architecture & Design | 5 | ⭐⭐⭐ |
| Systems Programming | 5 | ⭐⭐⭐ C++ |
| LLM Application Developer | 5 | ⭐⭐⭐ |
| Automation Builder | 7 | ⭐⭐ |

### 2.3 已有的 AutoSkills 基礎設施

從 MemPalace 檢索得知：
- `src/agents/skills-clawhub.ts` — ClawHub 搜尋/安裝 API 已實作。
- `scripts/auto_skills_server.py` — FastMCP 伺服器骨架已存在（含 search/install/generate）。
- `.planningClaw/STATE.md` — AutoSkills Phase 2 狀態為 `READY TO EXECUTE`。
- `autoskills_load.md` — Bridge Skill 完整規格（manifest.json + bridge.ts）已撰寫。

---

## 3. 決策記錄 (Architecture Decision Records)

### ADR-001: 採用「雙軌策略」— 立即 Bundle 精簡 + 漸進 Bridge 建置

**決策**：不二選一，同時推進兩條路線。

**Rationale**：
- **短期（今天）**：用 `activate-skills.bat --clear` + 手動 bundle 挑選，立刻把 skills/ 從 1505 降到 ~80-100。
- **中期（本週）**：將未激活的 1400+ skills 建立 `skills_index.json` 輕量索引。
- **長期（Q2）**：完整 AutoSkills Bridge 實作，intent-based dynamic loading。

### ADR-002: 保留原始 skills 在 `skills_library/` 而非刪除

**決策**：已安裝的 1505 個 skill 移至 `skills_library/` 做為資料源，`skills/` 僅放活躍 skills。

**Rationale**：
- 備份已在 `skills_backup_20260414/`。
- `skills_library/` 作為 AutoSkills Bridge 的掃描目標。
- 未來 `npx antigravity-awesome-skills` 更新時直接覆蓋 `skills_library/`。

### ADR-003: 自訂 skills 永遠優先於社群 skills

**決策**：`aa-*`, `cc-*`, `claw-*`, `gsd-*`, `invoice-*`, `jpg2*`, `nlm-*` 等自訂 skills 永遠保留在 `skills/` 活躍目錄。

---

## 4. 技術方案 — 兩階段架構

### Phase A: 立即精簡 (Today — 30 分鐘)

```
skills/ (活躍, ~100 個)
├── [自訂 skills: aa-*, cc-*, claw-*, gsd-*, invoice-*, etc.]  (~60)
├── [Essentials bundle]                                         (~5)
├── [Agent Architect bundle]                                    (~6)
├── [Python Pro bundle]                                         (~7)
├── [Security Engineer bundle]                                  (~7)
├── [Documents & Presentations bundle]                          (~7)
├── [Architecture & Design bundle]                              (~5)
└── docs/                                                       (保留)

skills_library/ (完整存檔, 1505 個)
└── [所有 antigravity-awesome-skills 安裝的 skill]
```

**執行方式**：
1. 將 `skills/` 重命名為 `skills_library/`。
2. 建立新的 `skills/` 目錄。
3. 將自訂 skills（非 antigravity 安裝的）複製回 `skills/`。
4. 從 `skills_library/` 中按 bundle 定義複製選定 skills 到 `skills/`。

### Phase B: AutoSkills Bridge (This Week)

建立 `skills/antigravity-awesome-bridge/` skill，包含：
- `manifest.json` — Bridge 配置。
- `SKILL.md` — Agent 指令（永不出現在 command 清單）。
- `bridge.py` 或 `bridge.ts` — Semantic search engine。
- `skills_index.json` — 從 `skills_library/` 自動生成的輕量索引。

---

## 5. 資安威脅建模 (STRIDE Analysis)

| 威脅類型 | 風險描述 | 防禦措施 |
|----------|---------|---------|
| **Spoofing** | 惡意 skill 偽裝為合法 skill | `antigravity-install-manifest.json` 驗證源頭 |
| **Tampering** | Bridge 載入被篡改的 SKILL.md | 讀取時校驗檔案 hash |
| **Information Disclosure** | Skill 內容暴露敏感路徑 | `truncateIfNeeded` 限制注入大小 |
| **Denial of Service** | 載入過多 skills 撐爆 context | Top-5 限制 + 8000 token 上限/skill |
| **Elevation of Privilege** | Skill 指令繞過安全沙箱 | Permission Manifest + Runtime Sandbox (Phase 2) |

---

## 6. 非功能性需求

- **啟動速度**：精簡後 skill 載入 < 2 秒（目前 1505 個可能 > 10 秒）。
- **Context 效率**：活躍 skills 摘要 < 10,000 tokens（從 ~100K+ 降至 ~10K）。
- **可恢復性**：隨時可從 `skills_backup_20260414/` 或 `skills_library/` 恢復。
- **跨平台**：方案必須相容 Windows PowerShell。

---

## 7. 下一步 (Next Steps)

1. **立即執行 Phase A**：精簡 skills 目錄（需用戶確認 bundle 選擇）。
2. **建立 skills_index.json**：從 `skills_library/` 掃描生成。
3. **實作 AutoSkills Bridge**：基於 `autoskills_load.md` 的規格。
4. **更新 MemPalace**：記錄本次決策。

---

**核定日期**: 2026-04-14  
**負責人**: Tom (AA-Consultant + Antigravity Agent)
