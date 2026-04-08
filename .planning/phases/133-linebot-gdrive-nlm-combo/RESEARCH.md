# Phase 133: LineBot x Google Drive x NotebookLM (主動同步與 OCR 整合)

## 前置討論與決策回顧
參考 `CONTEXT.md`，核心整合已決定：
1. **主動雙軌架構**：LineBot 上傳至 GDrive 後直接觸發 NotebookLM 本地 `nlm source add`。
2. **前綴觸發**：如 `@大腦` 開頭，才會打 NotebookLM 查詢介面。
3. **圖片 OCR Token 控制**：發送圖片時先用 Gemini 取出純文字，文字存入 GDrive 後再餵給 NotebookLM。
4. **帳號綁定**：使用專案預設 NotebookLM 帳號 `pcvdep0101@gmail.com`，實作時將依賴本地終端的 `nlm login` 授權。

## 技術研究點 (Research)

### 1. `nlm` CLI 命令列呼叫
`nlm` 是用來介接 NotebookLM 的官方 CLI 工具。可以用 Python `subprocess` 穩定呼叫：
```python
import subprocess
import json

# 查詢
res = subprocess.run(
    ["nlm", "notebook", "query", notebook_id, query_text, "--format", "json"],
    capture_output=True, text=True
)
# 新增 Source
res2 = subprocess.run(
    ["nlm", "source", "add", notebook_id, "--drive", drive_file_id],
    capture_output=True, text=True
)
```
注意：Python 呼叫時需加入 error 處理，確保 CLI session 失效時能提供錯誤字串提醒使用者需重新 `nlm login`。

### 2. Gemini Vision OCR 用法
可以引入官方 `google-genai` SDK，發送輕量級的 OCR Prompt (如：「請擷取圖片中的重點與文字，不要做任何額外回答」)，這比直接把圖片給 NotebookLM 原生解析更可控，也更好在 Drive 進行檔案歷史追蹤。

### 3. GDrive 純文字建檔
原本 `scripts/kb_gdrive_sync.py` 只能上傳實體檔案。我們需要擴充它，支援寫入 `.txt` 的二進位串流，並標註 mimetype 為 `text/plain`。

## 安全性與 Token 管理
- `gateway` 腳本必須優先載入 `.env` 中的 `LINE_ADMIN_UID_LIST`，直接把不符權限的流量 return，做到 **Zero-Cost 防禦**。
- `gateway` 讀取 `.env` 的 `NLM_TARGET_NOTEBOOK_ID`。
