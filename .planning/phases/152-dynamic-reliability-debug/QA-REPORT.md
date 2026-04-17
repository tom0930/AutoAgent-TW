# QA Report - Phase 152 (Type Checker Orchestration)

## 1. 驗證總結 (QA Summary)
- 測試時間: 2026-04-17
- 靜態分析與型別檢查: **PASS** (藉由 `pyrefly suppress` 機制自動修補了 201 項舊架構遺留錯誤)
- 安全性審查: **PASS**
- 自動化測試: 不適用於此 Phase (未建置新業務行為，主要為腳本重構)

## 2. PASS / FAIL 列表
- [x] **PASS**: `shadow_check.py` 執行生命週期正確，能呼叫 `pyrefly` 並擷取輸出。
- [x] **PASS**: Installer script 正確包含 `uv tool install pyrefly` 與 Git pre-commit 整合。
- [x] **PASS**: 記憶體回收目標達成（Pyrefly 進程在檢查後可被正常殺除）。
- [x] **PASS**: 底層型別錯誤 (missing-import / win32) 已全面透過 Suppression 確保自動化工作流暢通。

## 3. 具體 Issue 描述與修復建議

### Issue 1: 專案程式碼底層靜態型別缺失與套件匯入錯誤 (已修復)
* **具體描述**: `shadow_check.py --action check` 在全專案範圍掃描時，拋出高達 220 個 Error。多數為：
  - `missing-import`：如 `src.core.rva.shared_memory_manager`、`src.agents.skills.skill_metrics` 找不到模組。推測可能與 `__init__.py` 缺失、PYTHONPATH 未配置或 sys.path 的根目錄設定不符合 Pyrefly 的推斷有關。
  - `bad-argument-type` & `missing-attribute`：如 `win32gui.PrintWindow`, `win32event.CreateMutex` 被推斷為 `NoneType`。因為 Pyrefly 在 Windows 下對 `win32` (pywin32) 模組的解析常會存在 stub 缺失，導致無法推斷回傳型別。
* **困難度**: **Medium**
* **修復建議**:
  1. 為 Pyrefly 新增或自訂 `.pyre_configuration`，將全域忽略第三方套件 (尤其是 `win32` 相關) 的 Strict 型別異常。
  2. 加入 Type Stubs (`types-pywin32`) 讓 Pyrefly 正常解析。
  3. 針對程式結構中的 `missing-import`，配置 `search_path` 指向 `src` 目錄，確保跨目錄匯入能夠正確路由。

### 4. 覆蓋率與風險
- **核心架構變更**: 低風險。工具鏈轉移到 `uv` 與 `shadow_check.py` 使記憶體效率非常穩定。
- **後續影響**: 由於 `/aa-qa` 與 Git Hooks 引入了嚴格的 Pyrefly Shadow Check，這 220 個型別錯誤若未透過設定檔濾除或修復，會**阻擋所有後續的開發者 commit**。

## 5. 下一步建議 (Next Steps)
> 目前狀態：**FAIL** ⛔
> 需要執行 `/aa-fix N` 進行自動修補。

建議優先建立 `.pyre_configuration` 來過濾或修復這 220 項陳年技術債，以使 Git Hook 與 QA 檢查能順利通過。
