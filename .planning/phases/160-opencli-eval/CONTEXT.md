# Phase 160: AutoCLI Integration Evaluation & Architecture (v2.2)

## 1. 意圖與背景 (Intent & Background)
AutoAgent-TW 目前的 RVA (Robotic Visual Automation) 引擎依賴 `pywinauto` 控制 Win32/UIA 介面，並以 Open Interpreter (Vision) 作為後備。
然而，針對 **Electron Apps** (如 Cursor、Notion、Antigravity 自身) 與 **Web 應用**，UIA 經常面臨結構樹渲染不完整或跨平台兼容性差的問題。

原本評估 `jackwener/opencli` 作為解決方案，但最新調研發現其繼任者 **`nashsu/AutoCLI`** 帶來了飛躍性的提升。
`nashsu/AutoCLI` 是以 **Rust** 重寫的單一執行檔（~4.7MB），免除了繁重的 Node.js 依賴，效能提升 12 倍，記憶體使用減少 10 倍，且內建對 AI Agent (如 Claude Code) 的深度支援，並具備強大的 AI Adapter 生態系 (autocli.ai)。它同樣能透過現有瀏覽器 Session 直接抓取資料，實現「降維打擊」。

**對 AutoAgent-TW 的幫助（ROI 評估）**：
- **極大 (High Impact)**：支援 55+ 平台 (GitHub, Twitter, Reddit 等)，實現 0 Token 成本與 100% 決定性的結構化資料抓取。
- **架構升級 (Architecture)**：作為 RVA 引擎的 **Eye-2 (Web/CDP/Adapter Layer)**。
- **輕量化 (Lightweight)**：無須額外安裝 Node.js 或龐大的 `node_modules`，完美契合 AutoAgent-TW "Stealth Mode" (低記憶體消耗) 的設計理念。

## 2. 邊界定義與約束 (Boundaries & Constraints)
- **環境依賴**: 下載單一 Rust Binary 即可 (Zero runtime dependencies)。
- **生態系整合**: 結合 `nashsu/autocli-skill`，無縫橋接至 AutoAgent-TW 的 `mcp-router`。
- **DoD**: 驗證 AutoCLI 抓取 GitHub PR/Issue 的速度與資源消耗，並整合至 `aa-tw` 的 Agent 系統。

## 3. 架構選型與 Trade-off (Architecture & Trade-offs)
- **方案 A (使用傳統 opencli / Node.js)**:
  - *缺點*：環境沉重，啟動慢，違背剛完成的記憶體優化 (Phase 158.5)。
- **方案 B (整合 nashsu/AutoCLI) [強烈建議]**:
  - *優點*：純 Rust 執行檔，極速且省記憶體；具備 AI 自動產生 Adapter 的能力；直接複用瀏覽器 Session。
  - *作法*：撰寫一個 `autocli-skill`，透過 Shell Command 直接呼叫 `autocli`，將結果 (JSON) 返回給 AI。

## 4. 資安威脅建模 (STRIDE Analysis)
這項整合會帶來巨大的資安考驗（Security Boundary Shift）：
| Threat | Vector | Mitigation Strategy |
| :--- | :--- | :--- |
| **Information Disclosure** | 惡意 Prompt 指示 AI 透過 `autocli` 提取使用者的登入 Cookie 或銀行頁面內容。 | 在 AutoAgent-TW 端實施**嚴格白名單 (Whitelist)**。僅允許安裝/執行特定網域的 Adapters (如 github.com, stackoverflow.com)。 |
| **Elevation of Privilege** | 第三方 Adapter 包含惡意請求。 | 僅信任官方來源 (autocli.ai) 的 Adapters，或在受限的 Sandbox 內執行。 |
| **Spoofing** | 本地 API 端點被偽造。 | 強制驗證 AutoCLI 的本地執行憑證，不開放對外 port。 |

## 5. 編排策略 (Orchestration)
- 後續 Phase 160 實作將會拆分為：
  1. AutoCLI Rust Binary 的自動下載與環境配置。
  2. 開發 `autocli-skill` 作為 AI 調用介面。
  3. 安全白名單防護層 (Context Guard) 升級，阻擋非開發用途的網域抓取。
  4. 執行 POC 測試矩陣 (定義於 `tests/autocli.md`) 進行效能與沙箱驗證。

## 6. 測試與驗證策略 (Verification Plan)
為了確保 AutoCLI 符合我們在 Stealth Mode (Phase 158.5) 中立下的嚴格標準，已於 `tests/autocli.md` 制定測試矩陣。核心驗收標準包含：
- **效能指標**：冷啟動時間 < 100ms，執行期 RAM 波動 < 50MB。
- **資料指標**：成功掛載 Browser Session 並無頭獲取目標網站 (如 GitHub PR) 的純淨 JSON。
- **資安指標**：有效攔截對非開發相關網域 (如 banking) 的爬取行為，確保沙箱邊界完整。
