# GSD PLAN: Phase 159.2 - Security Hardening & Documentation (v2.1)

## 1. 執行拆解 (Plan Details)

| 步驟 | 說明 | 影響檔案 |
| :--- | :--- | :--- |
| **1. 擴充威脅模型表** | 更新 `SECURITY.md` 內的 STRIDE 表格，加入 LSP DoS 與 Tampering 的相關說明。 | `SECURITY.md` |
| **2. 插入新章節** | 在 Protective Measures 和 Installer Security 之間，插入 "Runtime Resource & Extension Hardening" 章節，詳細說明 Stealth Mode 機制。 | `SECURITY.md` |
| **3. 狀態更新** | 更新 `STATE.md` 紀錄 Phase 159.2 狀態。 | `.planning/STATE.md` |

## 2. UAT 驗收準則 (Acceptance Criteria)
- [ ] `SECURITY.md` 正確反映了 Phase 158.5 所做出的 `exe.disabled` 防禦策略。
- [ ] 威脅矩陣中明確定義了避免資源耗盡與競爭狀態的安全防禦規則。
- [ ] 文件架構無損，且 Markdown 渲染正確。
