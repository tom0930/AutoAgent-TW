# Phase 160: OpenCLI Integration Evaluation & Architecture (v2.1)

## 1. 意圖與背景 (Intent & Background)
AutoAgent-TW 目前的 RVA (Robotic Visual Automation) 引擎依賴 `pywinauto` 控制 Win32/UIA 介面，並以 Open Interpreter (Vision) 作為後備。
然而，針對 **Electron Apps** (如 Cursor、Notion、Antigravity 自身) 與 **Web 應用**，UIA 經常面臨結構樹渲染不完整或跨平台兼容性差的問題。
`jackwener/opencli` 提供了一種「降維打擊」的解決方案：它透過 CDP (Chrome DevTools Protocol) 直接掛載到使用者現有且已登入的 Chrome 瀏覽器或 Electron App 上，免去了傳統 Playwright/Puppeteer 需要處理登入狀態、無頭模式 (Headless) 驗證碼等痛點。

**對 AutoAgent-TW 的幫助（ROI 評估）**：
- **極大 (High Impact)**：對於 Web 抓取、社群媒體互動（如抓取 PR、Issue、查詢文件）將實現 0 Token 成本與 100% 決定性 (Deterministic)。
- **架構升級 (Architecture)**：可作為 RVA 引擎的 **Eye-2 (Web/CDP Layer)**，補足 UIA 與 Vision 之間的空缺。

## 2. 邊界定義與約束 (Boundaries & Constraints)
- **環境依賴**: 必須引入 Node.js (>= 21) 環境與 npm 全域套件 `@jackwener/opencli`。
- **使用者操作**: 必須在開發者的 Chrome 中手動安裝「Browser Bridge」擴充功能。
- **DoD**: 決定是否將 OpenCLI 整合進 AutoAgent-TW 的 `mcp-router` 或是建立獨立的 `opencli-skill`。

## 3. 架構選型與 Trade-off (Architecture & Trade-offs)
- **方案 A (作為獨立 Tool/Skill)**:
  - 封裝為 `opencli-bridge` Skill，當 AI 需要網頁操作時才調用 `opencli browser xxx`。
  - *優點*：解耦，不影響現有 RVA 核心。
- **方案 B (深度整合入 RVA 引擎) [建議]**:
  - 將 OpenCLI 作為 RVA 的第三引擎 (`RVA.Eye-2-CDP`)。當判斷目標為 Web 或 Electron App 時，優先路由給 OpenCLI，失敗再退回 Vision。
  - *優點*：速度最快，精準度最高（可直接擷取 DOM State 而非影像辨識）。

## 4. 資安威脅建模 (STRIDE Analysis)
這項整合會帶來巨大的資安考驗（Security Boundary Shift）：
| Threat | Vector | Mitigation Strategy |
| :--- | :--- | :--- |
| **Information Disclosure** | 惡意 Prompt 指示 AI 透過 `opencli` 提取使用者的登入 Cookie 或銀行頁面內容。 | 在 AutoAgent-TW 端實施**嚴格白名單 (Whitelist)**。僅允許 `opencli` 操作特定的開發相關網域 (如 github.com, stackoverflow.com)。 |
| **Elevation of Privilege** | `opencli browser eval` 被注入惡意 JavaScript (XSS)。 | 禁用或攔截 AI 嘗試執行 `eval` 的工具調用，強制使用高階原語 (`click`, `extract`, `state`) 或已編譯好的 Adapters。 |
| **Denial of Service** | Daemon Port (19825) 被本地其他惡意進程占用或調用。 | 開放 `OPENCLI_DAEMON_PORT` 環境變數動態綁定，並限制 localhost access。 |

## 5. 編排策略 (Orchestration)
- 若決定整合，後續 Phase 160 實作將會拆分為：
  1. Node.js 環境依賴檢查器 (Installer Update)。
  2. RVA 引擎層面的 CDP 路由擴充。
  3. 安全白名單防護層 (Context Guard) 升級。
