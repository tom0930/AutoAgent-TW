# Phase 154: Advanced Deep Debugging (ELF & Symbolic Logic)

## 1. 目標 (Objective)
深度整合硬體除錯資訊，使 AI 能從「看 Raw Hex」進化到「看變數與行號」。利用專案編譯產出的 `.elf` 或 `.map` 檔案，實現精確的符號化定位。

## 2. 核心技術選型 (Technical Stack)
- **Tool**: `pyelftools` (Python 庫) 或是 `riscv-none-embed-nm` (對應平台工具)。
- **Logic**: 將 `hex_parser.py` 升級為 `symbolic_parser.py`。
- **Integration**: 當 AI 看到 Log 中的地址（如 `0xC0001234`）時，自動查詢 Symbol Table 得到 `dma_base_addr`。

## 3. 待解決的問題 (Challenges)
- **實時性**：如何在不影響 Bridge 效能的情況下進行大體量 ELF 的檢索。
- **動態偏置**：處理系統加載時的動態偏移位址。

## 4. 決策 (Decisions)
- 先聚焦於靜態 Symbols 映射。
- 優先支持 **MicroBlaze** 與 **ARM Cortex** 通用的 ELF 格式。
