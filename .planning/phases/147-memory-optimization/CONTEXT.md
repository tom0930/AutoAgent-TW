# Phase 147: System Resource & Multi-Process Optimization - Context

## 1. 核心意圖 (Intent)
優化系統資源占用，解決 Antigravity 子進程過度增生 (Zombie Agents) 導致的記憶體溢出問題。

## 2. 當前現況分析 (Current State)
- **進程數**: 48+ 個 (Antigravity.exe, pyrefly.exe, gk.exe)。
- **記憶體**: ~4.3 GB。
- **根本原因**: 
    - `spawn_manager.py` 使用 `DETACHED_PROCESS` 標記，導致父進程結束後子進程未被回收。
    - LSP (Language Server) 模型在每個子代理中重複啟動。
    - `pyrefly.exe` 視覺引擎緩衝區未定時釋放。

## 3. 技術決策 (Decision Records)
- **DR1**: 將 Windows 進程啟動標記從 `DETACHED_PROCESS` 改為 `CREATE_NEW_PROCESS_GROUP`。
- **DR2**: 引入 `ResourceSentinel` 模式，在 Phase 結尾執行強制性的孤兒進程回收。
- **DR3**: 實施 `Worker Pool` 併發限制，初始上限設為 4。

## 4. 資安與穩定性需求 (DoD)
- [ ] 系統總記憶體占用需降至 1.5GB 以下。
- [ ] 併發執行時進程數不超過 (CPU Core * 2)。
- [ ] 任務結束後必須自動執行資源回收。

## 5. STRIDE 分析
- **DoS**: 異常任務觸發 fork-bomb 風險。防護：設置進程計數器上限與超時強制殺死機制。
