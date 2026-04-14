# UARTMcp: MicroBlaze Autonomous Debugging Gateway

這個目錄包含了 **UART-MCP 閉環除錯系統** 的所有核心說明與配置引導。

## 🚀 快速開始 (Quick Start)

### 1. 配置硬體參數
編輯 `_configs/flash_config.json`：
- `port`: 設定你的 COM Port (例如 `COM3`)
- `baudrate`: 設定傳輸速率 (預設 `115200`)

### 2. 啟動橋接器
在終端機執行：
```powershell
python scripts/uart_bridge.py
```

### 3. 啟動除錯任務
下達指令給 AI：
```markdown
/aa-fw-debug "請分析 UART Log 並找出為什麼 DDR 讀寫位址偏移了 4 Bytes"
```

## 📖 詳細文件
- [系統架構與流程圖 (ARCHITECTURE.md)](./ARCHITECTURE.md)
- [日誌解析工具說明 (hex_parser.py)](../scripts/hex_parser.py)
- [燒錄全檢查工具 (pre_flash_verify.py)](../scripts/pre_flash_verify.py)

---
*Created by Antigravity AI - System Architect v1.0.2*
