# PLAN: Code Review vs. Code-Review-Skill Diff Documentation

## 1. 需求拆解與邊界定義
- **目標**：產出詳細對比文件 `.\temp\diff_code_review.md`。
- **邊界**：涵蓋從 PR 的提交、檢查、描述到最終 Approve 的完整流程。

## 2. 技術選型與理由
- **Markdown (表格 + 列表)**：用於結構化呈現 6 大核心審核維度。
- **GSD 流程**：確保對比深度達到架構師級別。

## 3. 系統架構圖 (Mermaid)
```mermaid
graph TD
    A[Raw Code Changes] --> B[Code Review Layer]
    B -- Current -- > C[Surface Bug Hunting]
    B -- Enhanced (CR-Skill) -- > D[Holistic Quality Audit]
    D --> E[1. Overall Check]
    D --> F[2. Code Quality]
    D --> G[3. Architecture]
    D --> H[4. Documentation]
    D --> I[5. Testing]
    D --> J[6. Standard Labels]
```

## 4. 並行與效能設計
- 寫作任務，無並行鎖定問題。使用單一文件路徑。

## 5. 資安設計與威脅建模
- **資安重點**：`code-review-skill` 特別強調 XSS/SQLi 以及權限檢查，這是傳統 CR 容易忽略的。

## 6. AI 產品相關考量
- **專業化語氣**：確保 CR 的反饋是建設性 (Constructive) 的，而非僅是非黑即白的。

## 7. 錯誤處理、監控與恢復策略
- 檢查文件寫入路徑。

## 8. 測試策略
- **自檢**：確保對比表格準確引用了 `code-review-skill.md` 中的維度。

---

### GSD 8 維度檢查表
| 次元 | 檢查項目 | 狀態 |
| :--- | :--- | :--- |
| 1 | 覆蓋率 (Coverage) | 涵蓋 PR/Quality/Arch/Docs/Test 六大領域 | OK |
| 2 | 原子性 (Atomicity) | 獨立文件產出 | OK |
| 3 | 依賴 (Dependency) | 基於 `code-review-skill.md` 原文 | OK |
| 4 | 檔案範圍 (File Scope) | `.\temp\diff_code_review.md` | OK |
| 5 | 驗證指令 (Verify cmd) | `cat .\temp\diff_code_review.md` | OK |
| 6 | 上下文適合度 (Context Fit) | 符合 Tom 的架構師角色 | OK |
| 7 | 缺口 (Gaps) | 已補齊與 Issue 系統的關聯 | OK |
| 8 | Nyquist 測試覆蓋 | 符合多維度專業對比 | OK |
