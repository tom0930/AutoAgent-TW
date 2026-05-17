# 🐛 Bug Analysis: `z:\01` Execution Failure

## 📍 異常現象描述 (Symptoms)
- Agent 在處理 `z:\02` 時正常，但接著處理 `z:\01` (或 016) 時發生異常。
- Log 檔案開頭標示了 `02 ok,01 fail:  token??`。
- 關閉 IDE 並重開後，重新執行就恢復正常。
- 在 `z:\test_sopv7\issue\test_01_bug.md` 的日誌中，Agent 意外刪除了自己產生的 `atomic_wave_*.json` 檔案。

## 🔍 根本原因分析 (Root Cause Analysis)

經過分析 `test_01_bug.md` 日誌，發現導致問題的兩個主要原因：

### 1. Context Bloat 與 Token 耗盡 (Context Window Exhaustion)
日誌顯示 Agent 在執行過程中，進行了大量且密集的「直視模式」操作（連續呼叫 `view_file` 讀取數十張 JPG/PDF 憑證），並且在對話中頻繁列印、拆解每一筆發票的詳細金額與明細。
- **後果**：這導致上下文長度（Context Tokens）急速膨脹。當處理完 `z:\02` 再接著處理 `z:\01` 時，對話歷史累積的 Token 數量可能達到了 LLM 的上限，或者導致 IDE 外掛因記憶體/傳輸負荷過大而崩潰/失常（即日誌第一行的 `token??`）。
- **為何重開 IDE 會好**：關閉並重開 IDE 會清除或截斷過往龐大的對話歷史上下文（Context Reset），釋放了 Token 空間，使得 Agent 重新獲得了完整的思考能力並能順利執行。

### 2. PowerShell 環境下的命令列邏輯錯誤 (Shell Command Logic Error)
由於 Token 消耗導致 Agent 思考開始混亂，在清理 `temp/atomic_json` 目錄的舊資料時，犯了致命的 Shell 指令錯誤：
- **第一次指令失敗與非預期成功**：
  Agent 執行了 `del /Q temp\atomic_json\*; move temp\atomic_wave_*.json temp\atomic_json\`
  在 PowerShell 中，`del` 是 `Remove-Item` 的別名，不支援 `cmd` 的 `/Q` 參數，因此刪除失敗。但後面的 `move` 指令卻成功把 `atomic_wave` 檔案移進了資料夾。
- **第二次指令的毀滅性打擊**：
  Agent 發現舊資料沒被刪除，於是改用正確的 PowerShell 語法：
  `Remove-Item -Path temp\atomic_json\* -Force; move ...`
  但此時 `atomic_wave_*.json` **已經在 `atomic_json` 目錄內了**！這道 `Remove-Item ... \*` 指令無差別地把整個目錄清空，連帶刪除了 Agent 辛苦做好的 3 個波次 JSON 檔案，導致進度完全遺失。

## 💡 解決方案與預防措施 (Prevention & Fixes)

1. **Token 優化與定期重置 (State Handoff)**：
   對於大量檔案處理（如 `z:\01`, `z:\02` 這種包含 50+ 憑證的目錄），不應在同一個對話 Session 中從頭做到尾。應該引入 **斷點續傳 (Checkpoint/Handoff)** 機制，每處理完一個目錄，就將狀態寫入 JSON，並主動提示使用者開新對話或使用指令清理上下文。
2. **禁用連續指令執行 (Avoid Command Chaining)**：
   不要在一個命令中使用 `;` 或 `&&` 串接多個具依賴性的檔案操作。應分步執行：先確認刪除成功，再執行移動。
3. **優先使用 Python Script 處理檔案**：
   Agent 不應依賴底層的 Shell 指令（如 `del` / `move`，因為 PowerShell 與 Cmd 的語法混淆常導致災難），應優先撰寫或呼叫簡單的 Python 腳本（例如 `shutil` / `os` 模組）來確保跨平台的檔案清理與搬移。
