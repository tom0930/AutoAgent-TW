**✅ 在 aa-TW（autoagent-TW）中加入 Graphify CLI 呼叫的完整教學**

由於 aa-TW 基於 **HKUDS/AutoAgent**（零碼 / 自然語言驅動框架），加入外部 CLI 工具主要有兩種推薦方式：

### 推薦方式 1：使用自然語言直接讓 Agent Editor 建立工具（最簡單，符合 aa-TW 設計理念）

這是最適合 aa-TW 的方式，幾乎不用改程式碼。

**步驟：**

1. 啟動 aa-TW（`auto main` 或你的啟動指令）。
2. 進入 **Agent Editor** 模式。
3. 告訴 Agent 建立一個新工具，例如：

> 「建立一個名為 `build_graphify` 的工具，功能是執行 Graphify CLI 來為目前專案建立知識圖譜。
> 工具描述：使用 graphify CLI 為指定目錄建立知識圖譜，輸出 graph.html、GRAPH_REPORT.md 和 graph.json。
> 參數：path（字串，必填，預設 '.'）、mode（字串，可選：normal/deep/update）、no_viz（布林，可選）。
> 執行指令使用 subprocess 呼叫 shell：graphify {path} --mode {mode} ...」

4. Agent 會自動生成工具定義，你確認後即可使用。
5. 在後續 Agent 或 Workflow 中直接呼叫這個工具。

**優點**：完全符合 aa-TW 的零碼精神，Agent 自己維護工具。

### 推薦方式 2：手動新增 Shell Tool（更穩定、可控）

如果你希望更精準控制，建議手動加一個 Shell Executor 工具。

**具體步驟：**

1. **先安裝 Graphify**（在你的環境或 Docker container 中執行）：

   ```bash
   uv tool install graphifyy && graphify install
   # 或
   pipx install graphifyy && graphify install
   ```
2. 在 aa-TW 的 **tool 定義目錄**（通常在 `tools/` 或 `custom_tools/` 資料夾）新增一個 Python 檔案，例如 `tool_graphify.py`：

```python
from AutoAgent.tools.base import BaseTool
import subprocess
from typing import Optional

class GraphifyTool(BaseTool):
    name = "graphify_build"
    description = "使用 Graphify 為專案建立知識圖譜，大幅提升 Agent 對大型 codebase 的理解能力"
    parameters = {
        "path": {"type": "string", "description": "要分析的目錄路徑，預設當前目錄", "default": "."},
        "mode": {"type": "string", "description": "模式：normal / deep / update", "default": "normal"},
        "no_viz": {"type": "boolean", "description": "是否跳過生成 graph.html", "default": False}
    }

    def _run(self, path: str = ".", mode: str = "normal", no_viz: bool = False):
        cmd = ["graphify", path]
        if mode == "deep":
            cmd.append("--mode")
            cmd.append("deep")
        if mode == "update":
            cmd.append("--update")
        if no_viz:
            cmd.append("--no-viz")
      
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=path, timeout=300)
            return f"Graphify 執行完成！\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        except Exception as e:
            return f"Graphify 執行失敗: {str(e)}"
```

3. 在 aa-TW 的工具註冊檔案中引入這個 tool（通常是 `tools/__init__.py` 或 agent 初始化處加入）。
4. 重啟 aa-TW 後即可在 Agent 中使用。

### 比較表：兩種方式優缺點

| 方式                      | 難度   | 穩定性 | 可控性 | 適合情境               | 推薦指數   |
| ------------------------- | ------ | ------ | ------ | ---------------------- | ---------- |
| 自然語言 Agent Editor     | ★☆☆ | 中     | 中     | 快速測試、零碼愛好者   | ★★★★★ |
| 手動新增 Python Tool      | ★★☆ | 高     | 高     | 生產環境、大型 TW 專案 | ★★★★★ |
| 直接 subprocess 在 prompt | ★☆☆ | 低     | 低     | 臨時實驗               | ★★☆☆☆ |

### 額外進階建議

- **自動建圖**：建立另一個工具 `graphify_auto`，在每次專案載入或 git pull 後自動執行 `graphify . --update`。
- **優先讀取 Graph**：在 Agent 的 system prompt 中加入：「每次處理專案相關問題時，先使用 graphify 工具或直接讀取 GRAPH_REPORT.md」。
- **結合 Antigravity / Gemini CLI**：Graphify 原生支援 Gemini CLI，效果更好。

---

**需要我幫你寫完整的工具程式碼 + prompt 範例嗎？**
或者告訴我你目前 aa-TW 的專案結構（例如有沒有 custom_tools 資料夾），我可以給更精準的檔案路徑和整合方式！
