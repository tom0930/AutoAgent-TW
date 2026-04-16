# Phase 144: MCP Proxy Gateway v1.0 (AutoSkill Optimized)

## 1. 目標與意圖挖掘 (Goal & Intent)
本階段旨在解決早期「CLI Wrapper」繞過 JSON-RPC 導致緩存失效的架構盲點。透過實作 **MCP Proxy Gateway**，將 AutoSkill (動態技能載入) 與 RTK (極致 JSON 壓縮) 深度結合，確保所有原生 `use_mcp_tool` 的底層 API 呼叫都能被透明攔截與瘦身，實現 85-95% Token 節省，無縫支援 10MB 以上之巨型檔案與 log。

## 2. 邊界與約束 (Boundaries & Constraints)
* **DoD (Definition of Done)**:
  1. `mcp-router-gateway.py` 採用 `asyncio` 實作非阻塞式 StdIO 監聽。
  2. 整合 `auto_register.py` 讓 AutoSkill 動態載入時能自動綁定 Gateway。
  3. 導入 Streaming Compression（邊讀邊壓），防止超大 JSON (如 Vivado log) 導致 OOM。
* **限制**: Proxy 的介入延遲必須小於 10ms。不得修改 AutoAgent-TW 現存任何 LLM prompt，達到 100% 透明代理。

## 3. 架構設計與 Trade-offs
### 方案 A: CLI 命令列代理 (舊方案)
* **缺點**: AI 透過 `use_mcp_tool` 呼叫 Native Server 時會繞過 CLI Script，導致壓縮徹底失效。

### 方案 B: MCP JSON-RPC Proxy Gateway (最終採用方案)
* **優勢**: 在 LLM 與 Native Server 間建立隔離網關。
  - **Interceptor**: 解析 JSON-RPC Payload。
  - **AutoSkill Registry**: `auto_register.py` 動態更新 `mcp-router.toml` 白名單。
  - **RTK Filter**: 透過 `subprocess.PIPE` 的流式輸入輸出，高速調用 Rust `rtk compress`。

## 4. 資安威脅建模 (STRIDE)
* **Spoofing (假冒) & Elevation of Privilege (越權)**: 
  * 由於所有 MCP 工具流量將被強迫匯流至單一 Proxy Gateway，這裡自然形成了 **Zero Trust Choke Point**。
* **防禦**:
  * Gateway 僅允許對 `mcp-router.toml` 內的白名單路徑進行路由轉發。
  * 提供 `--inspect` 與 `Guardian` (--verbose) 模式，在資安掃描時強制暴露出未經污染的原始 JSON，防止 Prompt Injection 去除重要查核軌跡。

## 5. 編排與執行模式 (Orchestration)
採用 Wave 並行化部署：
- **Wave 1**: 建立 Gateway 核心監聽服務 (`mcp-router-gateway.py`, `mcp-router.toml`)
- **Wave 2**: 實作動態註冊機制 (`auto_register.py` 與 AutoSkill 連動)
- **Wave 3**: 壓力與整合測試 (`test_gateway.py`)，確認 Streaming 回傳正確。

## 6. 附註
此規劃完全遵循 `temp/cmpkiller_autoskill.md` 最終版的「MCP Proxy Gateway」架構。
