# Roadmap: v1.7.0 Resilience Upgrade

## Phase 1: 錯誤分類引擎 (Error Classification System)
- `error_classifier.py`: 精準分類為 5 個等級 (TRANSIENT, RECOVERABLE, DEPENDENCY, LOGICAL, FATAL)
- 從 Traceback 識別具體錯誤狀態 (Rate Limit, Timeout, API Down, Context Overflow)

## Phase 2: 指數退避重試引擎 (Low-Level Retry Engine)
- `retry_engine.py`: 針對 TRANSIENT 等級錯誤使用「指數退避 (Exponential Backoff) + 隨機抖動 (Jitter)」自動重試
- 引入 `@with_retry` 裝飾器增強核心方法的抗壓力

## Phase 3: 智能降級與熔斷策略 (Fallback & Circuit Breaker)
- `fallback_manager.py`: 當模型或服務達到極限時降級
- 處理 Model Fallback (轉為 mini 模型) 與 Context Compression (上下文自動摘要縮減)
- `circuit_breaker.py`: 保護外部 API (若連續失敗，啟動熔斷)

## Phase 4: Token 與成本監控 (Cost & Token Monitoring)
- 新增 Token 消耗累計計算
- 引入「預算限制」，當循環浪費大量額度時阻斷執行 (轉為 FATAL)
- 將消耗推播顯示至 `status.html` 儀表板

## Phase 5: 致命錯誤人工介入流程 (Human-in-the-loop for FATAL)
- 遇到 FATAL 等級錯誤，主動發送確認請求（經由 CLI 中斷或 LINE 訊息）
- 系統暫停執行 (Pause)，等待使用者批准 (承認風險、選擇強制執行、或輸入新方向) 後才能解鎖
