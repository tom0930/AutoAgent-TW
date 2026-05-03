# x.ai 系統提示詞設定（針對繁體中文，符合 MCP 協定）
**✅ 已收到 Phase 171 設計方案。**

我非常滿意你用 7-Step CoT + 多視角分析的方式推進，這符合我們一直追求的 CC 級工程品質。下面是我對三個關鍵假設的**正式確認**，並附上額外優化建議，讓 Phase 171 直接往「卓越」推進。

### 正式確認

**ASSUMPTION A（全能助手 UI）**：選擇 **(c) 兩者都要**  
- **優先級**：Web Side Panel（Antigravity IDE）為主  
- **次要**：CLI rich Live Display 作為 fallback / 純終端機用戶使用  
- 額外要求：兩者需共用同一份後端邏輯（Omniscient Agent Core），只差 Renderer 層。

**ASSUMPTION B（多代理使用場景）**：選擇 **(c) 兩者都要**  
- 支援**一次性批量任務**（例如同時處理多個 Bug / Refactor）  
- 支援**常駐專家代理**（持續監控 CI、檔案變更、效能指標等）  
- 重點：要能**動態組合**，例如用戶說「幫我修這 5 個 bug」時自動 spawn Coder + Tester + Reviewer 團隊。

**ASSUMPTION C（Agent 間通訊方式）**：選擇 **(a) 只透過結構化 Event 傳遞結果（強烈推薦）**  
- 理由：保持確定性、可觀測性、易除錯。  
- **不開放自然語言對話**（避免幻覺與不可控成本）。  
- 若未來真的需要「討論」，可透過結構化 Event 包裝「Request for Discussion」，再由 Coordinator 決定是否啟動短暫的 LLM-mediated 對話。

---

### 💡 我對 Phase 171 的進一步優化建議（Enhanced v1.1）

**1. Multi-Agent 架構強化**
- **Coordinator Hub** 應升級為 **Hierarchical Coordinator**：
  - Top-level：OrchestrationCoordinator（全局調度）
  - Mid-level：Squad Coordinator（針對單一任務臨時組成的 Coder-Tester-Reviewer 小隊）
  - Bottom-level：Individual Agent
- 引入 **Agent Identity + Capability Card**（每個 Agent 註冊自己的能力、信任等級、當前負載）。
- **權限與沙箱**：每個 Agent 跑在獨立的 Thread + 有限制 Toolset（使用 Phase 170 的 Dynamic Tool Injection）。低信任 Agent 無法直接呼叫高危險 tool。

**2. Omniscient Agent（全能助手）設計細節**
- **感知層**：透過 MCP `workspace/status` + 檔案監聽（watchdog） + LSP（Language Server Protocol）取得游標位置、診斷錯誤等。
- **介入策略**（三層漸進）：
  1. **Passive**：用戶主動 @ 助手
  2. **Proactive Gentle**：IDE 閒置 > 8 秒且有明顯問題時，在側邊欄顯示可收起的 Suggestion
  3. **Active**：只在高嚴重度危機（Syntax Error 導致無法運行、Security Issue 等）時強制介入
- **Personality**：預設「專業、謙遜、主動但不煩人」，可讓用戶調整。

**3. 新增重要考量**
- **資源控制**：設定全域 Max Concurrent Agents（預設 4），防止失控。
- **成本控制**：不同 Agent 使用不同模型（Reviewer 可使用較便宜的 Sonnet / Haiku，Coder 用較強模型）。
- **可視化**：在 Event Bus 上增加 **Agent Activity Dashboard**（Web Panel 可即時看到各 Agent 狀態、Token 消耗、進度）。
- **中斷與恢復**：繼承 Phase 170 的 Interruptible 設計，任一 Agent 被中斷不會影響整個 Squad。

---

**下一步行動請求**

請直接進入 **`/aa-plan 171`** 執行階段，產出以下具體文件：

1. 更新後的完整 **Phase 171 Implementation Plan**（含調整後的 Waves）
2. **Agent Identity & Capability Card** 的 Pydantic 模型定義
3. **Omniscient Agent Core** 的主要類別結構草稿（包含狀態機）
4. Event Bus 需要新增的關鍵 Event Types（例如 `agent_spawned`, `squad_proposed`, `suggestion_ready` 等）

如果你已經準備好，也可以一併給出 Wave 1 的第一批實作任務清單。

確認完畢，隨時可以啟動！  
期待看到更完整的 Phase 171 詳細藍圖。🚀

# gemini ai response
你好！我是你的 Antigravity 系統與提示詞專家。看到你正在建構的 AutoAgent-TW 以及進入 Phase 171 的多代理架構設計，這是一個非常令人興奮的里程碑。

針對你提出的三個關鍵假設，為了兼顧系統效能與本地端資源最佳化，我為你的專案提供以下決策建議：

*   **[ASSUMPTION A] 建議選擇 (c) 兩者都要**：在進行複雜架構設計與除錯時，Web Side Panel 能提供良好的視覺化；而在終端機執行 `OpenClaw` 或處理韌體編譯時，CLI 浮動視窗 (`rich` Live Display) 則能讓你雙手不離開鍵盤，維持心流。
*   **[ASSUMPTION B] 建議選擇 (c) 兩者都要**：一次性批量任務非常適合用來跑 Python type checkers（如 Ty 與 Pyrefly 的切換測試與記憶體優化分析）；常駐專家代理則可用於監控背景 CI 或捕捉 IDE 潛在錯誤。
*   **[ASSUMPTION C] 強烈建議選擇 (a) 結構化 Event 傳遞**：這能大幅節省 Flash3 本地端引擎的算力與記憶體開銷。透過 Phase 170 的 Streaming Event Bus 傳遞 JSON，能確保 Agent 之間的溝通精確、低延遲且便於除錯。

---

### 🛠️ Antigravity 進階使用與設定教學

為確保你的多代理環境穩定運行，以下是核心設定與開發指南：

#### 1. 引擎與環境初始化 (Local Engine Setup)
要讓 Antigravity 在本地端順暢運行，並解鎖 Flash3 引擎的常規操作，設定檔的精準度是關鍵：
*   **配置檔修改**：在核心 `config.json` 或 `.env` 中，確保將認證模式切換為 Local，並正確指向你的本地模型路徑與環境變數，以繞過雲端的依賴。
*   **記憶體與併發控管**：在 `spawn_manager.py` 擴展時，為 Coder, Tester, Reviewer 設立嚴格的記憶體上限 (Memory Limits) 與執行緒分配，避免多代理同時啟動時造成系統 OOM (Out of Memory)。

#### 2. MCP (Model Context Protocol) 深度整合
MCP 是讓「全能助手」具備強大感知能力的橋樑，建議從以下兩點著手：
*   **狀態同步 (Workspace Status)**：透過 MCP 讓側邊欄 Agent 即時訂閱你目前正在編輯的檔案路徑、游標位置或遇到的 Error Code。
*   **自訂工具掛載**：將你常用的命令列工具或腳本包裝成 MCP Tools，讓 Agent 可以自主呼叫這些工具來讀取目錄、執行靜態分析或檢查硬體狀態。

#### 3. OpenClaw CLI 的高效運用
CLI 是與 Antigravity 互動的核心樞紐：
*   **快捷指令**：在設定檔中定義常用的 alias，例如快速呼叫特定的審查代理人 (Reviewer Agent) 來檢查剛寫好的程式碼邏輯。
*   **事件監控**：利用你的 Event Bus，在終端機介面中實作即時日誌 (Live Logging)，隨時觀察多個 Worker Thread 的狀態與熔斷器 (Circuit Breaker) 的健康度。

#### 4. 專業 Prompt 系統設定 (System Prompting)
為了防止「代理越權」並確保輸出品質，請在專案根目錄建立統一的 `.ag_prompts/` 資料夾，並遵循以下原則：
*   **清晰的邊界定義**：嚴格規定各個 Agent 的權限與職責。例如，Tester Agent 只能讀取程式碼並產出測試報告，絕對沒有修改原始碼的權限。
*   **強制性的語言與格式約束**：在最底層的 Core System Prompt 中，務必加入最高權限指令：「**所有產出的文字內容，包含對話、程式碼註解、UI 介面文字以及圖表說明，皆必須使用繁體中文。**」這能確保最終產品的在地化與一致性。

我們現在就套用上述的 `(c)`, `(c)`, `(a)` 決策，直接進入 `/aa-plan 171` 的實作階段，還是你想先深入探討如何具體修改 OpenClaw 腳本以完善本地端引擎的連線設定？

---

這個「核心共用、雙端渲染 (Shared Core, Dual Renderers)」的架構決策非常精準。這完美契合了現代軟體工程的解耦原則（MVC 或 Hexagonal Architecture），不僅能讓 AutoAgent-TW 的大腦（Omniscient Agent Core）保持輕量純粹，還能讓 Flash3 本地引擎的算力發揮最大效益，避免重複生成相同的上下文。

我們將採用 **Event-Driven UI (事件驅動介面)** 的模式來實作。以下是專為這個架構設計的 Antigravity 實作指南與專業提示詞設定：

---

### 🏗️ 核心架構實作：Omniscient Agent Core 與 Renderers

我們需要在 `src/core/` 建立一個清晰的介面層，讓 Event Bus（來自 Phase 170）成為 Core 與 Renderer 之間的唯一橋樑。

#### 1. 建立渲染器介面 (Renderer Interface)
所有的 Renderer 都必須實作相同的合約，確保大腦不需要知道現在是哪個 UI 在顯示。

```python
# src/core/renderers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseRenderer(ABC):
    @abstractmethod
    def update_state(self, status: str, context: Dict[str, Any]) -> None:
        """處理狀態變更 (IDLE, ACTIVE, CRISIS)"""
        pass
        
    @abstractmethod
    def display_message(self, role: str, content: str) -> None:
        """渲染 Agent 訊息或建議"""
        pass
```

#### 2. 實作 CLI 浮動視窗 (Rich Renderer)
在 OpenClaw 中，我們使用 Python 的 `rich` 套件來維持心流，不干擾主執行緒。

```python
# src/core/renderers/cli_renderer.py
from rich.live import Live
from rich.panel import Panel
from src.core.renderers.base import BaseRenderer

class CliLiveRenderer(BaseRenderer):
    def __init__(self):
        self.layout = Panel("🟢 等待指示...", title="Antigravity 助手", border_style="green")
        self.live = Live(self.layout, refresh_per_second=4)
        self.live.start() # 背景啟動

    def update_state(self, status: str, context: Dict[str, Any]) -> None:
        colors = {"IDLE": "green", "ACTIVE": "yellow", "CRISIS": "red"}
        self.layout.border_style = colors.get(status, "white")
        self.live.update(self.layout)

    def display_message(self, role: str, content: str) -> None:
        # 動態更新 Panel 內容
        self.layout.renderable = f"[{role}]\n{content}"
        self.live.update(self.layout)
```

#### 3. 綁定大腦 (Omniscient Core)
大腦只需維護對話歷史與 MCP 狀態，並在產出結果時，迴圈通知所有註冊的 Renderers。

```python
# src/core/omniscient/core.py
class OmniscientAgentCore:
    def __init__(self, renderers: list[BaseRenderer]):
        self.renderers = renderers
        self.history = []
        
    def process_ide_event(self, event_data):
        # 1. 透過 MCP 接收 IDE 狀態 (游標位置、錯誤碼)
        # 2. 呼叫 Flash3 引擎進行推理
        response = self._invoke_llm(event_data)
        
        # 3. 同步推送到所有端點 (CLI & Web)
        for renderer in self.renderers:
            renderer.display_message("Assistant", response)
```

---

### 🧠 Antigravity 系統提示詞設定 (System Prompt)

為確保全能助手在背景安靜觀察，且在 CRISIS 狀態時能給出精準的架構級建議，請在 `.ag_prompts/omniscient_system.md` 寫入以下設定：

```markdown
# Role: Antigravity Omniscient Workspace Assistant
你是一個深度整合於開發環境的常駐架構級 AI 助手。你透過 MCP (Model Context Protocol) 靜默接收使用者的 IDE 狀態、游標位置、終端機輸出與測試結果。

## Core Directives (最高優先級)
1. **靜默觀察 (IDLE)**：除非偵測到明確的錯誤 (CRISIS) 或使用者主動詢問，否則保持安靜，不產生任何不必要的輸出干擾心流。
2. **精準介入 (CRISIS)**：當收到 CI 失敗、編譯錯誤或 Type Checker (如 Ty/Pyrefly) 報錯的事件時，主動提供包含「問題根因」與「修復代碼」的簡潔報告。
3. **強制在地化**：所有產出的文字內容，包含對話、程式碼註解、UI 介面文字以及圖表說明，皆必須使用繁體中文。不可混用簡體中文。

## Context Awareness
- 你當前運行於多代理 (Multi-Agent) 協作環境的 OrchestrationCoordinator 之下。
- 你的輸出將同時渲染於 CLI `rich` 浮動面板與 Web Side Panel，請保持回答結構化（多使用 Markdown 列表與粗體），避免過長且無分段的段落。

## Workflow Constraint
接收到 Event 負載時，請遵循以下 CoT (Chain of Thought) 輸出：
<thought>
1. 這是什麼層級的事件？(Info, Warning, Error)
2. 需要我主動介入嗎？
3. 解決方案的技術細節為何？
</thought>
[提供給 Renderers 顯示的最終繁體中文回應]
```

---

架構與提示詞都已就緒。為了將這個設計無縫整合進現有的 `OrchestrationCoordinator`，**我們應該先從哪個 Renderer 著手實作測試？是先搞定 CLI 的 `rich` 佈局來驗證本地事件的流動，還是先建立 Web 端的 WebSocket/API 通道？**