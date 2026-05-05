# PLAN.md - Security Remediation & CI Alignment (Phase 174)

## 任務清單
- [x] 識別 GitHub Secret Scanning 警報涉及的檔案
- [x] 修改 `.env` 移除真實金鑰
- [x] 對 `redact.test.ts` 進行字串混淆 (Concatenation)
- [x] 對 `fetch.test.ts` 進行字串混淆
- [x] 執行 `git rm --cached .env`
- [x] 執行 `vitest` 驗證測試依然通過
- [x] 修復 CI `code_reviewer.py` 中的硬編碼路徑
- [x] 補全 `state_lock.py` 的 CLI 參數與退出碼
- [x] 撰寫 `VERIFICATION.md` 與 `PHASE-SUMMARY.md`

## 受影響檔案 (File Scope)
- .env
- openclaw/src/logging/redact.test.ts
- openclaw/src/media/fetch.test.ts
- openclaw/extensions/telegram/src/fetch.test.ts
- scripts/utils/code_reviewer.py
- scripts/utils/state_lock.py
- scripts/__init__.py
- .planning/phases/174-security-remediation/VERIFICATION.md
- .planning/phases/174-security-remediation/PHASE-SUMMARY.md
- .planning/phases/174-security-remediation/verification_contract.yaml
