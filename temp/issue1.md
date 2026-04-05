# aa command issue
身為擁有 20 年實戰經驗的資深架構師，我必須說：**「這是一個非常深刻且具有代表性的案例。」** 

剛才遇到的 `cli.js` (13MB) 導致 Token 爆炸，正是目前 AI Agentic Workflow 在處理「混合了原始碼與編譯產物」的專案時最常見的陷阱。這絕對值得 **AutoAgent-TW (AA)** 核心機制的全面檢討與升級。

以下是我從架構師角度對 **「AA 上下文防護機制」** 的檢討與優化建議：

---

✅ **問題重述：**
AutoAgent-TW 目前的 `/aa-plan` 或 `/aa-execute` 流程，在啟動前是否應該具備「自動偵測與排除大規模檔案」的能力，以防止 Token 爆炸與不必要的成本？

📋 **核心檢討與改進方向 (AA Next Gen):**

| 改進模組 | 檢討內容 | 建議實施方案 (Architecture RFC) |
|------|------|------|
| **1. Pre-scan Guardrail** | 目前流程是「先讀取再說」，導致大檔案直接灌入 LLM。 | **強制前置檢查**：增加 `context_check.py`，若偵測到 > 1MB 檔案且不在忽略名單，自動發出警告。 |
| **2. Intelligent Ignorer** | 現有 `.gitignore` 可能不夠完整（有些 built 檔案未被 ignore）。 | **智慧推斷忽略**：自動檢查 `.js.map`, `.log`, `.tmp` 等副檔名，主動建議寫入 `.claudeignore`。 |
| **3. Phase Lifecycle** | 歷史 Phases 堆積在 `ROADMAP.md` 導致背景雜訊越來越多。 | **自動歸檔機制**：當 Phase N 狀態改為 ✅ Completed，自動將其 Detailed Wave 移至 `HISTORY.md`。 |
| **4. Token Visualization** | 使用者不知道目前 AI 讀取了多少 Context。 | **儀表板即時預警**：在 Dashboard 顯示當前「當前會話 Token 佔用比」，紅燈警告過載風險。 |

---

🚀 **推薦最佳方案：實施「上下文主動防禦 (Active Context Defense)」**

我建議在 AutoAgent-TW 的下一個版本中，將剛才我們手動執行的 **`context_guard`** 邏輯整合進核心的 `/aa-plan` 工作流。

**新的 `/aa-plan` 標準流程應為：**
1. **[感知]** 掃描工作區檔案大小分佈。
2. **[干預]** 若發現非必要的 1MB+ 檔案 -> **自動提示使用者** -> **加入忽略列表**。
3. **[精簡]** 讀取 ROADMAP 前，檢查歷史記錄長度 -> **自動建議 Archive**。
4. **[執行]** 這才真正將「精煉過後」的上下文送往 AI。

🔍 **網路最新資訊：**
目前的 AGI 框架（如 LangGraph, AutoGen）越來越強調 **「Memory Management」**。將過去的所有歷史全部丟入 Context 已經是落後的做法；現代的做法是「將歷史摘要化（Summarize history）」或「將歷史 RAG 化（Retrieve historical logs via RAG）」。

💡 **可執行選項 (針對您的專案優化)：**

| 選項 | 內容 | 目的 |
|------|------|------|
| **[1] 整合 `context_guard` 到 AA** | 將我剛才寫的腳本邏輯加入 `_agents/workflows` 的標準模板。 | 讓所有新 Phase 自動具備防護能力。 |
| **[2] 實施 Phase 歸檔規範** | 將 `.planning/HISTORY.md` 定義為標準產物。 | 保持 ROADMAP 維持在單一畫面可視的大小。 |
| **[3] 強化 RAG 權重** | 對於 Phase 001~005 資訊，強制使用 RAG 讀取而不是全文讀取。 | 節省主對話視窗的 Token 空間。 |

📌 **下一步行動：**
我會把這次的經驗**寫入您的 `PROJECT_MEMO.md` 或團隊規範中**。你想讓我現在就為你設計一個「AutoAgent 上下文管理規範 (RFC Docs)」嗎？這能讓未來接手或擴展的朋友少踩同樣的坑。



# 我建議在 AutoAgent-TW 的下一個版本中，將剛才我們手動執行的 context_guard 邏輯整合進核心的 /aa-plan 工作流。

新的 /aa-plan 標準流程應為：

[感知] 掃描工作區檔案大小分佈。
[干預] 若發現非必要的 1MB+ 檔案 -> 自動提示使用者 -> 加入忽略列表。
[精簡] 讀取 ROADMAP 前，檢查歷史記錄長度 -> 自動建議 Archive。
[執行] 這才真正將「精煉過後」的上下文送往 AI。


# 設計一個「AutoAgent 上下文管理規範 (RFC Docs)」