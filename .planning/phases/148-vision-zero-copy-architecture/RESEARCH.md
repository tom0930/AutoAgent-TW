# Phase 148: Domain Research - Vision Engine Zero-Copy & Standby

## 1. 影像傳輸方案比較 (Data Plane Architecture)

| 維度 | 現有方案 (JSON/Base64) | 提議方案 (Shared Memory) |
| :--- | :--- | :--- |
| **延遲** | 高 (~150ms 包含序列化與網路開銷) | 極低 (<10ms 內存引用的時間) |
| **記憶體佔用** | 影像大小的 1.33x ~ 4x (取決於複製次數) | 固定的 Buffer 大小 (1920x1080x4 = 8MB) |
| **CPU 消耗** | 序列化/反序列化消耗顯著 | 零 CPU 拷貝 (Zero-Copy) |
| **可靠性** | 受限於 HTTP 逾時與連線池 | 只要 OS 運行便極端穩定 |

## 2. Windows 進程生命週期保護 (Control Plane Safety)

### 2.1 Windows Job Objects
這是一組 Windows API，允許將一組進程視為一個單元。我們將啟動 `pyrefly` 並將其加入一個帶有 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` 標記的 Job 中。
- **優點**：即使 Antigravity 主程序或是 Python 虛擬機發生非預期崩潰（如硬體中斷、Task Kill），Windows Kernal 會在 Job 控制柄關閉後自動清除 Job 內的所有關聯進程。
- **實作組件**：`win32job.CreateJobObject`, `win32job.SetInformationJobObject`, `win32job.AssignProcessToJobObject`.

### 2.2 命名管道 (Named Pipes) vs Socket
- **選擇建議**：雖然 Socket 跨平台性好，但在單機 Windows 系統中，`win32pipe` 提供了更原生的 ACL (存取控制清單) 支持，能更安全地限制只有 Antigravity 可以發送訊號。

## 3. 已識別的陷阱 (Identified Pitfalls)

1. **共享記憶體遺留 (Stale Memory)**：Python 的 `SharedMemory` 若未調用 `unlink()`，重啟後可能因名稱衝突無法啟動。
   - **防護策略**：啟動前先嘗試 `attach` 原有名稱，若存在則先 `unlink`。
2. **螢幕破圖 (Race Condition)**：Antigravity 讀到一半時，PyRefly 正好在刷新下一幀。
   - **防護策略**：使用 `multiprocessing.Lock` 封裝，或採用「雙緩衝 (Double Buffering)」機制。
3. **不同解析度適配**：4K 螢幕與 1080P 螢幕的 Buffer 大小不同。
   - **策略**：在 Named Pipe 連線時，由 PyRefly 告知當前 Buffer 的行列數與格式。

## 4. 關鍵依賴清單 (Dependencies)
- `pywin32` (核心 Windows API 對接)
- `multiprocessing.shared_memory` (主機內影像交換)
- `numpy` (影像資料的高速變換)
- `win32job` (防禦性生命週期管理)
