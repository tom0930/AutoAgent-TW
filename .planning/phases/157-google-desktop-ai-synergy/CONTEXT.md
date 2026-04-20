# Phase 157: Google Desktop AI + pywinauto v2.3 — GUI Control & Vision-Cognitive Upgrade

> **Phase**: 157 | **Status**: Discuss Complete (v3) | **Date**: 2026-04-20
> **Input Artifact**: `tests/autogui.md` (pywinauto + py_inspect 架構全面升級)
> **Supersedes**: Phase 157 v2 (2026-04-19)

---

## 0. 意圖挖掘 (Intent Mining)

Tom 在 Phase 157 v2 基礎上，進一步提供了 `autogui.md` 具體架構升級方案。核心需求：

1. **視覺判斷** → 用 pywinauto UIA 取代脆弱的 pyautogui 座標定位
2. **GUI 控制** → 用 `Application(backend="uia")` + `WindowSpecification` + `wait_until` 做企業級穩定控制
3. **Context Awareness** → 從 Polling 進化到 **UIA Event-Driven** 監聽
4. **其他** → py_inspect 開發效率、Google Desktop App 整合路徑

---

## 1. 現狀痛點分析 (Current Pain Points)

### 1.1 現有 RVA Engine 代碼審計 (`src/core/rva/rva_engine.py`)

| 層面 | 現狀 | 問題 | 嚴重度 |
|:---|:---|:---|:---|
| **GUI 操控** | `pyautogui.click(x, y)` 座標驅動 | DPI/解析度/主題變動即壞 | 🔴 CRITICAL |
| **等待策略** | `time.sleep(0.8)` / `asyncio.sleep(1.2)` | 固定延遲，不確定性高 | 🔴 CRITICAL |
| **UIA 快速路徑** | `_try_uia_fast_path()` 存在但功能薄弱 | 僅搜 Button，無 TreeView/DataGrid | 🟡 MEDIUM |
| **截圖方式** | `pyautogui.screenshot()` + `PrintWindow` | 需獲得焦點，遮擋時不穩 | 🟡 MEDIUM |
| **開發效率** | 手動猜座標 / trial-and-error | 無 Inspector 工具輔助 | 🟡 MEDIUM |

### 1.2 `autogui.md` 提出的解法映射

```
autogui.md 解法          →  對應現有問題
─────────────────────────────────────────────────
pywinauto.Application()  →  取代 pyautogui 座標
WindowSpecification      →  取代 FindWindow + guesswork  
wait_until()             →  取代 time.sleep()
py_inspect               →  取代手動猜 auto_id
UIA Event Hook           →  取代 5 秒 polling
```

---

## 2. 視覺判斷強化 (Visual Judgment Enhancement)

### 2.1 雙眼架構 v2.3 (Dual-Eye with pywinauto Core)

```
┌──────────────────────────────────────────────────────────┐
│  AutoAgent-TW Agent (Phase 157 v2.3)                      │
│                                                            │
│  ┌────────────────────┐   ┌──────────────────────────┐   │
│  │ Eye-0 (Structural) │   │ Eye-1 (Visual)            │   │
│  │ pywinauto UIA       │   │ Local LLM / VisionProxy   │   │
│  │ 直接讀取控制項       │   │ 截圖 + Gemini 解析        │   │
│  │ ~10ms latency       │   │ ~100-500ms latency        │   │
│  │ ★★★★★ 穩定性     │   │ ★★★☆☆ 穩定性           │   │
│  └─────────┬──────────┘   └──────────┬───────────────┘   │
│            │                          │                     │
│            │  ┌───────────────────────┘                     │
│            ▼  ▼                                             │
│  ┌──────────────────┐   ┌──────────────────────────┐      │
│  │ Confidence Gate   │   │ Eye-2 (Authority)         │      │
│  │                   │   │ Google Desktop Lens        │      │
│  │ Eye-0 found? → ✓ │   │ Alt+Space Screen Share     │      │
│  │ Eye-0 miss →Eye-1 │   │ ~2-5s latency              │      │
│  │ Eye-1 < 0.85→Eye2 │   │ 最後手段 / HITL 確認       │      │
│  └──────────────────┘   └──────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

**核心變更**：新增 **Eye-0 (Structural)** 作為最高優先級。pywinauto UIA 能在 **10ms** 內直接讀取控制項文字、狀態、位置，完全不需截圖。

### 2.2 升級後的能力矩陣

| 能力 | Phase 138 (舊) | Phase 157 v2.3 (新) | 增幅 |
|:---|:---|:---|:---|
| **UI 元件辨識** | pyautogui 座標 + Vision fallback | pywinauto UIA 直接讀取 | ★★★★★ |
| **Vivado TreeView** | 截圖猜 → 幻覺風險 | `.TreeView.get_items()` 直接拉文字 | ★★★★★ |
| **Google Overlay** | `sleep(0.8)` 不穩定 | `wait('visible')` 確定性等待 | ★★★★★ |
| **高 DPI 支援** | `SetProcessDpiAwareness` 有但脆弱 | UIA 後端原生支援 | ★★★★☆ |
| **開發效率** | 手寫座標 trial-and-error | py_inspect 點擊 → 自動產生程式碼 | ★★★★★ |

---

## 3. GUI 控制架構 (How to Control)

### 3.1 三層控制策略（更新版）

| 層級 | 方法 | 工具 | 穩定性 | 延遲 | 適用場景 |
|:---|:---|:---|:---|:---|:---|
| **L0: UIA 直接控制** | `WindowSpecification` + `auto_id` | pywinauto (backend="uia") | ★★★★★ | ~10ms | 所有有 UIA 元件的 App |
| **L1: Google Overlay** | `Desktop().window(title_re=...)` + `wait` | pywinauto 穩定呼叫 | ★★★★☆ | ~800ms | Google Desktop App |
| **L2: Vision Fallback** | 截圖 → Gemini/LLM 解析 → 座標點擊 | RVAVisionClient | ★★★☆☆ | ~1-3s | 無 UIA 元件的 legacy App |
| **L3: Gemini Computer Use** | API 直接呼叫 | Google Gen AI SDK | ★★★★★ | ~1-3s | 完全程式化自動化 |

### 3.2 核心升級代碼：PywinautoController

```python
# src/core/rva/gui_control.py (新模組)

from pywinauto import Application, Desktop
from pywinauto.timings import wait_until
import logging

logger = logging.getLogger("RVA.GUIControl")

class PywinautoController:
    """L0/L1 層：pywinauto UIA 控制器"""
    
    def __init__(self, backend: str = "uia"):
        self.backend = backend
    
    # === L0: 通用控制項操作 ===
    
    def find_and_click(self, window_title_re: str, 
                       control_title_re: str = None,
                       auto_id: str = None,
                       control_type: str = None,
                       timeout: float = 5.0) -> bool:
        """用 UIA 精確定位並點擊控制項（取代 pyautogui 座標）"""
        try:
            desktop = Desktop(backend=self.backend)
            win = desktop.window(title_re=window_title_re)
            win.wait('visible', timeout=timeout)
            
            kwargs = {}
            if control_title_re: kwargs['title_re'] = control_title_re
            if auto_id: kwargs['auto_id'] = auto_id
            if control_type: kwargs['control_type'] = control_type
            
            element = win.child_window(**kwargs)
            if element.exists(timeout=timeout):
                element.click_input()
                return True
            return False
        except Exception as e:
            logger.debug(f"UIA click failed: {e}")
            return False

    def read_control_text(self, window_title_re: str,
                          auto_id: str = None,
                          control_type: str = None) -> str:
        """直接讀取控制項文字（不需截圖 + OCR）"""
        try:
            desktop = Desktop(backend=self.backend)
            win = desktop.window(title_re=window_title_re)
            
            kwargs = {}
            if auto_id: kwargs['auto_id'] = auto_id
            if control_type: kwargs['control_type'] = control_type
            
            element = win.child_window(**kwargs)
            return element.window_text() if element.exists(timeout=2) else ""
        except Exception as e:
            logger.debug(f"UIA read failed: {e}")
            return ""
    
    # === L1: Google Desktop App 專用 ===

    def invoke_google_desktop(self, query: str, 
                              use_lens: bool = False) -> bool:
        """穩定呼叫 Google Desktop Overlay（取代 pyautogui.hotkey）"""
        try:
            desktop = Desktop(backend=self.backend)
            
            # 嘗試找已存在的 overlay
            try:
                overlay = desktop.window(
                    title_re=r".*Google.*|Search|Gemini.*",
                    timeout=1
                )
                overlay.wait('visible', timeout=2)
            except Exception:
                # Fallback: 用 pyautogui 觸發 Alt+Space
                import pyautogui
                pyautogui.hotkey('alt', 'space')
                overlay = desktop.window(
                    title_re=r".*Google.*",
                    timeout=5
                )
                overlay.wait('visible', timeout=5)
            
            # 找到 Edit 控制項，輸入查詢
            edit = overlay.child_window(control_type="Edit")
            if edit.exists(timeout=3):
                edit.set_focus()
                edit.set_edit_text(query)
            
            # Lens 模式
            if use_lens:
                lens_btn = overlay.child_window(
                    title_re=r"Lens|視覺搜尋|Screen",
                    control_type="Button"
                )
                if lens_btn.exists(timeout=2):
                    lens_btn.click_input()
            
            # 送出
            overlay.type_keys('{ENTER}')
            
            # 等待回應（用 wait_until 取代 sleep）
            wait_until(10, 0.5, 
                lambda: overlay.child_window(
                    control_type="Text",
                    title_re=r".*"
                ).exists())
            
            return True
        except Exception as e:
            logger.error(f"Google Desktop invoke failed: {e}")
            return False
    
    # === Vivado/Vitis 專用 ===
    
    def get_vivado_tree_items(self) -> list:
        """直接讀取 Vivado Project Explorer TreeView 節點"""
        try:
            app = Application(backend=self.backend).connect(
                title_re=r".*Vivado.*"
            )
            tree = app.window(
                title_re=r".*Project.*"
            ).child_window(control_type="Tree")
            
            if tree.exists(timeout=3):
                return [item.text() for item in tree.get_items()]
            return []
        except Exception as e:
            logger.debug(f"Vivado tree read failed: {e}")
            return []
    
    def get_vivado_errors(self) -> list:
        """讀取 Vivado Messages/Errors DataGrid"""
        try:
            app = Application(backend=self.backend).connect(
                title_re=r".*Vivado.*"
            )
            messages = app.window(
                title_re=r".*Messages.*|.*Errors.*"
            ).child_window(control_type="DataGrid")
            
            if messages.exists(timeout=3):
                return [row.texts() for row in messages.items()]
            return []
        except Exception as e:
            logger.debug(f"Vivado error read failed: {e}")
            return []
```

### 3.3 RVA Engine 升級路徑

```diff
# src/core/rva/rva_engine.py 修改摘要

+ from src.core.rva.gui_control import PywinautoController

  class RVAEngine:
      def __init__(self):
          self.vision_client = RVAVisionClient()
          self.vision_proxy = VisionProxy()
+         self.gui = PywinautoController()  # 新增 L0/L1 控制器
  
      def _try_uia_fast_path(self, target, action_type) -> bool:
-         # 現有：僅搜 Button，功能薄弱
-         element = app.child_window(title_re=f".*{target}.*",
-                                    control_type="Button")
+         # 升級：完整 UIA 搜索 (Button + TreeItem + DataItem + ...)
+         return self.gui.find_and_click(
+             window_title_re=r".*",  # active window
+             control_title_re=f".*{target}.*",
+             timeout=1.0
+         )
```

---

## 4. Context Awareness 優化

### 4.1 從 Polling 到 Event-Driven

**現狀** (`rva_engine.py`): 無主動監控。Agent 完全被動等待用戶指令。

**目標**: UIA Event-Driven → 僅在「有意義的事件」發生時才觸發分析。

```python
# src/core/rva/context_monitor.py (新模組概念)

import comtypes
from pywinauto import Desktop
import logging

logger = logging.getLogger("RVA.ContextMonitor")

class ContextMonitor:
    """Event-Driven 情境監控器"""
    
    def __init__(self):
        self.handlers = {}
    
    def register_window_change_handler(self, callback):
        """監聽焦點視窗變化"""
        self.handlers['focus_change'] = callback
    
    def poll_smart(self, interval: float = 2.0):
        """
        Smart Polling: 用 pywinauto wait_until 取代 sleep-loop。
        只在狀態真正變化時才觸發 callback。
        
        Note: 完整 UIA Event Hook 需要 comtypes + IUIAutomation,
        此處先用 pywinauto 原生 wait 作為穩定替代。
        """
        desktop = Desktop(backend="uia")
        last_title = ""
        
        while True:
            try:
                current = desktop.active_window()
                title = current.window_text() if current else ""
                
                if title != last_title:
                    last_title = title
                    if 'focus_change' in self.handlers:
                        self.handlers['focus_change'](title)
                
                import time
                time.sleep(interval)
            except Exception as e:
                logger.debug(f"Monitor cycle error: {e}")
```

### 4.2 多源情境融合（更新版）

| 情境來源 | 提供者 | 資訊類型 | 觸發方式 |
|:---|:---|:---|:---|
| **控制項狀態** | pywinauto UIA (Eye-0) | 按鈕文字、TreeView 節點、DataGrid 行 | **即時讀取** (~10ms) |
| **視窗焦點** | ContextMonitor | 當前 active window title | **Event-Driven** |
| **螢幕像素** | VisionProxy (Eye-1) | UI 佈局、顏色狀態 | **On-demand** |
| **語意理解** | Google Lens (Eye-2) | 品牌辨識、型號查找 | **升級觸發** |
| **外部知識** | Gemini API (L3) | 錯誤碼含義、最佳實踐 | **On-demand** |
| **歷史記憶** | MemPalace | 過往決策、已知問題 | **自動注入** |

---

## 5. 其他整合機會 (Additional)

### 5.1 py_inspect 開發工作流

```bash
# 一鍵啟動 Inspector
pip install pywinauto[inspect] PyQt5
python -m pywinauto.inspector

# 工作流：
# 1. 打開目標 App (Vivado / Google Desktop / Docklight)
# 2. py_inspect 中點擊目標元件
# 3. 右側顯示 title / class_name / auto_id / control_type
# 4. 點「Copy Code」→ 直接貼入 gui_control.py
```

### 5.2 注意事項（來自研究）

> [!IMPORTANT]
> **py_inspect 是原型工具**。生產環境建議優先用 Microsoft `Inspect.exe` (Windows SDK)。
> `Inspect.exe` 需切到 UIA 模式才能看到 pywinauto 可用的屬性。

> [!WARNING]
> **pywinauto 不原生支援 Event Hook**。
> `wait()` / `wait_not()` 是官方推薦的同步方式，
> 真正的 UIA Event subscription 需 `comtypes` + `IUIAutomation`。
> Phase 157 先用 Smart Polling，後續可升級。

### 5.3 Chrome Skills / Auto Browse / Generative UI

(維持 v2 版本內容不變 — 詳見 Section 4 of v2)

---

## 6. 資安威脅建模 (STRIDE Analysis)

| 威脅 | 描述 | 風險 | 緩解 |
|:---|:---|:---|:---|
| **S** | 假 Overlay 竊取憑證 | 🔴 | 驗證進程簽章 + HITL |
| **T** | 惡意 UI 注入誤導 Agent | 🟡 | Eye-0/Eye-1 交叉驗證 |
| **R** | Agent 操作無法追溯 | 🟡 | rva_audit + MemPalace 日誌 |
| **I** | 截圖含敏感資料上傳 | 🔴 | Zone 分類 + 敏感區域遮罩 |
| **D** | API Rate Limit 卡死 | 🟡 | Eye-0 本地優先 + 429 降級 |
| **E** | Computer Use API 權限提升 | 🔴 | Sandbox + 最小權限 |

> [!CAUTION]
> **pywinauto UIA 可讀取任何視窗的文字** — 包含密碼欄位。
> 必須在 gui_control.py 中加入 **Sensitive Control Blacklist**，
> 禁止讀取 `PasswordBox` / `PasswordEdit` 類型控制項。

---

## 7. 架構選型最終決策

### ✅ 推薦方案：「pywinauto UIA Core + Dual-Eye Fallback」

```
日常 GUI 操控 → Eye-0 (pywinauto UIA)        [~10ms, 最穩定]
Eye-0 找不到元件 → Eye-1 (Vision + LLM)     [~100-500ms]
Eye-1 信心度 < 0.85 → Eye-2 (Google Lens)   [~2-5s, 權威確認]
完全程式化場景 → L3 (Gemini Computer Use API) [~1-3s]
敏感操作 → HITL 確認 (Phase 153 合約引擎)
```

### 新模組清單

| 檔案 | 用途 | 優先級 |
|:---|:---|:---|
| `src/core/rva/gui_control.py` | **[NEW]** PywinautoController 核心 | P0 |
| `src/core/rva/context_monitor.py` | **[NEW]** Event-Driven 情境監控 | P1 |
| `src/core/rva/rva_engine.py` | **[MODIFY]** 整合 gui_control | P0 |

---

## 8. DoD (Definition of Done) — 最終版

- [ ] **DOD-0**: 安裝 `pywinauto[inspect]` + `PyQt5` 到 aa venv
- [ ] **DOD-1**: 用 py_inspect / Inspect.exe 驗證 Google Desktop Overlay 的 UIA 元件
- [ ] **DOD-2**: 完成 `gui_control.py` 模組 (find_and_click + read_control_text + invoke_google_desktop)
- [ ] **DOD-3**: 完成 `rva_engine.py` 升級 (整合 PywinautoController，替換 pyautogui 路徑)
- [ ] **DOD-4**: 用 pywinauto 重寫 Vivado 至少 2 個場景 (TreeView + Error DataGrid)
- [ ] **DOD-5**: 完成 `context_monitor.py` Smart Polling 原型
- [ ] **DOD-6**: 新增 Sensitive Control Blacklist (防止讀取密碼欄位)
- [ ] **DOD-7**: 端到端驗證：Google Desktop Overlay 查詢 → 結果回收 → Dual-Eye 判斷
- [ ] **DOD-8**: 端到端驗證：FPGA 電路圖辨識場景

---

## 9. 編排策略 (Orchestration)

### Wave 並行化可行

```
Wave 1 (基礎)：DOD-0 + DOD-1 (安裝 + Inspector 驗證)
Wave 2 (核心)：DOD-2 + DOD-3 (gui_control + rva_engine 升級) [可並行]
Wave 3 (擴展)：DOD-4 + DOD-5 (Vivado 場景 + Context Monitor)
Wave 4 (驗證)：DOD-6 + DOD-7 + DOD-8 (安全 + E2E 測試)
```
