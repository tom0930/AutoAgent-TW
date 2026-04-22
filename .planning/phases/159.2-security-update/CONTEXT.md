# Phase 159.2: SECURITY.md Update & Hardening Context (v2.1)

## 1. 意圖與背景 (Intent & Background)
在 Phase 158.5 中，我們成功導入了 **IDE Memory Stealth Mode**，透過將 Pyrefly LSP `exe` 重新命名為 `.disabled`，強迫其轉為 "One-Shot CLI" 模式，成功將 IDE 記憶體從 4GB+ 壓縮至 < 200MB。
然而，`REVIEW-REPORT.md` 指出：此機制屬於「防禦性架構」，且涉及路徑劫持 (Path Hijacking) 式的手段。若未在 `SECURITY.md` 中明文定義，未來可能被誤認為惡意行為或防毒軟體誤判。
同時，面對即將到來的 Phase 159 (FPGA RVA Upgrade)，我們需要確保系統的自動化操作有更清晰的安全邊界。

## 2. 邊界定義與約束 (Boundaries & Constraints)
- **DoD (Definition of Done)**:
  1. `SECURITY.md` 必須包含專門的 "IDE Extension Hardening (Stealth Mode)" 章節。
  2. 明確說明 `exe.disabled` 的運作原理，並宣告其為合法、受控的系統行為。
  3. 紀錄針對 Phase 158.5 QA 發現的 `shadow_check.py` 並發競爭風險 (Race Condition) 的修復策略。
- **約束**: 文件更新必須符合 Zero-Trust (ZT) 原則。

## 3. 架構選型與 Trade-off (Architecture & Trade-offs)
- **方案 A (整合入現有模塊)**: 將說明加入現有的 `Installer Security` 中。
  - *缺點*: 職責不符，LSP 屬於 Runtime 行為而非 Installation。
- **方案 B (獨立安全章節) [選擇此方案]**: 在 `SECURITY.md` 新增 "Runtime Resource & Extension Hardening" 章節。
  - *優點*: 清晰定義了 Antigravity 在 Runtime 階段的主動防禦與資源回收機制。

## 4. 資安威脅建模 (STRIDE Analysis)
| Threat | Vector | Mitigation (Stealth Mode / VDyn) |
| :--- | :--- | :--- |
| **Tampering** | 惡意腳本或 IDE 異常重新啟用 `.disabled` 擴充 | **Stealth Mode**: 透過專屬 `shadow_check.py` 進行受控啟用 (Rename-Run-Rename)，並結合 `.pyrefly.lock` 避免競爭。 |
| **Denial of Service (DoS)** | LSP 守護進程無限增生導致系統 OOM | **Stealth Mode**: `pyrefly_mode.py` 啟動時強制隔離，限定單次執行 (One-shot) 最大執行緒數。 |
| **Elevation of Privilege** | RVA (視覺自動化) 越權點擊或執行 | **FPGA Phase 159 預防**: 將 VDyn / RVA 權限嚴格限制在 `UIA-First` 框架的白名單視窗內。 |

## 5. 編排策略 (Orchestration)
- 本次任務屬於文檔與架構準則同步，無需 Wave 並行化，採單線路執行 (discuss -> plan -> execute)。
- 下一步 (aa-plan) 將根據此 Context 撰寫具體的 PLAN.md。
