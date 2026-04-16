# Task 1: Foundation & Shared Memory Bridge

## 🎯 目標
實作基於 `multiprocessing.shared_memory` 的高效影像傳遞通道。

## 📋 具體步驟
1. [ ] **建立 `src/core/rva/shared_memory_manager.py`**：
   - 實作 `VisionBuffer` 類別。
   - 負責 `shm.create` (Server/PyRefly 側) 與 `shm.attach` (Client/Antigravity 側)。
   - 定義記憶體佈局：前 16 byte 為 Metadata (Width, Height, Format, FrameID)，後端為 Raw RGBA Data。
2. [ ] **整合 Mutex 鎖**：
   - 使用 `win32event.CreateMutex` 確保跨進程讀寫一致性。
3. [ ] **實作零拷貝讀取**：
   - 利用 `np.ndarray(buffer=shm.buf)` 直接映射記憶體，避免 data copying。
4. [ ] **開發測試腳本 `scratch/test_shm_latency.py`**：
   - 測量從 PyRefly 寫入到 Antigravity 讀取的延遲，標竿需 < 5ms。

## 📄 預期變更文件
- `src/core/rva/shared_memory_manager.py`
- `src/core/rva/rva_engine.py` (導入新 Buffer 讀取邏輯)

## ✅ 驗證標準 (UAT)
- 成功在兩個獨立 Python 進程間傳遞 4K 隨機像素陣列。
- 監控記憶體，確認沒有因為傳輸影像而發生 Page Fault 或 Memory Swap。
