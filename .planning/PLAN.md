# Plan: Install Karpathy Skills into AutoAgent-TW

## 1. 需求拆解與邊界定義
| 項目 | 描述 |
| :--- | :--- |
| **目標** | 將 `https://github.com/forrestchang/andrej-karpathy-skills` 中的技能整合至 `AutoAgent-TW`。 |
| **範疇** | 複製 `skills/karpathy-guidelines` 資料夾；整合 `CLAUDE.md` 行為準則；更新技能註冊。 |
| **非範疇** | 修改核心 Agent 引擎邏輯。 |

## 2. 技術選型與理由
| 技術 | 理由 |
| :--- | :--- |
| **Git Clone** | 標準且高效的遠端倉庫獲取方式。 |
| **Skill Engine** | 沿用現有 `src/core/skill/engine.py` 以確保相容性。 |
| **Path** | 安裝至 `.agents/skills/`，符合系統進階技能目錄規範。 |

## 3. 系統架構圖 (Mermaid)
```mermaid
graph TD
    Repo["GitHub Repo (Karpathy Skills)"] -->|Clone| TempDir["Temp Directory"]
    TempDir -->|Extract| KarpathySkill["karpathy-guidelines/SKILL.md"]
    KarpathySkill -->|Move| AgentSkills[".agents/skills/"]
    TempDir -->|Merge| ClaudeConfig["CLAUDE.md / AGENTS.md"]
```

## 4. 並行與效能設計
- **Wave 1**: 建立臨時目錄並執行 `git clone`。
- **Wave 2**: 檔案搬移與路徑驗證。
- **Wave 3**: 註冊表更新與最終清理。

## 5. 資安設計與威脅建模 (STRIDE)
| 威脅 | 對策 |
| :--- | :--- |
| **Spoofing** | 驗證來源 URL 為 `forrestchang/andrej-karpathy-skills`。 |
| **Tampering** | 檢查下載的檔案是否包含惡意腳本或隱藏指令。 |
| **Info Disclosure** | 確保 `.env` 等敏感檔案不被 accidental indexing。 |

## 6. AI 產品相關考量
- **UX**: 技能安裝後應能立即透過 `aa_useguide.md` 調用。
- **Consistency**: 保持 Karpathy 準則與現有 `AGENTS.md` 邏輯的一致性。

## 7. 錯誤處理、監控與恢復策略
- 若 Clone 失敗，自動重試。
- 若路徑衝突，備份原有技能。

## 8. 測試策略
- **Unit Test**: 執行 `python scripts/doctor.py --status`。
- **Integration Test**: 驗證 `karpathy-guidelines` 的觸發邏輯。

---

## 任務清單 (Task List)
- [X] Wave 1: 建立臨時目錄並 Clone 倉庫
- [X] Wave 2: 提取 `karpathy-guidelines` 並搬移至 `.agents/skills/`
- [X] Wave 3: 整合 `CLAUDE.md` 內容至 `AutoAgent-TW` 核心配置 (於 `docs/karpathy/` 歸檔並同步準則)
- [X] Wave 4: 執行系統診斷與驗證
