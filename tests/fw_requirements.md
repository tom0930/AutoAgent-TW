# Firmware Success Requirements & Patterns

## 🛠 測試準則 (Evaluation Criteria)
此文件供 `judge_agent` 參考，用於判別 FW 運行是否符合預期。

### 1. 啟動成功特徵 (Success Patterns)
當 UART Log 出現以下文字或 Regex 匹配時，判定為 PASS：
- `[SYS] Booting...Done`
- `[VDMA] Init Successful`
- `Main Loop Started`
- `System Ready (0xAA55)`

### 2. 致命錯誤特徵 (Failure Patterns)
出現以下文字時，判定為 FAIL 並觸發修復循環：
- `Assert failed at`
- `Illegal Instruction`
- `[ERROR] VDMA Timeout`
- `Data Abort`
- `Stack Overflow detected`

### 3. 超時設定 (Timeout)
- **Booting Timeout**: 5.0 秒
- **Operation Timeout**: 2.0 秒

### 4. 關鍵暫存器預期 (Register Map)
- **VDMA Status (0x44200004)**: Bit 14 (Error) 必須為 0。
- **GPIO State**: Bit 0 必須在初始化後拉高。
