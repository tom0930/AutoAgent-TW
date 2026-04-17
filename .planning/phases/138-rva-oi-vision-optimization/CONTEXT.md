# Phase 138 Architectural Context: RVA & Open Interpreter Vision Optimization

## 1. 🎯 需求拆解與邊界定義 (Decomposition & Boundaries)
- **目標**: 將 AutoAgent-TW 的 RVA (Robotic Visual Automation) 引擎與 `Z:\open-interpreter` 的核心視覺模組 (`computer.vision` 包含 Moondream2 與 EasyOCR) 進行深度判定結合。
- **邊界 (DoD)**: 
  - RVA 能將畫面狀態無縫傳遞給 OI 的 Vision 子系統。
  - OI 負責語義層解析 (「畫面上是否有紅色報警？」、「按鈕是否被停用？」) 而非僅依賴像素比較。
  - 無需向外部 API (如 OpenAI/Anthropic) 外洩畫面，所有推論 100% 在本地完成。

## 2. 🏛️ 系統架構圖 (System Architecture)
```mermaid
graph TD
    subgraph AutoAgent-TW [RVA System]
        Engine[RVA Engine]
        Capture[Screen Capture / State]
    end

    subgraph Open-Interpreter [Z:\open-interpreter]
        VisionMod[vision.py Core]
        TextExt[EasyOCR / Layout]
        Semantic[Moondream2 Local VLM]
    end
    
    Capture -->|Shared Memory / RAM| VisionMod
    VisionMod --> TextExt
    VisionMod --> Semantic
    Semantic -->|Semantic Insight (JSON)| Engine
    TextExt -->|Bounding Boxes| Engine
```

## 3. ⚙️ 技術選型與決策 (Technical Decisions)
- **Zero-Copy Payload 交握**: 取代傳統的 base64 + 磁碟 I/O，RVA 與 OI 間採 Python `multiprocessing.shared_memory` 或精簡的 NumPy Array 進行記憶體中傳遞，將傳輸延遲極小化。
- **Moondream2 作為決策中樞**: 選擇 Moondream2 (1.8B) 而非 Qwen-VL 等較大模型以防止 VRAM 出現爆點，並符合 RVA 的低延遲需求。

## 4. 🚀 並行與效能設計 (Performance & Concurrency)
- **非同步視覺管線 (Async Pipeline)**: RVA 在捕獲畫面後，不應阻斷事件循環 (Event Loop)。推論將丟入 ThreadPoolExecutor。
- **Agent Reaper 機制**: 為防止 VRAM 溢位，視覺分析模組在超過 1 分鐘閒置後，需具備動態卸載模型的能力。

## 5. 🛡️ 資安設計與威脅建模 (STRIDE & Security)
從我資安工程師的視角，這部分的整合潛藏以下威脅：
1. **[T] Tampering**: 截圖中若出現特定的混淆視角 (Adversarial perturbation)，可能欺騙 VLM，導致 Agent 執行錯誤的自我修復。(防禦: 設置 Prompt Validation Layer，對 VLM 的決策增加信賴區間閾值)。
2. **[I] Information Disclosure**: 確保 RVA 傳入 OI 的截圖**絕對不包含** `.env` 或高機密 IP 範圍，執行前先進行基本的 OCR Pattern 屏蔽 (Masking)。

## 6. 💼 AI 產品相關考量 (Product & UX)
- **UX 透明度**: 增加 GUI (Antigravity面板) 指示燈，讓使用者知道「目前是局部比對，還是深度語義理解」。
- **防濫用**: 限制每秒最大的視覺推斷次數，避免 GPU 過載導致開發機卡死。

## 7. 🚑 錯誤處理與恢復策略 (Error Handling & Recovery)
- 若 OI Vision 模組載入失敗 (CUDA OOM)，自動退回傳統的 RVA OpenCV 模板比對 (Template Matching) 模式降級運行。
- `try-except` 包裝模型載入，遇到 `torch.cuda.OutOfMemoryError` 時觸發 GC 與 VRAM 清理。

## 8. 🧪 測試策略 (Verification Plan)
- **Unit Test**: 給予含有已知「Error 500」字樣的假截圖，驗證 OI Adapter 能否正確 Parse 並且抽取 bounding box。
- **UAT**: 在模擬的使用者介面上，讓 RVA 識別並自動關閉突然彈出的干擾視窗 (`Popup`)。
