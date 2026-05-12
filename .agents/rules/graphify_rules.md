# Graphify Knowledge Graph Rules (v3.7.2)

## 核心準則
- **架構先行**: 在處理本專案任何導航、重構或新功能開發任務前，**必須**先確認知識圖譜狀態。
- **工具調用**: 
    1. 呼叫 `graphify_status` 檢查新鮮度。
    2. 若顯示 `outdated` 或 `N/A`，呼叫 `graphify_update`。
    3. 使用 `graphify_query` 進行架構探索（取代盲目的 grep）。

## 查詢範例
- "用 Graphify 查詢所有跟 Line Pay 相關的模組"
- "根據最新 knowledge graph 產生支付流程的調用鏈"
- "確認 `src/core/auth.py` 被哪些組件引用"

## 降級機制
若 Graphify 無法提供準確資訊，請自動切換至 `grep` / `ripgrep` 並在 `VERIFICATION.md` 中記錄。
