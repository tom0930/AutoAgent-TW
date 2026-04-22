# Research Report: AutoCLI (nashsu/AutoCLI) Integration Analysis

## 1. 方案可行性分析 (Feasibility Study)
- **核心技術**: AutoCLI 基於 Rust 實現，透過 Chrome DevTools Protocol (CDP) 與瀏覽器通訊。
- **優勢**:
    - **Single Binary**: 不需要 Node.js/Python 運行環境。
    - **Session Persistence**: 支援 `--profile` 參數直接掛載現有瀏覽器 Session，免除 2FA/登入困擾。
    - **Speed**: Rust 的高效能使得冷啟動幾乎感測不到 (<50ms)。
    - **Token Efficiency**: 內建 Adapter 機制，回傳的是經過過濾的結構化 JSON，而非整頁 HTML，對 LLM 極其友善。

## 2. 依賴與環境檢查 (Dependencies)
- **Binary**: `autocli.exe` (需放入 `bin/` 並加入 PATH)。
- **Runtime**: 需要本機安裝 Google Chrome 或 Microsoft Edge。
- **Connectivity**: 需要 CDP (9222 port) 訪問權限，或由 AutoCLI 自行啟動瀏覽器實體。

## 3. 已識別的陷阱與風險 (Pitfalls & Risks)
- **CDP Conflict**: 如果已有其他工具（如 Playwright 或 Chrome 偵錯工具）佔用 CDP 埠位，可能會導致啟動失敗。
- **Adapter Update**: 網站 UI 變更可能導致舊的 Adapter 失效，需要具備 AI 自動修復 Adapter 的機制（AutoCLI 已具備此潛力）。
- **Security Boundary**: AutoCLI 可以讀取已登入的 Session，若 AI 被誘導抓取敏感頁面（如 AWS Console），存在資安風險。

## 4. 實施方案路徑 (Implementation Path)
1. **Infrastructure**: 下載 Rust Binary 並完成環境變數配置。
2. **Skill Interface**: 實作 `openclaw/skills/autocli/SKILL.md`，定義 `fetch`, `interact` 指令。
3. **Defense**: 在 `aa-tw` 的 `mcp-router` 層級實施網域攔截，保護敏感資訊。
4. **Validation**: 執行 `tests/autocli.md` 驗證矩陣。
