# Phase 159 Architectural Context: FPGA Toolchain RVA Upgrade

## 1. 任務目標 (Objectives)
工業化 Xilinx Vivado 與 Vitis 的自動化流程，將 AutoAgent-TW 的 RVA 引擎 (Eye-0 + Eye-1) 導入 FPGA 開發週期。

## 2. 核心決策 (Key Decisions)
- **控制器策略**: 實作 `VivadoController` 與 `VitisController`。
- **Hybrid 驅動**: 優先使用 Vivado 內建的 Tcl Console 進行指令執行，配合 UIA (Eye-0) 進行選單點擊與狀態監控。
- **視覺驗證**: 使用 Eye-1 (Gemini Vision) 辨識編譯進度條與錯誤圖示，提升對 GUI 異常的彈性。
- **資源隔離**: FPGA 工具鏈極耗資源，RVA 執行時將自動掛載 `AgentReaper` 監控系統負載。

## 3. 架構設計 (Architecture)
- **`src.core.rva.fpga_vivado`**: 封裝 Vivado 視窗、Tcl Console 注入與流程控制。
- **`src.core.rva.fpga_vitis`**: 封裝 Vitis (Eclipse) 視窗、Workspace 選取與 Debug 流程。
- **Orchestration**: `RVAEngine` 透過多 Agent 模式（Orchestrator + VivadoExpert）協作。

## 4. 外部技能與資源 (External Skills)
- **`mindrally/skills@fpga`**: 用於加速 FPGA 基本指令集控制。
- **`omer-metin/skills-for-antigravity@fpga-design`**: 基於 Antigravity 優化的 FPGA 設計子代理。

5. 資安與風險 (Security & STRIDE)
- **Tampering**: 防止自動化點擊觸發 destructive action（如 `Reset Project`）。
- **Information Disclosure**: 自動遮蔽 Tcl 日誌中的授權資訊與私有路徑。
- **DOS**: 監控 Vivado 資源佔用，必要時自動降級 RVA 抓取頻率。

## 5. DoD (Definition of Done)
1. 成功開發 `VivadoController` 並能自動開啟現行專案。
2. 實現 Tcl Console 的自動化輸入與輸出讀取。
3. 透過 Eye-1 驗證 "Bitstream Generation Successful" 彈窗。
4. 完成 P159 整合測試。
