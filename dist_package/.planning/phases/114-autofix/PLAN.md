# Phase 114: AutoFix Engine Implementation Plan

## 1. Objective (目標)
實作具有創新與自癒能力的雙核 AutoFix 引擎。系統必須能在開發新功能或遭遇 QA 錯誤時，自我建立 Git 分支沙盒、擷取 Runtime 錯誤追蹤 (Traceback) 並呼叫 LLM 進行語義分析與修復。若修復失敗次數過高，系統會自動利用 Git 回滾防護，防止主機代碼污染。

## 2. Tasks (任務拆解)

### Task 1: 沙盒管理員 (Sandbox Manager)
- **檔案**：`scripts/autofix/sandbox_manager.py`
- **職責**：
  1. `create_sandbox(feature_name)`: 確保基於穩定的 master 建立並切換至新 Git 分支。
  2. `create_checkpoint(message)`: 在測試/修復前建立 commit 節點，記錄案發現場。
  3. `rollback_checkpoint(steps)`: 執行 `git reset --hard HEAD~{steps}` 回退至修復前的穩定狀態。
  4. `abort_sandbox()`: 放棄修復，切回 base branch 並強制刪除沙盒分支。
  5. `merge_sandbox()`: 順利修復/創新後，將沙盒安全合併回主線並刪除臨時分支。

### Task 2: 錯誤分析器 (Error Analyzer)
- **檔案**：`scripts/autofix/error_analyzer.py`
- **職責**：
  1. `run_with_capture(cmd)`: 使用 `subprocess.run` 執行傳入的指令（如 pytest、或者是編譯器指令），攔截 stdout, stderr、return code，並設定 Timeout (120s) 以防無窮迴圈鎖死系統。
  2. `generate_repair_prompt(target_file, exec_result)`: 針對擷取到的 Traceback 進行清洗與提取，內建嚴格的安全、型別規範提示詞 (符合 C/C++與 Python 專業規範)，並自動生成「修復建議 prompt」交給 Agent。

## 3. Risks & Interventions (風險與回滾策略)
- **Git 衝突風險**：若在沙盒分離期間，主線發生改變，合併時將觸發 Conflict。
- **對策 (Fallback)**：偵測到 Merge 失敗的回傳碼，立刻主動發送錯誤，執行 `git merge --abort`，並通知人類介入審閱。休眠並等待修正。
