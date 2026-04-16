# Phase 144: MCP Router + Token Killer v1.0

## 1. 目標與意圖挖掘 (Goal & Intent)
本階段旨在透過實作統一的 **MCP Router (`mcp-router`)**，將所有外部 MCP 呼叫 (GitKraken、Filesystem、Browser、Code Search 等) 全面導向 RTK (Rust Token Killer) 壓縮層。
這將解決隨著技能與工具使用頻率增加所帶來的巨量上下文冗餘，達到全系統 **80-95% Token 開支節省**。

## 2. 邊界與約束 (Boundaries & Constraints)
* **DoD (Definition of Done)**:
  1. `mcp-router` skill 完整部署包含 `SKILL.md`, `config/`, 與 `scripts/`。
  2. 確保舊有的 `git-token-killer` 等邏輯可被平滑整合或協同運作。
  3. 依據 Agent 所處 Phase (Builder/QA/Guardian)，動態調節壓縮強度。
* **限制**: 必須維持零 Context 污染的設計模式，系統回報需走側向通道 (JSON/Dashboard) 避免回傳過長字串。

## 3. 架構設計與 Trade-offs
### 方案 A: 單純修改系統提示詞 (Prompt Engineering)
* **優點**: 無需開發新組件。
* **缺點**: AI 遵循度不穩定，且消耗大量 Prompt 空間，長期可靠度極低。

### 方案 B: 透明代理器路由 (The MCP Proxy Wrapper - 採用)
* **優點**: LLM 仍呼叫原本的工具邏輯，但在執行底層會被全域攔截。統一了所有的設定與回傳過濾，並可針對特定 Phase (Guardian) 強制解壓縮 (`--raw`) 進行安全掃描。
* **缺點**: 增加 1 層極薄的路由負擔 (約 10ms)。

## 4. 資安威脅建模 (STRIDE)
* **Tampering (竄改)**: 外部輸入可能試圖植入惡意指令。
  * **防禦**: MCP Router 會封裝參數並以白名單機制向 RTK 遞交指令。Guardian Phase 會強制關閉壓縮（`--verbose` / `--raw`）以便於安全雷達的檢測與留痕。
* **Information Disclosure (資訊洩漏)**:
  * **防禦**: RTK 在處理 FPGA/MFC 敏感路徑時，遵循配置檔 `.toml` 的遮蔽邏輯排除敏感字串。

## 5. 編排與執行模式 (Orchestration)
採用 Wave 並行化部署：
- **Wave 1**: 建立統一入口 `SKILL.md` (定義觸發與約定)
- **Wave 2**: 部署 `config/mcp-router.toml` (針對不同專案如 Vivado 的客製化過濾)
- **Wave 3**: 部署核心 `mcp_router.py` (動態調度邏輯)

## 6. 附註
此規劃完全遵循 `temp/mcpkiller.md` 的藍圖定義。
