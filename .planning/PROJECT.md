# Project: AutoAgent-TW
Version: v1.7.5
Status: Active (Phase 132 - Buffer Engine Deployed)
Description: 專注於全自動、無感、具備高韌性（Resilience）的高級 AI 系統與知識庫自動化管道。
Type: Python CLI & Autonomous Agent Workspace

## 📝 專案說明 (Project Description)
AutoAgent-TW 是一個高度自動化、具備背景排程與防呆修復（Self-Repair）能力的自主代理開發環境。
v1.7.0 之開發核心為「底層韌性與容錯升級 (Resilience Upgrade)」，導入全方位的錯誤分類、指數退避重試、降級熔斷、花費監控與人工介入等待機制。
v1.7.4 之開發核心為「知識自動化與上下文優化 (Knowledge Automation)」，導入向量資料庫整合、動態知識庫檢索與長期記憶優化機制。

## 🎯 核心目標 (Core Objectives)
1. 將原本脆弱的單次腳本執行強化為能在惡劣網路環境與突發異常下存活的高韌性系統。
2. 在發生嚴重例外狀況（如 Token 花費暴走、權限阻擋）時，能有效暫停並透過 LINE 通知人工介入，不再盲目無限循環。
3. 把各類底層例外精準分類並實施隔離對策 (TRANSIENT, RECOVERABLE, DEPENDENCY, LOGICAL, FATAL)。
