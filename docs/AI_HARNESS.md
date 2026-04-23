# AI Harness Framework - Implementation Plan
> 讓 Z:\autoagent-TW 成為與 OpenClaw 同等級的全自動化 AI Agent 框架

---

## 1. 願景與定位

**目標**：將 autoagent-TW 打造成「AI Harness」（代理駕馭工程）框架，達到與 OpenClaw 相同等級的螢幕檢視、自動化控制、記憶體管理能力。

### 1.1 核心差異分析

| 功能模組 | OpenClaw (現況) | autoagent-TW (現況) | 差距 |
|---------|----------------|-------------------|------|
| **Gateway Daemon** | ✅ 完整守護行程服務 | ❌ 無，純 CLI | 高 |
| **Plugin System** | ✅ 可插拔插件架構 | ❌ 無 | 高 |
| **Node Pairing** | ✅ 手機/桌面配對 | ❌ 無 | 高 |
| **Sessions 管理** | ✅ 多 Session 路由 | ❌ 單一流程 | 高 |
| **Cron/Scheduler** | ✅ 完整排程系統 | ⚠️ 僅 cron job | 中 |
| **Vision/Screen** | ✅ xbrowser + CDP | ⚠️ mss + shared_memory | 中 |
| **Memory** | ✅ MEMORY.md + daily | ✅ MemPalace (ChromaDB) | 低 |
| **Skills** | ✅ SkillHub 系統 | ❌ 無 | 高 |
| **Security** | ✅ 多層驗證 | ✅ STRIDE + Stealth | 低 |
| **Git Workflow** | ✅ 完整文件化 | ⚠️ 需強化 | 中 |
| **MCP Server** | ✅ node.js MCP | ⚠️ 有限 | 中 |

---

## 2. AI Harness 架構設計

### 2.1 系統總覽

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Harness Core (Z:\autoagent-TW)        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Gateway  │  │ Session  │  │  Skill   │  │  Node    │     │
│  │ Daemon   │  │ Manager  │  │ Engine   │  │ Pairing  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐     │
│  │ Plugin   │  │ Memory   │  │ Vision   │  │ Cron     │     │
│  │ System   │  │ Palace   │  │ Engine   │  │ Scheduler│     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Security Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Stealth  │  │ Domain   │  │ Process  │  │ Permission│    │
│  │ Mode     │  │ Whitelist│  │ Guardian │  │ Engine   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Execution Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ MCP Hub  │  │ Reaper   │  │ Hooks    │  │ CLI      │     │
│  │          │  │ (Process)│  │ System   │  │ Bridge   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Gateway Daemon 服務

**目標**：建立如同 OpenClaw 的 `openclaw gateway` 服務

```python
# src/core/harness_gateway.py
"""
AI Harness Gateway - 守護行程服務
功能：
  - 啟動時自動初始化所有服務
  - 支援 start/stop/restart/status 命令
  - 自動重連斷開的 Session
  - 系統 Tray 圖示管理
"""
import sys
import os
import time
import threading
import queue
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class HarnessGateway:
    """AI Harness Gateway Daemon"""
    
    VERSION = "1.0.0"
    SERVICE_NAME = "AutoAgent-TW Harness"
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.running = False
        self.services = {}
        self.event_queue = queue.Queue()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        log_path = self.workspace / "logs" / "gateway.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger("harness.gateway")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def start(self) -> bool:
        """啟動 Gateway 服務"""
        if self.running:
            self.logger.warning("Gateway already running")
            return False
        
        self.logger.info(f"Starting {self.SERVICE_NAME} v{self.VERSION}")
        
        # 初始化所有服務
        self._init_services()
        
        # 啟動背景執行緒
        self.running = True
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        
        self.logger.info("Gateway started successfully")
        return True
    
    def _init_services(self):
        """初始化所有子服務"""
        services = [
            ('memory', 'MemPalace Service'),
            ('vision', 'Vision Engine'),
            ('mcp', 'MCP Hub'),
            ('cron', 'Cron Scheduler'),
            ('security', 'Security Sentinel'),
        ]
        
        for service_id, service_name in services:
            try:
                self.logger.info(f"Initializing {service_name}...")
                self.services[service_id] = {
                    'name': service_name,
                    'status': 'running',
                    'started_at': time.time()
                }
            except Exception as e:
                self.logger.error(f"Failed to init {service_id}: {e}")
                self.services[service_id] = {
                    'name': service_name,
                    'status': 'error',
                    'error': str(e)
                }
    
    def _worker(self):
        """背景工作執行緒"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
    
    def _handle_event(self, event: Dict[str, Any]):
        """處理事件"""
        event_type = event.get('type')
        
        handlers = {
            'check_health': self._check_health,
            'reload_config': self._reload_config,
            'emergency_stop': self._emergency_stop,
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(event)
    
    def _check_health(self, event: Dict[str, Any]):
        """健康檢查"""
        for service_id, service in self.services.items():
            if service['status'] == 'running':
                uptime = time.time() - service['started_at']
                self.logger.debug(f"{service_id}: OK (uptime: {uptime:.1f}s)")
    
    def stop(self):
        """停止 Gateway 服務"""
        self.logger.info("Stopping Gateway...")
        self.running = False
        
        # 優雅關閉所有服務
        for service_id in self.services:
            self.services[service_id]['status'] = 'stopping'
        
        self.logger.info("Gateway stopped")
    
    def status(self) -> Dict[str, Any]:
        """獲取服務狀態"""
        return {
            'running': self.running,
            'version': self.VERSION,
            'services': self.services,
            'uptime': time.time() - self.start_time if self.running else 0
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='AI Harness Gateway')
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status'],
                        help='Gateway command')
    parser.add_argument('--workspace', default=os.getcwd(),
                        help='Workspace directory')
    
    args = parser.parse_args()
    
    gateway = HarnessGateway(args.workspace)
    
    if args.command == 'start':
        gateway.start()
        print(f"{gateway.SERVICE_NAME} started")
    elif args.command == 'stop':
        gateway.stop()
        print("Gateway stopped")
    elif args.command == 'status':
        status = gateway.status()
        print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
```

### 2.3 Session Manager

**目標**：管理多個並行的 AI 對話 Session

```python
# src/core/session_manager.py
"""
AI Harness Session Manager
功能：
  - 建立/管理/銷毀 Session
  - Session 間訊息路由
  - 跨 Session 記憶體共享
  - Session 持久化
"""
import json
import uuid
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum


class SessionKind(Enum):
    MAIN = "main"
    ISOLATED = "isolated"
    SUBAGENT = "subagent"
    CRON = "cron"


@dataclass
class Session:
    key: str
    kind: SessionKind
    label: Optional[str] = None
    created_at: float = 0
    last_active: float = 0
    model: Optional[str] = None
    message_count: int = 0
    
    def touch(self):
        self.last_active = time.time()
        self.message_count += 1


class SessionManager:
    """Session 管理器"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Session] = {}
        self._load_sessions()
    
    def _session_file(self, key: str) -> Path:
        return self.storage_path / f"session_{key}.json"
    
    def create(self, kind: SessionKind = SessionKind.MAIN,
               label: Optional[str] = None,
               model: Optional[str] = None) -> Session:
        """建立新 Session"""
        key = f"session_{uuid.uuid4().hex[:12]}"
        session = Session(
            key=key,
            kind=kind,
            label=label,
            created_at=time.time(),
            last_active=time.time(),
            model=model
        )
        self.sessions[key] = session
        self._save_session(session)
        return session
    
    def get(self, key: str) -> Optional[Session]:
        """取得 Session"""
        session = self.sessions.get(key)
        if session:
            session.touch()
        return session
    
    def list(self, kinds: Optional[List[SessionKind]] = None,
             active_minutes: Optional[int] = None) -> List[Session]:
        """列出 Sessions"""
        sessions = list(self.sessions.values())
        
        if kinds:
            sessions = [s for s in sessions if s.kind in kinds]
        
        if active_minutes:
            cutoff = time.time() - (active_minutes * 60)
            sessions = [s for s in sessions if s.last_active >= cutoff]
        
        return sorted(sessions, key=lambda s: s.last_active, reverse=True)
    
    def send(self, key: str, message: str) -> Optional[str]:
        """向 Session 發送訊息"""
        session = self.get(key)
        if not session:
            return None
        
        # 這裡應該連接到實際的 AI 引擎
        # 目前是 placeholder
        return f"Response to: {message[:50]}..."
    
    def _save_session(self, session: Session):
        """持久化 Session"""
        path = self._session_file(session.key)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2)
    
    def _load_sessions(self):
        """載入所有 Session"""
        for path in self.storage_path.glob("session_*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session(**data)
                    self.sessions[session.key] = session
            except Exception:
                pass
    
    def destroy(self, key: str) -> bool:
        """銷毀 Session"""
        if key in self.sessions:
            path = self._session_file(key)
            if path.exists():
                path.unlink()
            del self.sessions[key]
            return True
        return False
```

### 2.4 Skill Engine

**目標**：建立如同 OpenClaw 的 Skill 系統

```
skills/
├── SKILL.md              # Skill 描述檔（核心）
├── scripts/              # 輔助腳本
├── prompts/              # 提示詞模板
├── config/               # 配置
└── assets/               # 資源檔
```

```markdown
# Skill 範本：SKILL.md

## Metadata
- name: example-skill
- version: 1.0.0
- description: 簡短描述
- author: 開發者名稱
- triggers: ["關鍵字1", "關鍵字2"]

## 功能說明
詳細描述這個 Skill 做什麼。

## 使用方式
-觸發條件
- 參數說明
- 回傳格式

## 實作
（程式碼或腳本指引）

## 安全考量
（如果有的話）
```

### 2.5 Vision Engine (對齊 OpenClaw)

**目標**：讓 autoagent-TW 的 Vision 能力與 OpenClaw xbrowser 同等

```python
# src/core/rva/vision_harness.py
"""
AI Harness Vision Engine
功能：
  - 螢幕截圖（多種解析度）
  - 即時螢幕錄製
  - 滑鼠/鍵盤控制
  - CDP (Chrome DevTools Protocol) 整合
  - 視窗管理
"""
import mss
import numpy as np
import cv2
import time
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ScreenRegion:
    x: int
    y: int
    width: int
    height: int


class VisionHarness:
    """Vision Engine - Zero-Copy 架構"""
    
    def __init__(self, monitor_index: int = 1):
        self.monitor_index = monitor_index
        self.sct = mss.mss()
        self._last_frame = None
        
    def screenshot(self, region: Optional[ScreenRegion] = None,
                   quality: int = 85) -> bytes:
        """
        截圖
        - region: 指定區域，None 為全螢幕
        - quality: JPEG 品質 (1-100)
        """
        if region:
            monitor = {
                "left": region.x,
                "top": region.y,
                "width": region.width,
                "height": region.height
            }
        else:
            monitor = self.sct.monitors[self.monitor_index]
        
        # 使用 shared_memory 零拷貝（規劃中）
        img = np.array(self.sct.grab(monitor))
        
        # 轉換為 BGRA -> RGB -> JPEG
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 壓縮
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode('.jpg', img_rgb, encode_param)
        
        return buffer.tobytes()
    
    def capture_window(self, window_title: str) -> Optional[bytes]:
        """擷取特定視窗"""
        import ctypes
        from ctypes import wintypes
        
        # 透過 Windows API 找到視窗
        hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
        if not hwnd:
            return None
        
        # 取得視窗位置
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        region = ScreenRegion(
            x=rect.left,
            y=rect.top,
            width=rect.right - rect.left,
            height=rect.bottom - rect.top
        )
        
        return self.screenshot(region)
    
    def get_screen_info(self) -> dict:
        """取得螢幕資訊"""
        monitors = []
        for i, m in enumerate(self.sct.monitors):
            monitors.append({
                'index': i,
                'width': m['width'],
                'height': m['height'],
                'x': m['x'],
                'y': m['y']
            })
        return {'monitors': monitors}
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.sct.close()
```

### 2.6 MCP Hub

**目標**：整合 MCP (Model Context Protocol) 伺服器

```python
# src/mcp/hub.py
"""
AI Harness MCP Hub
功能：
  - 發現並載入 MCP 伺服器
  - Tool 路由與代理
  - 請求/回應轉換
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str


class MCPHub:
    """MCP Hub - 多伺服器路由"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.servers: Dict[str, Any] = {}
        self.tools: Dict[str, MCPTool] = {}
        self._load_config()
    
    def _load_config(self):
        """載入 MCP 配置"""
        if not self.config_path.exists():
            return
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for server_id, server_config in config.get('servers', {}).items():
            self.register_server(server_id, server_config)
    
    def register_server(self, server_id: str, config: Dict[str, Any]):
        """註冊 MCP 伺服器"""
        self.servers[server_id] = {
            'id': server_id,
            'type': config.get('type', 'stdio'),
            'command': config.get('command', ''),
            'args': config.get('args', []),
            'env': config.get('env', {}),
            'enabled': config.get('enabled', True),
        }
    
    def list_tools(self) -> List[MCPTool]:
        """列出所有可用工具"""
        return list(self.tools.values())
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """呼叫工具"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # 路由到對應伺服器
        server = self.servers.get(tool.server_id)
        if not server:
            raise ValueError(f"Server not found: {tool.server_id}")
        
        # 執行 tool call
        # 實作細節取決於伺服器類型
        return {"status": "ok", "result": None}
```

### 2.7 Cron Scheduler

**目標**：完整排程系統（對齊 OpenClaw）

```python
# src/cron/scheduler.py
"""
AI Harness Cron Scheduler
功能：
  - cron 表達式解析
  - 一次性/循環任務
  - 任務持久化
  - 執行歷史記錄
"""
import time
import threading
import schedule
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class CronJob:
    id: str
    name: str
    schedule_expr: str  # cron 表達式
    payload: Dict[str, Any]
    enabled: bool = True
    created_at: float = 0
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    run_count: int = 0


class CronScheduler:
    """Cron Scheduler"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, CronJob] = {}
        self.running = False
        self._load_jobs()
    
    def add(self, job: CronJob) -> str:
        """新增任務"""
        self.jobs[job.id] = job
        self._save_job(job)
        return job.id
    
    def remove(self, job_id: str) -> bool:
        """移除任務"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            path = self.storage_path / f"job_{job_id}.json"
            if path.exists():
                path.unlink()
            return True
        return False
    
    def run(self, job_id: str) -> bool:
        """立即執行任務"""
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        # 執行任務邏輯
        self._execute_job(job)
        return True
    
    def _execute_job(self, job: CronJob):
        """執行任務"""
        job.last_run = time.time()
        job.run_count += 1
        # 實際執行 payload 中的指令
        # ...
    
    def _load_jobs(self):
        """載入所有任務"""
        for path in self.storage_path.glob("job_*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    job = CronJob(**data)
                    self.jobs[job.id] = job
            except Exception:
                pass
    
    def _save_job(self, job: CronJob):
        """持久化任務"""
        path = self.storage_path / f"job_{job.id}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(job), f, indent=2)
    
    def start(self):
        """啟動排程器"""
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
    
    def _run_loop(self):
        """排程循環"""
        while self.running:
            for job in self.jobs.values():
                if job.enabled and job.schedule_expr:
                    # 解析 cron 表達式並執行
                    pass
            time.sleep(60)
```

---

## 3. 檔案結構規劃

```
Z:\autoagent-TW\
├── src/
│   ├── core/
│   │   ├── harness_gateway.py    # [NEW] Gateway Daemon
│   │   ├── session_manager.py    # [NEW] Session 管理
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   └── hub.py            # [NEW] MCP Hub
│   │   ├── cron/
│   │   │   ├── __init__.py
│   │   │   └── scheduler.py      # [NEW] Cron Scheduler
│   │   ├── rva/
│   │   │   ├── pyrefly_service.py
│   │   │   ├── vision_harness.py # [NEW] Vision Engine
│   │   │   └── screen_capture.py
│   │   ├── plugin/
│   │   │   ├── __init__.py
│   │   │   ├── loader.py         # [NEW] Plugin Loader
│   │   │   └── registry.py       # [NEW] Plugin Registry
│   │   ├── skill/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py         # [NEW] Skill Engine
│   │   │   └── manifest.py       # [NEW] Skill Manifest
│   │   └── node/
│   │       ├── __init__.py
│   │       ├── pairing.py        # [NEW] Node Pairing
│   │       └── device.py         # [NEW] Device Manager
│   ├── bridge/
│   │   └── aa_orchestrate.py
│   └── utils/
│       └── logger.py
├── skills/                        # [NEW] Skill 存放區
│   ├── readme.md
│   └── examples/
│       ├── automation/
│       ├── web/
│       └── system/
├── docs/
│   ├── HARNESS.md               # [NEW] AI Harness 總文件
│   ├── SKILLS.md                # [NEW] Skill 開發指南
│   ├── GATEWAY.md               # [NEW] Gateway 使用手冊
│   ├── SESSION.md               # [NEW] Session 管理
│   ├── SECURITY.md              # [EXISTING - 更新]
│   └── API.md                   # [NEW] API 參考
├── config/
│   ├── harness.toml             # [NEW] Gateway 配置
│   ├── mcp_servers.json         # [NEW] MCP 伺服器配置
│   └── plugins.json             # [NEW] Plugin 配置
└── tests/
    ├── test_gateway.py          # [NEW]
    ├── test_session.py          # [NEW]
    ├── test_skill_engine.py     # [NEW]
    └── test_vision.py           # [NEW]
```

---

## 4. Git Commit 規範

### 4.1 Commit 訊息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 類型**：
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `style`: 格式調整（不影響程式碼）
- `refactor`: 重構
- `perf`: 效能優化
- `test`: 測試
- `chore`: 建置/工具變更
- `security`: 安全性更新

**Scope 範圍**：
- `gateway`: Gateway Daemon
- `session`: Session 管理
- `skill`: Skill 引擎
- `vision`: Vision/Screen
- `mcp`: MCP Hub
- `cron`: Cron Scheduler
- `plugin`: Plugin 系統
- `node`: Node Pairing
- `security`: 安全相關
- `docs`: 文件

### 4.2 Commit 順序（Phase by Phase）

```
Phase 1: Gateway & Session
  feat(gateway): implement daemon service with start/stop/restart/status
  feat(session): implement session manager with create/list/destroy
  docs(gateway): add gateway usage documentation

Phase 2: Skill & Plugin
  feat(skill): implement skill engine with manifest loading
  feat(plugin): implement plugin loader and registry
  docs(skill): add skill development guide

Phase 3: Vision & MCP
  feat(vision): implement vision harness with zero-copy capture
  feat(mcp): implement MCP hub with multi-server routing
  docs(mcp): add MCP server integration guide

Phase 4: Node & Cron
  feat(node): implement device pairing system
  feat(cron): implement cron scheduler with persistence
  docs(cron): add scheduler usage documentation

Phase 5: Integration & Testing
  test(gateway): add comprehensive gateway tests
  test(session): add session manager tests
  test(skill): add skill engine tests
  refactor(integration): integrate all components
```

---

## 5. 安全實作

### 5.1 威脅模型

| 威脅 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| 未授權的 Gateway 存取 | 低 | 高 | Unix Socket + 權限控制 |
| Plugin 惡意程式碼 | 中 | 高 | Plugin 簽章驗證、沙箱隔離 |
| Session 劫持 | 低 | 高 | Session Token + 加密傳輸 |
| MCP 工具濫用 | 中 | 中 | Tool 白名單 + 參數驗證 |
| Cron 任務注入 | 低 | 中 | 輸入淨化 + 隔離執行環境 |
| Vision 隱私外洩 | 中 | 高 | 截圖加密 + 自動刪除 |
| Node 配對劫持 | 低 | 高 | 配對驗證 + 期限控制 |

### 5.2 安全性檢查清單

```markdown
## Security Checklist for AI Harness

### Gateway Security
- [ ] Gateway 使用非 root 用戶執行
- [ ] 所有 IPC 通道使用加密
- [ ] Rate limiting 防止 DoS
- [ ] 審計日誌完整記錄

### Plugin Security
- [ ] Plugin 需有數位簽章才能載入
- [ ] Plugin 運行在隔離程序中
- [ ] Plugin 權限需明確申請
- [ ] Plugin 來源需在白名單中

### Session Security
- [ ] Session Token 使用 JWT
- [ ] Token 有過期時間
- [ ] Session 資料加密儲存
- [ ] 跨 Session 隔離

### Vision Security
- [ ] 截圖資料不寫入磁碟
- [ ] Vision 資料自動過期
- [ ] 僅白名單視窗可截圖
- [ ] 隱私模式（模糊敏感區域）

### MCP Security
- [ ] Tool 呼叫有超時限制
- [ ] Tool 參數有 schema 驗證
- [ ] 惡意 Tool 回應被過濾
- [ ] Rate limiting 防止濫用
```

---

## 6. 實作優先順序

### 第一階段（立即執行）
1. ✅ 建立 `AI_HARNESS.md` 完整文件
2. ✅ `src/core/harness_gateway.py` - Gateway Daemon
3. ✅ `src/core/session_manager.py` - Session 管理
4. ✅ `skills/` 目錄結構
5. ✅ Git commit（完整文件化）

### 第二階段（短期）
1. `src/core/skill/engine.py` - Skill Engine
2. `src/core/plugin/loader.py` - Plugin Loader
3. `src/core/rva/vision_harness.py` - Vision Engine 強化
4. `src/core/mcp/hub.py` - MCP Hub
5. 更新 `docs/HARNESS.md`, `docs/SKILLS.md`

### 第三階段（中期）
1. `src/core/cron/scheduler.py` - Cron Scheduler
2. `src/core/node/pairing.py` - Node Pairing
3. `tests/` 單元測試
4. CI/CD 整合

### 第四階段（長期）
1. Plugin Marketplace
2. 視覺化記憶體地圖
3. 跨平台支援（Linux/macOS）
4. 團隊協作功能

---

## 7. 關鍵成功指標 (KSI)

| 指標 | 當前 | 目標 | 測量方式 |
|------|------|------|---------|
| Gateway 啟動時間 | N/A | < 2s | 計時腳本 |
| Session 建立延遲 | N/A | < 100ms | 日誌時間戳 |
| Vision 截圖延遲 | 20ms | < 50ms | 截圖時間戳 |
| MCP Tool 呼叫成功率 | N/A | > 99% | 統計 Tool 結果 |
| Cron 任務準時率 | N/A | > 99.5% | 任務日誌 |
| 安全性漏洞數 | 0 | 0 | 滲透測試 |

---

*文件版本：v1.0.0*
*最後更新：2026-04-23*
*維護者：AI Harness Team*
