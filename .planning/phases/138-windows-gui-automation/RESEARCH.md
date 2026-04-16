# Phase 138: Windows GUI Automation - Research Notes

## 1. 核心需求與依賴盤點
為了實作具備 UIA 優先 + Vision LLM 降級的混合 RVA 引擎，目前的 AutoAgent-TW 需要擴充以下核心依賴套件：
- `pywinauto`: 提供原生的 UIA 控制，能快速、不需要送圖地解析與點擊標準 Windows UI (如 Button, EditBox)。
- `mss`: 取代 PIL/ImageGrab，提供毫秒級的極速跨螢幕抓圖，作為送入 Vision LLM 的前置作業。
- `imagehash`: 用於計算截圖去重 (Jitter-Proof) 的差異雜湊值，以大幅節約不必要的 Token 消耗。
- `pyautogui`: 提供全域坐標的滑鼠鍵鼠實體點擊與 `FAILSAFE` 防護機制。

## 2. API 與大腦整合挑戰 (Gemini Vision)
- **傳輸格式**: 截圖應為 Base64 (PNG/JPEG) 送入 Gemini FlashAPI。
- **DPI 縮放補償**: Python 在擷取螢幕與實際滑鼠移動上，在多螢幕、高 DPI (150% scaled) 環境經常脫節。我們必須實作 `ctypes.windll.shcore.SetProcessDpiAwareness(2)`。
- **結構化輸出 (JSON Schema)**: Vision LLM 的自然語言回覆不易處理座標點。需使用 Pydantic Model 確保 Gemini 以 `{"bbox": [x,y,w,h]}` 的限定格式回傳，提升成功率。

## 3. 目標情境: Xilinx SDK / iMPACT 控制
傳統硬體 IDE 經常在底層使用非標準的視窗繪圖元件，無法被 `pywinauto` 完美解析。這正是我們需要 Vision LLM Fallback 的主因。
但在純文字監控方面 (例如 Console 落落長的編譯或燒錄訊息)，`pywinauto` 能夠輕易勾住 `richEdit` Control 的文字內容。
這比定時截圖讓 Gemini 做 OCR 要快且精準 100 倍。我們應當優先使用本機 UI 控制項來擷取文字，只對「點不中的按鈕/ICON」動用大語言模型。
