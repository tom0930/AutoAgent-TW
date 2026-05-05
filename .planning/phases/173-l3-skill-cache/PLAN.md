# Phase 173 PLAN: L3 Skill Cache — 自動技能發現與生命週期管理

> **Phase**: 173 | **版本**: v3.6.3 | **狀態**: Plan Ready
> **來源**: CONTEXT.md v2.1 (Merged)

---

## 8 維度檢查表

| # | 維度 | 檢查結果 |
|---|------|----------|
| 1 | **需求拆解** | ✅ 4 子階段：核心引擎 → Workflow 整合 + Traceability → 品質報表 → 未來優化 |
| 2 | **技術選型** | ✅ Python CLI (argparse + pathlib)，JSON index，Git Trailers (標準格式) |
| 3 | **架構圖** | ✅ L1→L2→L3 三級快取 + Content Sanitizer + Quality Feedback Loop |
| 4 | **並行設計** | ✅ build_l3_index.py 使用 ThreadPoolExecutor (每 repo 限 2.5s timeout) |
| 5 | **資安威脅** | ✅ STRIDE 完成：Sanitizer 黑名單 + SHA-256 Hash + Quarantine + 白名單 repo |
| 6 | **AI 考量** | ✅ Token 注入上限 2,000，Eager Eviction，[L3 Cache HIT] 透明通知 |
| 7 | **錯誤處理** | ✅ Index miss → FS fallback，Clone fail → retry，Sanitizer block → 次佳匹配 |
| 8 | **測試策略** | ✅ py_compile + CLI 冒煙測試 + Sanitizer 攔截驗證 + Hash 篡改偵測 |

---

## Wave 執行計畫

### Wave 1：配置與索引建置基礎

#### Task 1.1: `config/l3_config.json`

**目標**: 建立可配置的 L3 路徑與 repo 清單

**變更檔案**:
- `[NEW] config/l3_config.json`

**具體步驟**:
1. 建立 JSON 結構：`l3_cache_root`, `repos[]`, `search{}`, `security{}`
2. 預填 5 個已知 repo (含 URL + priority + enabled flag)
3. 加入 search 參數：`timeout_seconds: 5`, `max_results: 5`, `score_threshold: 0.6`
4. 加入 security 參數：`enable_content_sanitizer: true`, `hash_verification: true`

**UAT**: `python -c "import json; json.load(open('config/l3_config.json'))"` → exit 0

---

#### Task 1.2: `scripts/build_l3_index.py`

**目標**: 遍歷所有 L3 repo，產出統一 `l3_master_index.json`

**變更檔案**:
- `[NEW] scripts/build_l3_index.py`
- `[NEW] data/l3_master_index.json` (產出)

**具體步驟**:
1. 讀取 `config/l3_config.json` 取得 repo 清單與 root path
2. 遍歷每個 enabled repo，掃描所有 `SKILL.md`
3. 解析 YAML frontmatter：`name`, `description`, `category`, `tags`, `risk`
4. 計算 `content_hash` (SHA-256)，估算 `token_count` (len/4)
5. 組裝為統一格式，寫入 `data/l3_master_index.json`
6. 支援 `--root <path>` 覆蓋 config 預設路徑
7. Content Sanitizer：掃描 9 種危險 pattern，標記 risk level

**UAT**:
- `python scripts/build_l3_index.py --root D:\git` → exit 0
- `python -c "import json; d=json.load(open('data/l3_master_index.json')); print(len(d['entries']))"` → 輸出 > 5000

---

### Wave 2：核心搜尋引擎

#### Task 2.1: `scripts/l3_skill_cache.py`

**目標**: L3 技能搜尋 CLI，支援 search / read / sources / rebuild-index

**變更檔案**:
- `[NEW] scripts/l3_skill_cache.py`

**具體步驟**:
1. 實作 `L3SkillCache` 類別：
   - `__init__`: 載入 config + master index
   - `search(query, top_k=5)`: keyword tokenize → name/desc/tags 匹配 → 排序
   - `read(skill_path)`: 讀取並返回 SKILL.md 內容
   - `list_sources()`: 列出所有可用 L3 repo 狀態
   - `rebuild_index()`: 呼叫 build_l3_index.py 邏輯
2. CLI 模式 (argparse):
   - `--search <query>` → JSON 輸出匹配結果
   - `--read <path>` → 輸出 SKILL.md 全文
   - `--sources` → 列表所有 repo
   - `--rebuild-index` → 重建索引
3. 搜尋演算法:
   - 精確名稱匹配 (score × 2.0)
   - 部分名稱匹配 (score × 1.5)
   - description 關鍵字匹配 (score × 1.0)
   - tags 匹配 (score × 1.2)
   - category 匹配 (score × 0.8)
4. 載入時 Hash 驗證：比對 index 中的 `content_hash`
5. Risk 過濾：`blocked` 等級直接跳過

**UAT**:
- `python scripts/l3_skill_cache.py --search "fastapi"` → 輸出 JSON，latency < 1s
- `python scripts/l3_skill_cache.py --search "kubernetes"` → 至少 1 筆結果
- `python scripts/l3_skill_cache.py --sources` → 列出 ≥ 4 個 repo

---

### Wave 3：Installer 整合

#### Task 3.1: 更新 `scripts/aa_installer_logic.py`

**目標**: 新增 `--with-l3-cache` + `--l3-path` 參數，自動 git clone

**變更檔案**:
- `[MODIFY] scripts/aa_installer_logic.py`

**具體步驟**:
1. 新增 argparse 參數：`--with-l3-cache`, `--l3-path <dir>`
2. 新增 `deploy_l3_cache(target_dir, l3_path, with_l3)` 函式：
   - 建立 l3_path 目錄
   - 從 config/l3_config.json 讀取 repo 清單
   - 對每個 repo 執行 `git clone --depth 1 <url> <l3_path>/<name>`
   - Clone 失敗重試 1 次
   - 成功後呼叫 build_l3_index.py 產出 master index
3. 將 l3_path 寫入 `config/l3_config.json` 的 `l3_cache_root`
4. 在 main() 中的 Step 4 (OpenClaw) 之後呼叫

**UAT**:
- `python scripts/aa_installer_logic.py --help` → 顯示 `--with-l3-cache` 參數
- `python -m py_compile scripts/aa_installer_logic.py` → exit 0

---

### Wave 4：Traceability 系統

#### Task 4.1: `scripts/l3_trace_hook.py`

**目標**: Git commit trailer 注入 + fix 關聯分析

**變更檔案**:
- `[NEW] scripts/l3_trace_hook.py`
- `[NEW] data/l3_skill_ledger.jsonl` (運行時產出)

**具體步驟**:
1. `inject_trailer(commit_msg, skill_id, repo, score, hash)`:
   - 使用 `git interpret-trailers` 注入 L3-Skill/L3-Repo/L3-Score/L3-Hash
   - 同時寫入 `l3_skill_ledger.jsonl` 一筆 `{"event": "used", ...}` 記錄
2. `correlate_fix(commit_hash)`:
   - 解析 commit message，偵測 `fix`/`bug`/`hotfix`/`revert`
   - 取得修改的檔案清單
   - 從近 30 天的 git log 中找出包含 L3-Skill trailer 的 commit
   - 計算檔案重疊率 × 時間接近度 = 關聯分數
   - 寫入 ledger 一筆 `{"event": "correlated_fix", ...}` 記錄
   - 返回關聯結果
3. CLI 模式:
   - `--inject --skill <id> --repo <name> --score <float>`
   - `--correlate <commit_hash>`
   - `--report` → 品質統計報表

**UAT**:
- `python -m py_compile scripts/l3_trace_hook.py` → exit 0
- `python scripts/l3_trace_hook.py --help` → 顯示所有模式

---

#### Task 4.2: `l3_skill_cache.py` 新增 `--report`

**目標**: 品質統計報表功能

**變更檔案**:
- `[MODIFY] scripts/l3_skill_cache.py`

**具體步驟**:
1. 新增 `--report` CLI 模式
2. 讀取 `data/l3_skill_ledger.jsonl`
3. 統計每個 skill_id：使用次數、fix 關聯次數、平均 score
4. 計算 `quality_score` 公式：
   ```
   0.4 * success_rate + 0.3 * avg_score + 0.2 * log(usage) + 0.1 * recency - 0.5 * fix_rate
   ```
5. 輸出 Rich Table 報表 (Skill / Uses / Fixes / Quality / Action)
6. Quality 分級：≥0.85 建議升級 L2 / <0.40 加入黑名單

**UAT**:
- `python scripts/l3_skill_cache.py --report` → 正常輸出（即使 ledger 為空顯示「無數據」）

---

### Wave 5：Workflow 整合 + Bridge 更新

#### Task 5.1: 更新 Antigravity Bridge SKILL.md

**目標**: 整合 L3 搜尋指令到現有 Bridge 技能

**變更檔案**:
- `[MODIFY] C:\Users\TOM\.gemini\antigravity\skills\antigravity-awesome-bridge\SKILL.md`

**具體步驟**:
1. 新增 L3 三級快取說明 (L1 → L2 → L3)
2. 新增搜尋指令：`python scripts/l3_skill_cache.py --search "<query>"`
3. 新增 auto-eviction 行為說明
4. 新增 `[L3 Cache HIT]` 通知格式

**UAT**: 檔案語法正確，frontmatter 完整

---

#### Task 5.2: Workflow 修改

**目標**: 在 aa-discuss2 / aa-execute / aa-ship / aa-fix 中加入 L3 hooks

**變更檔案**:
- `[MODIFY] _agents/workflows/aa-discuss2.md` — 新增 Step 2.7 (L3 Discovery)
- `[MODIFY] _agents/workflows/aa-ship.md` — 新增 L3 Trailer commit step
- `[MODIFY] _agents/workflows/aa-fix.md` — 新增 L3 correlation check

**具體步驟**:
1. `aa-discuss2.md`: 在 Step 2.6 後新增：
   ```markdown
   ### Step 2.7: L3 Skill Discovery (Auto)
   1. 如果當前任務關鍵字在 L1/L2 無匹配，執行:
      `python scripts/l3_skill_cache.py --search "<task keywords>"`
   2. 如果找到匹配，自動讀取 SKILL.md 並通知用戶
   3. 任務完成後 L3 內容不保留
   ```
2. `aa-ship.md`: 在 Step 3 commit 前加入 L3 Trailer 注入
3. `aa-fix.md`: 在 Step 1 讀取錯誤報告後加入 L3 correlation check

**UAT**: 所有 workflow .md 檔案語法正確

---

## 驗證計畫 (Verification Plan)

### 自動化測試

```bash
# 1. 所有 Python 檔案編譯通過
python -m py_compile scripts/l3_skill_cache.py
python -m py_compile scripts/build_l3_index.py
python -m py_compile scripts/l3_trace_hook.py
python -m py_compile scripts/aa_installer_logic.py

# 2. Index 建置
python scripts/build_l3_index.py --root D:\git

# 3. 搜尋功能
python scripts/l3_skill_cache.py --search "fastapi"
python scripts/l3_skill_cache.py --search "kubernetes"
python scripts/l3_skill_cache.py --sources

# 4. 報表功能
python scripts/l3_skill_cache.py --report

# 5. Trace hook
python scripts/l3_trace_hook.py --help

# 6. Preflight Gate
python scripts/preflight_gate.py --check
```

### 手動驗證

- [ ] Installer 顯示 `--with-l3-cache` 選項
- [ ] 搜尋延遲 < 1 秒
- [ ] Sanitizer 能攔截包含 `eval()` 的 SKILL.md
- [ ] Dashboard 正常運行

---

## 檔案變更總覽

| 檔案 | 操作 | Wave |
|------|------|------|
| `config/l3_config.json` | NEW | 1 |
| `scripts/build_l3_index.py` | NEW | 1 |
| `data/l3_master_index.json` | NEW (產出) | 1 |
| `scripts/l3_skill_cache.py` | NEW | 2 |
| `scripts/aa_installer_logic.py` | MODIFY | 3 |
| `scripts/l3_trace_hook.py` | NEW | 4 |
| `data/l3_skill_ledger.jsonl` | NEW (運行時) | 4 |
| `antigravity-awesome-bridge/SKILL.md` | MODIFY | 5 |
| `_agents/workflows/aa-discuss2.md` | MODIFY | 5 |
| `_agents/workflows/aa-ship.md` | MODIFY | 5 |
| `_agents/workflows/aa-fix.md` | MODIFY | 5 |
