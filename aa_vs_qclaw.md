# AutoAgent-TW vs QClaw (OpenClaw) 完整功能比對報告

> 生成時間：2026-04-25 23:58 GMT+8
> 分析者：代碼文學家（代碼文檔生成 Agent）
> 資料來源：Z:\autoagent-TW 原始碼掃描 + OpenClaw 官方文件

---

## 一、系統概況

| 維度 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **定位** | 工業級自主開發代理框架（IDE深度整合） | 個人 AI 助理（多渠道即時通訊整合） |
| **版本** | v3.3.2 (2026-04-25) | 2026.4.5 (3e72c03, 2026-04) |
| **語言** | Python + TypeScript/Node | Node.js (TypeScript) |
| **作者** | tom0930 (自建) | Peter Steinberger + 社群 |
| **License** | MIT | MIT |
| **核心 Paradigm** | GSD 流程引擎 + 多 Agent 並行 | Gateway 控制平面 + 多渠道路由 |
| **目標用戶** | 開發者 / 企業內部 Agent | 個人用戶 / 開源社群 |
| **程式碼規模** | ~80 個 Python 模組 + ~100 個 Node 擴展 | 300+ TypeScript 模組 |

---

## 二、架構設計

| 子系統 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|--------|-----------------|---------------------|
| **控制平面** | `HarnessGateway`（Python daemon）| `Gateway`（Node.js WebSocket 服務，`ws://127.0.0.1:18789`）|
| **通訊架構** | 自定義 WS 訊息路由 + JSONL Buffer | 原生 WebSocket 單一控制平面 |
| **Agent 執行** | Sub-Agent Spawner + `AgentProcess` | Pi Agent RPC Runtime |
| **狀態管理** | L1/L2/L3 Memory Palace + 知識圖譜 | Session Store + LCM 壓縮 |
| **並發模型** | Threading + Job Object (Windows) | Event-driven + Worker threads |
| **IPC 機制** | JSONL Buffer + subprocess | WebSocket RPC |

---

## 三、訊息渠道（Channel）

| 渠道 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| Telegram | ❌ 無 | ✅ 原生支援（grammY）|
| Discord | ❌ 無 | ✅ 原生支援（discord.js）|
| WhatsApp | ❌ 無 | ✅ 原生支援（Baileys）|
| Slack | ❌ 無 | ✅ 原生支援（Bolt）|
| LINE | ✅ Phase 133 知識整合（有限）| ✅ 原生支援 |
| Signal | ❌ 無 | ✅ 原生支援（signal-cli）|
| Microsoft Teams | ❌ 無 | ✅ 原生支援（Bot Framework）|
| iMessage | ❌ 無 | ✅ BlueBubbles 原生支援 |
| Matrix | ❌ 無 | ✅ 原生支援 |
| Google Chat | ❌ 無 | ✅ 原生支援（Chat API）|
| WeChat | ❌ 無 | ✅ 官方插件（`@tencent-weixin/openclaw-weixin`）|
| IRC | ❌ 無 | ✅ 原生支援 |
| Synology Chat | ❌ 無 | ✅ 原生支援 |
| Nostr | ❌ 無 | ✅ 原生支援 |
| Mattermost | ❌ 無 | ✅ 原生支援 |
| Nextcloud Talk | ❌ 無 | ✅ 原生支援 |
| Feishu（飛書）| ❌ 無 | ✅ 原生支援 |
| Zalo | ❌ 無 | ✅ 原生支援 |
| Tlon | ❌ 無 | ✅ 原生支援 |
| Twitch | ❌ 無 | ✅ 原生支援 |
| **渠道總數** | **1（LINE，僅知識管道）** | **23+ 完整渠道** |
| 群組管理 | ❌ 無 | ✅ Group routing + mention gating + allowlist |

---

## 四、Agent 能力

| 能力 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **多 Agent 協調** | ✅ LangGraph + ReAct Loop | ✅ Sub-Agent Registry + workspace isolation |
| **Sub-Agent 命名** | `AgentProcess` + UUID v4 | ✅ Workspace + per-agent sessions |
| **Tool Use** | MCP Hub (ToolNode) | ✅ 內建工具集（60+ 工具）|
| **Long-term Memory** | ✅ L1/L2/L3 Palace + RAG | ✅ LCM Summarization + Memory Search |
| **視覺自動化** | ✅ RVA Engine (UIA/Win32) | ✅ Canvas + A2UI |
| **代碼執行** | ✅ Subprocess + Job Object | ✅ exec tool (with sandbox/approval) |
| **意圖路由** | ✅ Skill Engine（關鍵字匹配）| ✅ Skills + ClawHub auto-search |
| **對話記憶** | ✅ Palace 持久化 | ✅ Session model（main/group/fork）|
| **自我修復** | ✅ AutoFix Engine（Phase 規劃中）| ❌ 無（但有 Approval System）|
| **自動反思** | ⚠️ ReAct Loop（5輪上限）| ✅ `compact` / `/think` / `/verbose` |
| **任務排程** | ✅ CronScheduler daemon | ✅ `cron` tool + webhook + Gmail Pub/Sub |
| **分支管理** | ✅ Branch Sandbox（AutoFix）| ❌ 無 |

---

## 五、工具系統（Tools）

| 工具類型 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|---------|-----------------|---------------------|
| **Browser 控制** | ❌ 無 | ✅ dedicated Chrome/Chromium CDP + profiles |
| **Canvas 視覺** | ✅ Phase 136 React Dashboard（Mermaid.js）| ✅ Live Canvas + A2UI push/reset/snapshot |
| **Cron 排程** | ✅ `CronScheduler`（Python）| ✅ `cron` tool + webhook surface |
| **檔案操作** | ✅ read/write/edit | ✅ read/write/edit（sandbox-aware）|
| **節點控制** | ✅ RVA Engine（Windows GUI 自動化）| ✅ nodes tool（macOS/iOS/Android）|
| **麥克風/語音** | ❌ 無 | ✅ Voice Wake + Talk Mode（ElevenLabs）|
| **相機控制** | ❌ 無 | ✅ camera_snap/clip |
| **螢幕錄製** | ✅ VisionHarness（opencv）| ✅ screen_record |
| **位置查詢** | ❌ 無 | ✅ location_get |
| **通知推送** | ❌ 無 | ✅ system.notify |
| **MCP 整合** | ✅ Phase 125 MCP Hub | ✅ MCP Client Manager + registry |
| **Git 操作** | ✅ aa-gitpush Engine + Serial Guard | ❌ 無原生（依賴 exec）|
| **代碼文檔** | ✅ code-doc-generator Skill | ❌ 無 |
| **知識檢索** | ✅ NotebookLM RAG | ✅ Memory Search |
| **OCR** | ✅ Gemini 1.5 Flash | ✅ 圖片理解（Multimodal）|
| **終端操作** | ⚠️ PowerShell 腳本 | ✅ `exec` tool |

---

## 六、知識管理

| 功能 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **RAG 查詢** | ✅ NotebookLM 整合 | ✅ Memory Search + embeddings |
| **文件攝取** | ✅ Gemini 1.5 Flash OCR | ✅ 圖片理解 |
| **雲端同步** | ✅ Google Drive + Rclone | ❌ 無直接整合 |
| **向量檢索** | ✅ rerank.py | ✅ engine-embeddings |
| **知識分享** | ✅ LineBot 分享鉤子 | ✅ Memory recall |
| **上下文壓縮** | ✅ Palace Compression | ✅ LCM Summarization |
| **知識持久化** | ✅ Palace JSONL | ✅ Session transcript files |
| **外部 API 整合** | ✅ LineBot + Google Drive | ✅ Gmail, Calendar, etc. |

---

## 七、安全機制

| 機制 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **DM 政策** | ✅ `LINE_ADMIN_UID_LIST` 白名單 | ✅ `dmPolicy` pairing/open + allowlist |
| **URL 白名單** | ✅ `autocli_guard.py` Zero-Trust | ✅ SSRF guard + path validation |
| **沙箱隔離** | ⚠️ Branch Sandbox（規劃中）| ✅ Docker for non-main sessions |
| **Prompt Injection** | ✅ Context Guard | ✅ Security defaults |
| **敏感資訊掃描** | ✅ Guardian Scan | ✅ `context_guard` |
| **命令執行審批** | ❌ 無 | ✅ Exec approvals（per node/session）|
| **Tailscale 暴露** | ❌ 無 | ✅ Serve / Funnel 模式 |
| **Webhook 安全** | ⚠️ 基本驗證 | ✅ Secret signing |
| **速率限制** | ❌ 無 | ✅ Rate limit per user |

---

## 八、CLI 與開發者體驗

| 功能 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **CLI 入口** | `aa-harness` / `aa-tw` | `openclaw` |
| **子命令數量** | ~10（start/stop/session/node/vision/cron/canvas等）| ~30+ |
| **健康檢查** | ✅ `aa-harness doctor` | ✅ `openclaw doctor`（含遷移）|
| **安裝方式** | PowerShell 一鍵腳本（需管理員）| npm + onboard wizard（全平台）|
| **終端主題** | ❌ 無 | ✅ 20+ 終端主題 |
| **Starship 整合** | ✅ JetBrainsMono Nerd Font | ❌ 無 |
| **IDE 整合** | ✅ Antigravity IDE 深度整合（UIA）| ❌ 無 |
| **Doc 生成** | ✅ code-doc-generator Skill | ❌ 無 |
| **安裝精靈** | ❌ 無（手動引導）| ✅ `openclaw onboard` |
| **遠端控制** | ❌ 無 | ✅ `openclaw agents/spawn/...` |

---

## 九、Skills 生態

| 項目 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **技能市場** | ❌ 自建，無市集 | ✅ ClawHub（clawhub.com）|
| **技能數量** | ~10 自建 skills | 50+ 官方 + 社群 skills |
| **技能類型** | code-doc-generator, find-skills | 1password, apple-notes, github, notion, spotify, etc. |
| **自動安裝** | ✅ `aa-installer.ps1` | ✅ `openclaw plugins install` |
| **技能觸發** | ✅ 關鍵字意圖路由 | ✅ 自動搜索 + 依需求拉取 |
| **Skill SDK** | ⚠️ 手動定義 SKILL.md | ✅ 結構化 SKILL.md 規範 |
| **技能發現** | ✅ find-skills（本地）| ✅ ClawHub 線上市場 |

---

## 十、部署與平台支援

| 維度 | **AutoAgent-TW** | **QClaw / OpenClaw** |
|------|-----------------|---------------------|
| **作業系統** | Windows（主要）/ Linux 有限 | macOS + Linux + Windows (WSL2) |
| **macOS 原生** | ❌ 無 | ✅ 選單列 App |
| **iOS/Android** | ❌ 無 | ✅ iOS/Android Node App |
| **Daemon 管理** | 需手動設定（無 service）| ✅ launchd/systemd 自動 |
| **遠端閘道** | ❌ 無 | ✅ Tailscale Serve/Funnel + SSH Tunnel |
| **Docker** | ⚠️ 僅規劃 | ✅ 官方 Docker 鏡像 |
| **Nix** | ❌ 無 | ✅ 原生 Nix mode |
| **本地-first** | ✅ 全本地 | ✅ 全本地 |
| **更新機制** | ❌ 無自動更新 | ✅ `openclaw update` |

---

## 十一、QClaw 強項 Top 10 完整分析 + 改進PLAN

---

### 🥇 第1名：23+ 訊息渠道原生整合

**現況：** AutoAgent-TW 只有 LINE（且僅用於知識管道，非完整 Bot）。

**QClaw 的做法：**
- 每個渠道一個專屬適配層（如 `channels/telegram/`, `channels/discord/`）
- 統一 `ChannelPlugin` 介面 + 差異化底層實現
- 支援 channel-specific 功能（Slack Thread、Discord Slash Command 等）

**對 AutoAgent-TW 的價值：** 讓 Antigravity IDE 的 Agent 透過任何渠道觸達用戶，建構真正的多觸點自動化工作流。

**→ PLAN-A：Multi-Channel Adapter（P0）**

---

### 🥈 第2名：訊息渠道 DM Pairing 安全模型

**現況：** AutoAgent-TW 使用簡單白名單 UID 列表，無配對流程。

**QClaw 的做法：**
```javascript
dmPolicy: "pairing"  // 陌生者收到配對碼，須管理員審批
dmPolicy: "open"      // 完全開放
```
- 配對請求帶時效性驗證碼
- 允許清單持久化（`pairing-store`）
- 支援精細控制：`channels.discord.allowFrom` 等

**→ PLAN-B：Universal DM Policy（P0）**

---

### 🥉 第3名：Skills 開放生態（ClawHub）

**現況：** AutoAgent-TW 有 ~10 個自建 skills，無市場，無發現機制。

**QClaw 的做法：**
- `clawhub.com` 線上市場
- `openclaw plugins install <name>` 一鍵安裝
- 自動意圖檢測 → 依需求拉取技能
- 50+ 官方維護的技能（github, notion, spotify, 1password...）

**→ PLAN-C：AutoAgent-TW Skills Hub（P0）**

---

### 第4名：Docker Sandbox 沙箱隔離

**現況：** AutoAgent-TW 的 Branch Sandbox 還在規劃，且無 Docker 整合。

**QClaw 的做法：**
- 非 main session（群組/頻道）的 bash 執行在 Docker 容器內
- 可配置的沙箱策略（allowlist/denylist）
- 隔離網路、檔案系統、資源（CPU/記憶體）

**→ PLAN-D：Docker Sandbox for AutoFix（P1）**

---

### 第5名：Voice Wake / Talk Mode 語音喚醒

**現況：** AutoAgent-TW 完全沒有語音能力。

**QClaw 的做法：**
- macOS/iOS：Wake word 觸發（ElevenLabs）
- Android：連續語音對話（系統 TTS fallback）
- `/voice` command 即時切換

**→ PLAN-E：Voice Module（P1）**

---

### 第6名：Exec Approval 分級審批

**現況：** AutoAgent-TW 的 exec 完全無審批，Agent 可執行任意命令。

**QClaw 的做法：**
```
session: main      → 完全信任（full access）
session: group     → Docker sandboxed
node: host         → 需要 elevated approval
node: sandboxed    → limited exec
```
- Inline button 審批卡片（DM/群組可用）
- `/approve` 或 API `gateway.approvals.*`

**→ PLAN-F：Approval System（P1）**

---

### 第7名：Tailscale 遠端閘道

**現況：** AutoAgent-TW 的 Gateway 只能在本地運行。

**QClaw 的做法：**
- `gateway.tailscale.mode: "serve"` → 僅 tailnet 內 HTTPS
- `gateway.tailscale.mode: "funnel"` → 公開 HTTPS（需密碼）
- Gateway 綁定 loopback，僅透過 Tailscale 暴露

**→ PLAN-G：Remote Gateway（P1）**

---

### 第8名：Browser CDP 控制

**現況：** AutoAgent-TW 完全無瀏覽器自動化能力。

**QClaw 的做法：**
- dedicated openclaw Chrome/Chromium
- CDP (Chrome DevTools Protocol) 全控制
- snapshot/screenshot/action/upload
- profiles 管理（隔離 cookie/狀態）

**→ PLAN-H：Browser Automation（P1）**

---

### 第9名：OpenClaw Onboard 安裝精靈

**現況：** AutoAgent-TW 需要手動執行 PowerShell 腳本，無引導流程。

**QClaw 的做法：**
- `openclaw onboard --install-daemon`
- 逐步引導：gateway → workspace → channels → skills
- 環境自動偵測（WSL2/Linux/macOS）
- 錯誤遷移（doctor migrations）

**→ PLAN-I：Onboard Wizard（P2）**

---

### 第10名：多平台原生支援

**現況：** AutoAgent-TW 只支援 Windows，無 macOS/iOS/Android。

**QClaw 的做法：**
- macOS：選單列 App（Gateway 控制、Voice Wake、PTT、WebChat）
- iOS：Node App（Canvas、Voice Wake、相機、螢幕錄製）
- Android：Node App（相機、位置、通知、SMS、Photos）

**→ PLAN-J：Cross-Platform Node（P2）**

---

## 十二、整合 PLAN 詳細實作計畫

---

### PLAN-A｜Multi-Channel Adapter（P0）

**目標：** 讓 AutoAgent-TW 支援至少 5 個渠道（Telegram, Discord, LINE, WhatsApp, Slack）

**架構設計：**
```
src/channels/
  __init__.py          # Channel 基類
  base.py              # ChannelPlugin 抽象層
  telegram.py          # Telegram Bot 適配
  discord.py           # Discord Bot 適配
  line.py              # LINE Bot 適配（擴展現有）
  whatsapp.py          # WhatsApp Bot 適配
  slack.py             # Slack Bot 適配
  router.py            # 統一訊息路由器
```

**標準化訊息格式：**
```python
@dataclass
class UnifiedMessage:
    channel: str            # "telegram" / "discord" / ...
    sender_id: str          # 渠道原生的 sender ID
    text: str               # 訊息內容
    timestamp: float        # 時間戳
    attachments: list       # 附件
    reply_to: Optional[str] # 回覆目標
```

**階段規劃：**
| Phase | 任務 | 預計工時 |
|-------|------|---------|
| A1 | 設計 Channel 基類 + 訊息標準化格式 | 4h |
| A2 | 實作 Telegram Adapter（最簡單）| 6h |
| A3 | 實作 Discord Adapter | 8h |
| A4 | 實作 LINE Adapter（擴展現有）| 4h |
| A5 | 統一路由接入 HarnessGateway | 2h |

**驗收標準：**
- `aa-tw channel list` 顯示所有已配置渠道
- `aa-tw channel test <name>` 發送測試訊息
- 所有渠道訊息正確路由到 Agent 對話

---

### PLAN-B｜Universal DM Policy（P0）

**目標：** 廢除 `LINE_ADMIN_UID_LIST`，替換為通用配對系統

**架構：**
```python
class DMPolicy(Enum):
    OPEN = "open"       # 任何人可互動
    PAIRING = "pairing" # 陌生者需配對碼審批
    CLOSED = "closed"   # 完全拒絕

class PairingStore:
    """持久化已配對的 sender ID"""
    def add(self, channel: str, sender_id: str, label: str): ...
    def remove(self, channel: str, sender_id: str): ...
    def is_allowed(self, channel: str, sender_id: str) -> bool: ...
    def generate_code(self, channel: str) -> str: ...
    def approve(self, channel: str, code: str) -> bool: ...
```

**實作點：**
1. 新增 `src/channels/dm_policy.py`
2. 擴展 `src/channels/base.py` → `check_access(sender_id)`
3. 設定檔支援 `channels.<name>.dmPolicy`
4. `/aa-pair approve <channel> <code>` CLI 命令
5. 移除舊有的 `LINE_ADMIN_UID_LIST`

---

### PLAN-C｜AutoAgent-TW Skills Hub（P0）

**目標：** 建立類似 ClawHub 的技能市場，發布到 GitHub/Gitea

**架構：**
```
skills-hub/
  index.json           # 技能清單（含 metadata）
  SKILL.md             # 市場入口文件
  skills/
    code-doc-generator/  # ✅ 已有
    autocli/             # ✅ 已有（Phase 160）
    docling-mcp/        # 已有
    biggo-scraper/      # 已有
    pchome-crawler/     # 已有
    github-integration/  # 需新建
    notion-sync/        # 需新建
    slack-adapter/       # 需新建（依賴 PLAN-A）
    docker-sandbox/      # 需新建（依賴 PLAN-D）
```

**index.json schema：**
```json
{
  "version": "1.0",
  "skills": [
    {
      "name": "code-doc-generator",
      "version": "1.0.0",
      "description": "自動生成 Python/JavaScript Docstring 與 API 文件",
      "author": "tom0930",
      "triggers": ["生成文件", "代碼註釋", "Docstring"],
      "github": "https://github.com/tom0930/autoagent-TW",
      "stars": 42,
      "installs": 156
    }
  ]
}
```

**實作：**
1. 將現有 skills 重構為標準 SKILL.md 格式（name/description/triggers/schema）
2. 生成 `skills-hub/index.json`（含 GitHub Stars、下載量）
3. 實作 `aa-skills search <keyword>` / `aa-skills install <name>` CLI
4. 可選：部署到 GitHub Pages 作為線上市場

---

### PLAN-D｜Docker Sandbox for AutoFix（P1）

**目標：** 讓 AutoFix 的修復測試在 Docker 容器隔離執行

**架構：**
```python
import docker

class DockerSandbox:
    """AutoFix 隔離沙箱，確保修復測試不影響主線"""
    def __init__(self, image: str = "python:3.13-slim"):
        self.client = docker.from_env()
        self.container = self.client.containers.run(
            image,
            detach=True,
            mem_limit="512m",
            cpu_period=100000,
            cpu_quota=50000,  # 50% CPU
            network_mode="none",  # 網路隔離
            volumes={str(workspace): {"bind": "/workspace", "mode": "ro"}}
        )

    def exec(self, cmd: list) -> ExecResult:
        """在容器內執行命令，回傳結果"""
        result = self.container.exec_run(cmd)
        return ExecResult(
            stdout=result.output.decode(),
            exit_code=result.exit_code
        )

    def destroy(self):
        self.container.remove(force=True)
```

**流程：**
```
需求 → Branch Sandbox → 修復代碼 →
  Docker 容器內執行測試 →
    Pass → Git PR / Merge
    Fail → AutoFix 重試或 Git Reset
```

**依賴：** `pip install docker`

---

### PLAN-E｜Voice Module（P1）

**目標：** 加入語音喚醒（可從 Windows Cortana/WSA 著手）

**實作路徑：**
```
src/voice/
  __init__.py
  wake_word.py     # 關鍵字偵測（"Hey Antigravity"）
  asr.py           # 語音轉文字（SpeechRecognition）
  tts.py           # TTS 回應（pyttsx3 / edge-tts）
  stream.py        # 連續語音對話
```

**觸發流程：**
```
麥克風 → Wake Word 偵測 → 開啟 ASR → 文字 -> Agent →
  回應文字 -> TTS -> 播放音訊
```

**依賴：** `pip install SpeechRecognition pyttsx3 edge-tts`

---

### PLAN-F｜Approval System（P1）

**目標：** 在執行危險命令前要求人類審批

**架構：**
```python
class RiskLevel(Enum):
    LOW = 0      # 讀取、查詢
    MEDIUM = 1   # 寫入檔案、建立資源
    HIGH = 2     # 刪除、修改系統
    CRITICAL = 3 # git push --force、rm -rf

@dataclass
class ApprovalRequest:
    request_id: str
    session_id: str
    sender_id: str
    command: str
    risk_level: RiskLevel
    requested_at: float
    status: str  # PENDING / APPROVED / REJECTED / EXPIRED
    expires_at: float
```

**CLI 命令：**
```bash
aa-tw approval list           # 列出待審批
aa-tw approval approve <id>   # 批准
aa-tw approval reject <id>   # 拒絕
aa-tw approval timeout        # 設定超時（預設 5 分鐘）
```

**整合點：**
- 掛鉤至 `harness_gateway.py` 的事件匯流排
- 整合 ContractEngine（Phase 153）做風險評估
- 整合 PLAN-A（Multi-Channel Adapter）發送審批通知

---

### PLAN-G｜Remote Gateway（P1）

**目標：** 透過 SSH Tunnel 或自架 reverse proxy 實現遠端訪問

**最簡方案（SSH Tunnel）：**
```powershell
# 用戶端（macOS/Linux/Windows）
ssh -L 18789:localhost:18789 user@gateway-host
openclaw gateway --port 18789
```

**Gateway 端增強：**
1. 新增 `gateway.remote.enabled: true`
2. SSH Key 配置引導
3. 更新 `aa-tw gateway status` 顯示遠端連線數
4. JWT Token 認證（防止未授權訪問）

**長期方案：** 参考 QClaw Tailscale Serve/Funnel，評估使用 Cloudflare Tunnel 或 Ngrok

---

### PLAN-H｜Browser Automation（P1）

**目標：** 接入 CDP 控制 Chromium 瀏覽器

**實作路徑：**
```
src/browser/
  __init__.py
  cdp_client.py    # CDP 客戶端封裝
  page.py          # 頁面控制
  screenshot.py    # 截圖 + OCR
  extractor.py     # AutoCLI 整合（Phase 160）
```

**核心功能：**
```python
class BrowserController:
    def __init__(self, profile: str = "default"):
        self.browser = launch_chrome(profile=profile)

    def navigate(self, url: str): ...
    def screenshot(self, path: str): ...
    def click(self, selector: str): ...
    def type(self, selector: str, text: str): ...
    def extract_text(self, selector: str) -> str: ...
    def wait_for(self, selector: str, timeout: int = 10): ...
```

**整合 Phase 160 AutoCLI：**
- AutoCLI 負責 HTTP 請求提取
- BrowserController 負責 JavaScript 渲染後的內容

**依賴：** `pip install playwright`

---

### PLAN-I｜Onboard Wizard（P2）

**目標：** `aa-tw onboard` 引導式初始化

**流程：**
```
1. 環境偵測
   - OS / Python 版本 / Node 版本 / Git
   - 顯示診斷報告 ⚠️

2. Gateway 設定
   - Port 選擇
   - 開機啟動（systemd / Task Scheduler）

3. 渠道配置
   - 選擇要啟用的渠道（Telegram/Discord/LINE...）
   - API Key / Bot Token 輸入

4. Skills 安裝
   - 推薦清單
   - 自訂搜尋

5. 測試驗證
   - 發送測試訊息
   - 顯示最終配置
```

**功能：**
- 環境依賴檢查（Python/Node/Git）
- 生成 `~/.autoagent-tw/config.toml`
- Doctor 遷移（自動修補舊版配置）

---

### PLAN-J｜Cross-Platform Node（P2）

**目標：** macOS/iOS/Android Node 應用

**優先順序：** macOS > Android > iOS

**macOS Node 核心功能：**
```swift
// 透過 openclaw nodes pair 與 Gateway WS 配對
// 功能列表：
// - Camera snap/clip
// - Screen recording
// - Location get
// - Notifications
// - Canvas
// - system.run / system.notify
```

**Node 端通訊協議：**
```python
class NodeProtocol:
    # WebSocket 連線
    CONNECT = "node.connect"
    PAIR = "node.pair"

    # 能力發現
    CAPABILITIES = "node.capabilities"  # 回傳設備能力清單

    # 動作調用
    INVOKE = "node.invoke"  # {"action": "camera_snap"}
```

---

## 十三、實作優先級總表

| PLAN | 名稱 | 優先級 | 預計工時 | 主要依賴 | Phase |
|------|------|:------:|:-------:|---------|-------|
| **A** | Multi-Channel Adapter | **P0** | ~24h | B（DM Policy）| Phase 161 |
| **B** | Universal DM Policy | **P0** | ~8h | — | Phase 161 |
| **C** | Skills Hub | **P0** | ~16h | — | Phase 161 |
| D | Docker Sandbox | P1 | ~12h | — | Phase 162 |
| E | Voice Module | P1 | ~20h | — | Phase 162 |
| F | Approval System | P1 | ~16h | B | Phase 162 |
| G | Remote Gateway | P1 | ~8h | — | Phase 162 |
| H | Browser Automation | P1 | ~16h | — | Phase 163 |
| I | Onboard Wizard | P2 | ~12h | A, B | Phase 163 |
| J | Cross-Platform Node | P2 | ~40h | — | Phase 164 |

**預計完成：Phase 161 ~ Phase 164（4 個衝刺週期）**

---

## 十四、AutoAgent-TW 差異化優點（QClaw 做不到的）

| 能力 | 說明 | Phase |
|------|------|-------|
| **IDE 深度整合** | Antigravity IDE 的 UIA/Win32 GUI 自動化 | DONE（M31-M35）|
| **FPGA 工具鏈** | Vivado/Vitis 自動化追蹤 | Phase 159 規劃 |
| **GSD 流程引擎** | Discuss → Plan → Execute → QA → Ship 結構化 | DONE |
| **代碼文檔生成** | code-doc-generator Skill（Docstring/JSDoc）| DONE |
| **Git 原生整合** | aa-gitpush 引擎 + Serial Guard | DONE |
| **工業記憶體優化** | IDE Stealth Mode（Pyrefly LSP shadow check）| DONE |
| **Google Desktop AI** | GoogleAppController 整合 | DONE（Phase 158）|
| **LineBot 知識管道** | LineBot ↔ Google Drive ↔ NotebookLM | DONE（Phase 133）|
| **AutoFix 自癒引擎** | Branch Sandbox + Git Checkpoint 回滾 | Phase 161 規劃 |
| **Buffer Engine** | Phase-based 容錯 + 斷點續傳 | DONE |

---

## 十五、整合戒律

1. **不改變 GSD 核心流程** — 所有新功能都服從 Discuss → Plan → Execute → QA → Ship
2. **Channel Layer 不得污染 Core** — 訊息轉換在 Router 層完成，Core 完全不知曉渠道差異
3. **所有新功能必須有 Docstring** — 保持「代碼文學家」的角色本色
4. **Security by Default** — 新增任何外部通道前，必須先完成 PLAN-B（DM Policy）
5. **Skills 優先複用** — 新功能優先評估是否可封裝為 Skill，再考慮進入 Core

---

*文件由代碼文學家 📖 自動生成 | AutoAgent-TW v3.3.2 | 2026-04-25*
