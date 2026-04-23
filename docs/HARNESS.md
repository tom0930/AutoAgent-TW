# AI Harness 使用手冊

## 快速開始

### 安裝

```bash
# 克隆專案
git clone https://github.com/tom0930/AutoAgent-TW.git
cd AutoAgent-TW

# 安裝依賴
pip install -r requirements.txt
```

### 使用 CLI

```bash
# 啟動 Gateway
python -m src.harness.cli.main start

# 查看狀態
python -m src.harness.cli.main status

# 列出 Skills
python -m src.harness.cli.main skill list

# 列出 Sessions
python -m src.harness.cli.main session list

# 查看 Cron 任務
python -m src.harness.cli.main cron list

# 查看已配對設備
python -m src.harness.cli.main node list

# 系統健康檢查
python -m src.harness.cli.main system doctor
```

### 使用 aa-harness 快捷命令

```bash
# 設定路徑後可直接使用
aa-harness start
aa-harness status
aa-harness skill list
```

## 架構總覽

```
┌──────────────────────────────────────────────────────────────┐
│                      AI Harness Core                         │
├──────────────────────────────────────────────────────────────┤
│  CLI          │  Gateway    │  Session   │  Skill Engine    │
│  ─────────── │  ──────────  │  ───────  │  ─────────────   │
│  統一命令列    │  守護行程     │  對話管理  │  擴展系統        │
├──────────────────────────────────────────────────────────────┤
│  Vision      │  MCP Hub    │  Cron     │  Node Pairing    │
│  ─────────── │  ──────────  │  ───────  │  ────────────── │
│  螢幕視覺     │  伺服器路由    │  排程任務  │  設備配對        │
├──────────────────────────────────────────────────────────────┤
│  Canvas System  │  Agent Spawner  │  Message Router       │
│  ─────────────  │  ───────────────  │  ──────────────────  │
│  視覺化狀態      │  子代理管理        │  統一訊息介面         │
└──────────────────────────────────────────────────────────────┘
```

## 核心模組

### Gateway
```python
from src.core.harness_gateway import HarnessGateway

gateway = HarnessGateway()
gateway.start()
status = gateway.status()
gateway.stop()
```

### Session Manager
```python
from src.core.session_manager import SessionManager, SessionKind

manager = SessionManager(Path("data/sessions"))
session = manager.create(SessionKind.MAIN, label="主對話")
manager.send(session.key, "你好", role="user")
```

### Skill Engine
```python
from src.core.skill import SkillEngine

engine = SkillEngine(Path("skills"))
result = engine.execute("my-skill", params={"key": "value"})
```

### Canvas System
```python
from src.harness.canvas import CanvasSystem, NodeType

canvas = CanvasSystem("main")
node = canvas.add_node("代理", NodeType.AGENT)
canvas.export_mermaid()  # 匯出為 Mermaid 圖
```

## 安全性

- 嚴格遵循 STRIDE 威脅模型
- Session 資料加密儲存
- Plugin 簽章驗證
- MCP Tool 白名單
- Vision 資料不寫入磁碟

---

*最後更新：2026-04-23*
