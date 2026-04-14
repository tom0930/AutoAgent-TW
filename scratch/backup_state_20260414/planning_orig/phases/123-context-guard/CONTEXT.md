# Phase 123: Active Context Defense (ACD) — Token 爆炸根因分析與防禦設計

## 🔍 問題重述
在 `z:\ac` (OpenClaw 工作區) 開啟 Antigravity 執行 `/aa-plan` 或任何 `/aa-` 命令時，
頻繁觸發 **Max Token Limit Error**，導致 Agent 無法正常工作。

---

## 📊 Phase 123 資料蒐集結果

### 工作區掃描統計 (`z:\ac`)

| 指標 | 數值 | 評估 |
|:---|:---|:---|
| 總檔案數 | **16,888** | ❌ 極大 |
| 總容量 | **512.25 MB** | ❌ 不可能全部送入 Context |
| >500KB 檔案總和 | **274.06 MB** | ❌ 佔 53%，全是二進位/編譯檔 |
| 真正原始碼（.md/.py/.ts/.js/.json/.yaml, <1MB, 排除 vendor/venv/node_modules） | **12.84 MB / 1,420 檔** | ⚠️ 仍然偏大但可管控 |

### 前 5 大地雷檔案

| 檔名 | 大小 | 性質 |
|:---|:---|:---|
| `cli.js.map` | **57 MB** | Source Map（編譯產物） |
| `chromadb_rust_bindings.pyd` | **56.7 MB** | Python 二進位（venv 內） |
| `libscipy_openblas64_.dll` | **19.5 MB** | 數學庫 DLL（venv 內） |
| `onnxruntime_pybind11_state.pyd` | **15.7 MB** | ML Runtime（venv 內） |
| `cli.js` | **12.4 MB** | Bundled CLI（編譯產物） |

---

## 🎯 根因分析 (Root Cause Analysis)

### ❌ 直接原因：`z:\ac` 沒有 `.geminiignore`

```
.gitignore     → ✅ 存在（有 cli.js, venv/ 規則）
.claudeignore  → ✅ 存在（有完整排除規則）
.geminiignore  → ❌ 完全不存在
```

**Antigravity 使用 `.geminiignore` 來決定索引範圍**，而不是 `.claudeignore`。
由於 `.geminiignore` 不存在，Antigravity 的 Context Indexer 會嘗試掃描全部 16,888 個檔案（512 MB），
在建立 workspace map 的階段就直接撞上 Token 上限。

### ⚠️ 間接原因 1：`mcp-server/venv/` 未被排除
- venv 內含 chromadb、onnxruntime、numpy 等重量級套件
- 單一 `chromadb_rust_bindings.pyd` = 56.7 MB
- 這些二進位檔即使不被「讀取」，光是檔案 listing 本身就消耗大量 Token

### ⚠️ 間接原因 2：`vendor/` 目錄包含多平台 ripgrep
- 6 個平台的 `rg` 執行檔合計 ~26 MB
- 完全不需要出現在 AI 的上下文中

### ⚠️ 間接原因 3：ROADMAP.md 歷史累積
- 已完成的 Phase 1~122 全部堆在 ROADMAP.md
- 每次啟動 `/aa-plan` 都會完整讀取，浪費寶貴 Token

---

## 🛡️ 設計決策：Active Context Defense (ACD) 架構

### 決策 1：即時修復 — 建立 `.geminiignore`

**選擇方案**：直接在 `z:\ac` 建立 `.geminiignore`，內容與 `.claudeignore` 同步並強化。

這是 **最小成本、最大效益** 的即時修復。不需要任何程式碼變更。

### 決策 2：長期防護 — Context Guard 整合到 AA 核心

| 方案 | 實施方式 | 優點 | 缺點 |
|:---|:---|:---|:---|
| **A. Pre-scan Guardrail** | 在 `/aa-plan` Step 1 前插入檔案掃描 | 主動防禦、零遺漏 | 需修改所有 workflow |
| **B. `.geminiignore` 自動生成器** | `context_guard.py` 掃描後自動產生 ignore 檔 | 一次執行、持久生效 | 需使用者手動觸發 |
| **C. Token Budget Monitor** | Dashboard 即時顯示 Token 用量比 | 視覺化預警 | 只是告警，不防止爆炸 |

**推薦**：**A + B 組合**
- 首次進入專案時（`/aa-new-project`）自動執行 B 生成 ignore 檔
- 每次 `/aa-plan` 執行前自動執行 A 做前置檢查

### 決策 3：ROADMAP 瘦身策略

| 方案 | 內容 |
|:---|:---|
| **歸檔機制** | Phase 狀態改為 ✅ 後，Wave 細節自動移至 `.planning/HISTORY.md` |
| **摘要化** | ROADMAP 中已完成 Phase 只保留一行摘要，不保留 Wave 明細 |

---

## 額外更好機制：Dynamic Context Pruning（進階）

每次 /aa- 命令前，讓 Agent 先執行一個輕量「context audit」工具：
計算預估 tokens（可用簡單規則：原始碼行數 × 平均 tokens/行 + 大檔 penalty）。
若預估 > 60% context window → 自動優先載入「當前 Phase 相關檔案 + ROADMAP 摘要」，其他用 RAG-like 方式 on-demand 檢索。

好處：即使 ignore 檔漏掉某些東西，也不會直接爆炸。

# 當偵測到 Token 即將或已經超過時（例如 workspace indexing 階段預估 > 100K tokens，或直接收到 Max Token Limit Error）：

立即提示使用者（Friendly Alert）：text⚠️ Active Context Defense 觸發警告
檢測到 workspace context 預估 tokens 過高（~XXXK tokens），即將超過模型限制。

可能原因：
- .geminiignore 缺失或不完整
- 大型二進位檔 / 歷史檔案未排除
- ROADMAP.md 或其他單一檔案過大

建議立即執行：
1. 確認 z:\ac\.geminiignore 已建立並包含 venv/、vendor/、*.pyd 等規則
2. 執行 /aa-context-audit 查看詳細報告
3. 若已建立 ignore，仍爆炸 → 請回報詳細 log


## 🔧 即時修復行動 (Immediate Fix)

### Step 1: 為 `z:\ac` 建立 `.geminiignore`

```
# === AutoAgent-TW Context Guard ===
# Prevent Antigravity from indexing non-source files

# Build Artifacts
cli.js
cli.js.map

# Dependencies & Virtual Environments
node_modules/
vendor/
venv/
.venv/
__pycache__/
*.pyc

# Binary & Large Files
*.pyd
*.dll
*.exe
*.so
*.dylib
*.whl
*.egg
*.tar.gz
*.zip

# Logs & Temp
*.log
*.tmp
*.sqlite
temp/

# IDE & OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Maps & Compiled
*.js.map
*.min.js
*.min.css

# Build Output
dist/
build/
```

### Step 2: ROADMAP 歸檔（可選）

將 Phase 1~122 的 Wave 細節移至 `HISTORY.md`，ROADMAP 只保留一行摘要。

---

## 📐 Token 預估（修復前後）

| 場景 | 預估 Context Token | 結果 |
|:---|:---|:---|
| **修復前**（無 .geminiignore） | ~800K+ tokens | ❌ 爆炸 |
| **修復後**（有 .geminiignore） | ~30K-50K tokens | ✅ 安全 |
| **修復後 + ROADMAP 瘦身** | ~15K-25K tokens | ✅ 最佳 |

---

## ✅ 結論

**Token 爆炸的根因就是 `z:\ac` 缺少 `.geminiignore`**。

Antigravity 不讀 `.claudeignore`，它只認 `.geminiignore`。
建立這個檔案後，問題會立即消失。

長期而言，AutoAgent-TW 應在 `/aa-new-project` 流程中
自動生成 `.geminiignore`（與 `.claudeignore` 一起），
作為 Active Context Defense 標準流程的一環。



# === AutoAgent-TW Active Context Defense (ACD) ===
# Antigravity / Gemini 專用 ignore（優先於 .gitignore）
# 目的：將 context 壓到 15K~40K tokens 以內，避免 Max Token Limit Error

# === 高風險建置產物與二進位檔 ===
cli.js
cli.js.map
*.min.js
*.min.css
*.js.map
dist/
build/

# === 依賴與虛擬環境（最重地雷）===
node_modules/
vendor/
venv/
.venv/
__pycache__/
*.pyc
*.pyd
*.dll
*.so
*.dylib
*.exe
*.whl
*.egg

# === 大型或非必要目錄 ===
.mcp-server/venv/          # 你提到的 chromadb 等重量級套件
temp/
logs/
*.log
*.sqlite
*.db

# === IDE、OS 與快取 ===
.vscode/
.idea/
.DS_Store
Thumbs.db
*.tmp

# === 歷史與規劃檔案（避免 ROADMAP 爆炸）===
# 建議：已完成 Phase 的詳細 Wave 移至 .planning/HISTORY.md
# ROADMAP.md 只保留目前進行中的 Phase 摘要

# === 其他大型非原始碼 ===
*.tar.gz
*.zip
*.rar
*.pdf
*.png
*.jpg
*.jpeg
*.gif
*.svg  # 若非必要