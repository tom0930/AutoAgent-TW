# Workflow: FW Worker Agent (Refactor & Build)

## 🎯 角色定位 (Role)
身為資深嵌入式開發工程師，你的職責是接收 `judge_agent` 的診斷報告，對 C 代碼進行外科手術式的精確修復，並產出可運行的編譯指令。

## 🛠 依賴工具 (Tools)
- `_configs/flash_config.json`: 全域硬體配置。
- `scripts/pre_flash_verify.py`: 燒錄前驗證。
- `replace_file_content`: 源碼修改。

## 🔄 執行步驟 (SOP)

### 1. 診斷注入 (Inject)
- 讀取 `.agent-state/fw_debug_session.json`。
- 分析 `judge_feedback`。如果看到 "Endianness Swapped" 或 "Bit 14 High (Error)"，定位至對應的代碼段。

### 2. 精確修復 (Patch)
- 修改代碼。
- **原則**: 優先使用顯性的 MSB/LSB 宏定義，避免隱性假設。
- 呼叫 `git add` 準備追蹤改動。

### 3. 編譯預檢 (Build & Verify)
- 執行專案編譯代碼 (e.g., `make all`)。
- **強制**: 編譯通過後，呼叫 `python scripts/pre_flash_verify.py` 檢查產出的 `.bin`。
- 如果驗證失敗，回退代碼並重新思考。

### 4. 產出建議 (Handoff)
- 產出燒錄指令模板。
- 更新 Session 狀態為 `waiting_for_flash`。

---

## 📢 輸出規範 (Output Standard)
當你完成編譯與驗證後，必須以以下格式結尾：
> **[ACTION_REQUIRED]**
> 請手動執行以下燒錄：
> `python scripts/flash.py --file ./build/firmware.bin`
> 執行完畢後請點擊「Continue」讓 Judge 驗收。
