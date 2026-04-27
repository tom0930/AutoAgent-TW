Viewed SKILL.md:1-20

好的！你問的核心問題是：**「當有 bug、有問題時，你是如何解決問題的？」**

從我 20 年架構師的實戰經驗，加上 AutoAgent-TW 框架的 GSD 哲學，我有一套**系統化的 Bug 解決方法論**，完全不靠感覺拍腦袋。

---

## 🧠 我的 Bug 解決框架（5 層診斷法）

### **Layer 0：現象定性 → 先分類，再動手**

```
Bug 類型判斷：
├── 邏輯錯誤   → 程式碼流程錯誤、算法缺陷
├── 資料錯誤   → 輸入格式/邊界值/Null/encoding 問題
├── 時序錯誤   → Race condition、async 順序、鎖死
├── 環境錯誤   → 版本不符、路徑、env 變數、依賴缺失
└── 架構錯誤   → 設計本身有缺陷（最貴，需重構）
```

> **「80% 的 bug 在第一層就能定性」** — 定性錯，後面白忙活。

---

### **Layer 1：重現 → 最小可重現案例（MRE）**

```python
# ✅ 正確做法：先隔離 bug 邊界
def minimal_repro():
    """把 500 行的 bug 縮成 10 行可重現"""
    # 只保留能觸發問題的最小代碼
    pass
```

我的口訣：**「能重現的 bug 才是真 bug，不能重現的是幽靈」**

---

### **Layer 2：三視角並行思考（Multi-Agent CoT）**

每次遇到 bug，我內部強制啟動 **3 個 Agent 視角**同時思考：

| Agent 視角              | 問的問題                                    |
| ----------------------- | ------------------------------------------- |
| 🏗️**架構師**    | 設計上有沒有根本缺陷？是否需要重構？        |
| 🔒**資安工程師**  | 這個 bug 有沒有安全漏洞？STRIDE 哪個維度？  |
| 🤖**AI 產品專家** | 這個問題是否影響用戶體驗？有無 workaround？ |

---

### **Layer 3：診斷工具鏈（依 bug 類型選擇）**

```bash
# Python 環境類
python -m py_compile src/core/*.py    # 語法快速驗證
python -c "import traceback; traceback.print_exc()"

# 邏輯類 → 加 debug 日誌
import logging; logging.basicConfig(level=logging.DEBUG)

# 型別類 → Pyrefly / mypy
mypy src/core/ --strict

# 依賴/環境類
pip list | grep <pkg>
python -c "import sys; print(sys.path)"

# AutoAgent-TW 專屬
python scripts/preflight_gate.py --check
python scripts/preflight_gate.py --files src/core/XXX.py
```

---

### **Layer 4：修復三原則（來自 AGENTS.md）**

> [!IMPORTANT]
> AutoAgent-TW 的鐵律：**Repair, not Reset（修復而非重建）**

1. **精準外科手術** — 只改有問題的地方，不大改動
2. **加迴歸測試** — 每個 bug fix 必須加一個對應測試，防止復發
3. **Commit 原子化** — 一個 fix 一個 commit，便於 `git bisect` 追蹤

---

### **Layer 5：根因分析 + 預防（SOP 化）**

修好之後，我必問自己：

```
5 Whys 分析：
Why 1: 為什麼會發生這個 bug？
Why 2: 為什麼沒在之前測試中被發現？
Why 3: 為什麼測試覆蓋率不夠？
Why 4: 為什麼沒有邊界值測試？
Why 5: 為什麼設計文件沒有明確定義邊界？

→ 根因：[設計文件缺失] → 更新 CONTEXT.md + 補測試
```

---

## 🛠️ 在 AutoAgent-TW 框架中的實際流程

```
Bug 發生
  ↓
[/aa-fix] 自我修復循環
  ├── Step 1: 讀 QA-REPORT.md 定位失敗點
  ├── Step 2: 三視角並行診斷
  ├── Step 3: 精準修復（最多 3 輪）
  ├── Step 4: py_compile + preflight_gate 驗證
  └── Step 5: 原子 commit + 更新 STATE.md

[/aa-guard] 安全掃描（資安類 bug）
  ├── STRIDE 威脅分析
  ├── Memory/Buffer 安全檢查
  └── 建立 checkpoint 備份
```

---

## 💡 你問的場景（你當前正在看的檔案）

注意到你目前開著：

- `generate_final_01_ledger.py` (InvoiceAI)
- `preflight_gate.py` (AutoAgent-TW)
- `security/__init__.py`

**如果你現在有具體 bug**，告訴我：

1. 錯誤訊息 / stack trace
2. 期望行為 vs 實際行為

我會直接啟動診斷，給你 **根因 + 修復代碼 + 預防 SOP**。
