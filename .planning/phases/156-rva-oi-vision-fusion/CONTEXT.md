# Phase 156: RVA & Open Interpreter Vision Fusion - CONTEXT

## 1. 核心願景 (Vision)
將 RVA (Robotic Visual Automation) 引擎升級為具備「語義辨識」能力的自主代理。透過整合 `Z:\open-interpreter` 的視覺能力，解決傳統 RVA 在處理動態 UI、混亂文字佈局及複雜錯誤狀態判斷時的脆落性 (Fragility)。

## 2. 歷史記憶檢索 (Memory Analysis)
- **Phase 146**: 曾規劃 Open Interpreter 作為本地代碼碼執行器，並確認了其與 Gemini Flash 的潛在整合。
- **Phase 148**: 實作了 Vision Engine 零拷貝架構，為本次高頻傳輸影像給 OI 奠定了效能基礎。
- **現狀**: RVA 已具備穩定的控制平面 (`control_plane.py`)，目前欠缺的是強大的判斷平面。

## 3. 架構設計 (Architecture)

### 3.1 視覺推進管線 (Vision Reasoning Pipeline)
1. **擷取 (Capture)**: `rva_engine` 定時觸發 `vision_client.py` 進行螢幕擷取。
2. **橋接 (Bridge)**: 實作新組件 `oi_vision_adapter.py`，將擷取到的影像 (MemoryStream/Base64) 封裝並導入 `Z:\open-interpreter\interpreter\core\computer\vision\vision.py`。
3. **推理 (Inference)**: 
   - 使用 **EasyOCR** 進行全畫面文字檢索（搜尋座標）。
   - 使用 **Moondream2** (Local VLM) 解答邏輯問題（例如：「登入按鈕是否為灰色不可點擊狀態？」）。
4. **指令 (Command)**: OI 回傳建議 JSON，由 RVA 解析為具體點擊或等待動作。

### 3.2 效能優化
- **GPU 加速**: 若環境支援，Moondream2 將載入至 GPU 以維持 < 500ms 的推理延遲。
- **Singleton Mode**: 預載入模型，避免每次判斷都重新載入權重。

## 4. 資安建模 (STRIDE Analysis)
- **Spoofing (偽造)**: 防止惡意程式注入偽造截圖給 OI 進行誤導判斷。
  - *防禦*: 擷圖程序必須具備系統級簽章。
- **Information Disclosure (洩漏)**: 避免 OI 將包含敏感資訊（密碼、Token）的截圖傳送至遠端 API。
  - *防禦*: 強制設定 `interpreter.llm.supports_vision = False` 或僅使用本地 `moondream`。
- **Denial of Service (拒絕服務)**: VLM 推理佔用大量 GPU/CPU，導致 RVA 系統掛掉。
  - *防禦*: 實作 `Reaper` 監控 OI 進程資源佔用，設置 Timeout。

## 5. DoD (Definition of Done)
- [ ] `oi_vision_adapter.py` 成功載入 `vikhyatk/moondream2` 模型。
- [ ] RVA 能夠將螢幕畫面發送給適配器並獲得文字描述。
- [ ] 實作一個測試 Scenario：RVA 依據畫面中的錯誤彈窗，自動由 OI 判定「關閉」或「重試」。
- [ ] 影像傳輸路徑維持在實體記憶體中，無額外寫盤動作（持久性優化）。

## 6. 技術債與風險
- Moondream2 的判斷準確性需進行多輪 Prompt 調優。
- `Z:\open-interpreter` 的 Python 依賴環境必須與 `autoagent-TW` 的 `uv` 環境相容。
