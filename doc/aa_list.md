# list install of extensions

Listed directory autoagent-TW
Listed directory .planning
Viewed STATE.md:1-39
Viewed SECURITY.md:1-29

### Phase 1: Discuss (意圖澄清與邊界定義)

從我 20 年的系統架構經驗來看，當開發者要求「list install of extensions」時，通常涉及三個層次的環境審查：

1. **IDE 層級 (VS Code Extensions)**：影響開發體驗與輔助工具。
2. **Agent 層級 (MCP Servers)**：影響 AI Agent 的工具調用能力與知識邊界。
3. **專案層級 (Internal Agent Skills/Extensions)**：位於 `_agents` 或 `.agents` 目錄下的自定義擴展。

**我的假設與風險預判：**

* **假設**：您希望確認當前 `AutoAgent-TW` 環境的完整版圖，以利於進行 M34 (Industrial Tooling) 的整合基準。
* **風險**：部分延伸插件可能存在版本衝突或冗餘（Redundant processes），需一併診斷。

---

### Phase 2: Plan (執行計畫)

#### 8 維度檢查 (8-Dimension Audit)

| 維度                     | 說明                                                                       |
| :----------------------- | :------------------------------------------------------------------------- |
| **1. 需求拆解**    | 整合 IDE 插件、MCP 工具鏈與內部 Agent Skills 列表。                        |
| **2. 技術選型**    | 使用 `code --list-extensions` + 遍歷 `.planning` 與 `_agents` 設定。 |
| **3. 系統架構**    | 透過 `Inventory Agent` 角色進行跨目錄掃描。                              |
| **4. 效能設計**    | 並行執行 CLI 指令與檔案掃描，確保零延遲。                                  |
| **5. 資安設計**    | **STRIDE**: 防止資訊洩漏，過濾敏感插件的路徑資訊。                   |
| **6. AI 產品考量** | 提供清楚的分類清單，區分「核心」與「選配」工具。                           |
| **7. 錯誤處理**    | 若 `code` 指令不在 PATH，自動退回靜態路徑掃描。                          |
| **8. 測試策略**    | 驗證清單完整性，比對 `package.json` 的依賴項。                           |

#### 執行步驟 (Task List):

1. [ ] **Scan IDE**: 執行 `code --list-extensions` 獲取原生插件清單。
2. [ ] **Scan MCP**: 讀取 `.planning/config.json` 與作業系統預設 MCP 路徑。
3. [ ] **Scan Internal**: 遍歷 `_agents` 與 `skills` 目錄。
4. [ ] **Consolidate**: 產出 `INVENTORY.md` 虛擬文件供用戶檢閱。

---

### Phase 3: Execute (執行中)

正在調用 [run_command] 與 [list_dir]...

Ran command: `code --list-extensions`
Viewed config.json:1-16
Listed directory workflows
Listed directory skills
Listed directory skills
Viewed package.json:1-15

### Phase 4: Ship (交付報告)

根據您的要求，我已對當前開發環境進行了深度掃描。身為架構師，我將這些擴展分為 **IDE 環境**、**MCP 工具核心**、**全域 AI 技能庫** 以及 **內部工作流** 四個維度進行呈現。

這是目前的系統擴展總表 (Inventory Report)：

#### 1. IDE 擴展 (VS Code Extensions)

當前 IDE 裝載了強大的 AI 輔助與工業開發工具鏈：

* **核心 AI 代理**: `anthropic.claude-code`, `rooveterinaryinc.roo-cline`, `saoudrizwan.claude-dev`, `google.geminicodeassist`
* **工業開發**: `ms-vscode.cpptools-extension-pack` (C/C++), `ms-vscode.cmake-tools`, `vadimcn.vscode-lldb`
* **輔助工具**: `eamodio.gitlens`, `formulahendry.code-runner`, `streetsidesoftware.code-spell-checker`, `mechatroner.rainbow-csv`
* **特規工具**: `unchase.antigravity-storage-manager` (Antigravity 專屬儲存管理)

#### 2. 全域 AI 技能庫 (Antigravity Global Skills)

位於 `C:\Users\TOM\.gemini\antigravity\skills`，共計 **171** 項工業級技能。關鍵技能包括：

* **自動化建構**: `aa-auto-build`, `claw-auto-build`
* **安全與審計**: `aa-guard`, `security-auditor`, `vulnerability-scanner`
* **財務自動化**: `invoice-automation`, `jpg2excel`, `test_invoice`
* **架構設計**: `architecture-patterns`, `senior-architect`, `event-sourcing-architect`
* **特定工具**: `nlm-skill` (NotebookLM), `vivado-rva` (即將整合)

#### 3. 內部 Agent 工作流 (_agents/workflows)

這是 `AutoAgent-TW` 的核心大腦邏輯：

* **核心循環**: `aa-discuss2.md`, `aa-plan.md`, `aa-execute.md`, `aa-qa.md`, `aa-ship.md`
* **自癒機制**: `aa-fix.md`, `aa-resume.md`
* **歷史記憶**: `aa-memory.md`, `aa-history.md`
* **工業特化**: `aa-fw-debug.md` (韌體除錯), `aa-testclaw.md`

#### 4. 當前環境狀態 (System Context)

* **專案版本**: v3.3.0 (Phase 158)
* **運行模式**: Multi-Agent Orchestration (Sub-Agent Mode)
* **核心引擎**: UIA-First Industrial Controller (支援雙眼感知)
* **下一步目標**: Phase 159 (Vivado/Vitis RVA Upgrade)

---

### 架構師建議 (Architect's Insights)

1. **冗餘清理**: 偵測到同時安裝了 `Claude Dev` 與 `Roo-Cline`，建議統一使用其中之一以避免工具衝突與 MCP 資源競爭。
2. **性能優化**: 由於全域技能高達 171 項，建議定期執行 `/aa-guard` 進行權限審查與環境快取清理。
3. **M34 整備**: 當前 C++ 插件鏈已就緒，可直接推進 M34 的 FPGA Tooling 整合。

**需要我針對特定類別（如 MCP Config 或 Python Packages）進行更深度的依賴掃描嗎？**

---

**Git Conventional Commit:**
`docs: inventory current extensions and system state for M34 readiness`






---




### Phase 1: Discuss (意圖確認)

您直接指令 `code --list-extensions`。從系統架構維護的角度來看，這通常是為了確切取得 IDE 插件的 **全名 (Extension ID)**，以便進行腳本化配置或環境同步。

### Phase 2: Plan (執行計畫)

1. **執行**：在當前 PowerShell 環境中呼叫 `code --list-extensions`。
2. **輸出**：將結果以原始清單呈現，並標註具備 MCP 支援的核心插件。

---

### Phase 3: Execute (執行中)

正在調用 [run_command]...

Ran command: `code --list-extensions`

### Phase 4: Ship (交付報告)

以下是當前系統中安裝的 **VS Code 插件完整 ID 清單**。這份清單已確認涵蓋了 AI 協作、工業開發以及 Antigravity 專用的存儲管理組件。

| Extension ID                               | Category            | Description / Note                           |
| :----------------------------------------- | :------------------ | :------------------------------------------- |
| `anthropic.claude-code`                  | **AI Core**   | Claude Native Bridge                         |
| `saoudrizwan.claude-dev`                 | **AI Core**   | Claude Dev (Prev. Roo-Cline)                 |
| `rooveterinaryinc.roo-cline`             | **AI Core**   | Roo-Cline Fork                               |
| `google.geminicodeassist`                | **AI Core**   | Gemini Code Assist                           |
| `continue.continue`                      | **AI Core**   | Open source AI coding assistant              |
| `github.copilot-chat`                    | **AI Core**   | GitHub Copilot Chat                          |
| `codeium.codeium`                        | **AI Core**   | Codeium AI                                   |
| `unchase.antigravity-storage-manager`    | **System**    | **Antigravity 專屬組件**               |
| `ms-vscode.cpptools-extension-pack`      | **Dev (C++)** | C/C++ IntelliSense, debugging, and browsing. |
| `ms-vscode.cmake-tools`                  | **Dev (C++)** | CMake support                                |
| `vadimcn.vscode-lldb`                    | **Dev (C++)** | Native debugger                              |
| `eamodio.gitlens`                        | **VCS**       | Git supercharged                             |
| `ms-azuretools.vscode-azure-mcp-server`  | **MCP**       | Azure MCP Server integration                 |
| `ms-windows-ai-studio.windows-ai-studio` | **System**    | Windows AI Studio                            |

**完整原始清單 (Raw List):**

```text
alefragnani.bookmarks
anthropic.claude-code
codeium.codeium
continue.continue
eamodio.gitlens
fernandoescolar.vscode-solution-explorer
formulahendry.code-runner
github.copilot-chat
google.geminicodeassist
kilocode.kilo-code
marscode.marscode-extension
mechatroner.rainbow-csv
ms-azuretools.vscode-azure-github-copilot
ms-azuretools.vscode-azure-mcp-server
ms-azuretools.vscode-azureresourcegroups
ms-vscode.cmake-tools
ms-vscode.cpp-devtools
ms-vscode.cpptools
ms-vscode.cpptools-extension-pack
ms-vscode.cpptools-themes
ms-vscode.vscode-typescript-tslint-plugin
ms-windows-ai-studio.windows-ai-studio
readbysearch.code2pdf
rooveterinaryinc.roo-cline
saoudrizwan.claude-dev
slevesque.shader
stevensona.shader-toy
streetsidesoftware.code-spell-checker
teamsdevapp.vscode-ai-foundry
twxs.cmake
unchase.antigravity-storage-manager
vadimcn.vscode-lldb
```

我們目前環境中存在多個競爭性的 AI 插件（Claude-Dev, Roo-Cline, Continue, Copilot, Gemini）。如果您需要針對特定的插件進行 MCP 伺服器掛載或衝突排查，請告訴我。

---

**Git Conventional Commit:**
`info: listed raw vscode extensions for environment audit`
