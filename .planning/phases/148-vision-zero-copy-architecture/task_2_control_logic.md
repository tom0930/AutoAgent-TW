# Task 2: Control Plane & State Machine

## 🎯 目標
建立控制通訊頻道，並實作 0% CPU 佔用的休眠與喚醒邏輯。

## 📋 具體步驟
1. [ ] **整合 `win32pipe` 建立命名管道服務器**：
   - 管道名稱：`\\.\pipe\AntigravityVisionControl`
   - 權限設定：僅限當前使用者 (ACL)。
2. [ ] **改造 `src/core/rva/pyrefly_service.py` (新創)**：
   - 實作「指令解析器」：處理 `PAUSE`, `RESUME`, `SHUTDOWN`。
   - 實作「狀態機」：
     - `Active`：持續更新 SHM。
     - `Standby`：調用 `threading.Event().wait()` 進入內核級休眠。
3. [ ] **加入垃圾回收觸發器**：
   - 在進入 `Standby` 時執行 `gc.collect()`。
4. [ ] **開發測試腳本 `scratch/test_standby_cpu.py`**：
   - 驗證在 `PAUSE` 狀態下，進程 CPU 持續穩定在 0%。

## 📄 預期變更文件
- `src/core/rva/pyrefly_service.py`
- `src/core/rva/control_client.py` (Antigravity 端的指令發送器)

## ✅ 驗證標準 (UAT)
- 成功透過指令遠端喚醒與凍結 Vision Engine。
- Standby 時 CPU 占用率降至作業系統能監測到的最小值。
