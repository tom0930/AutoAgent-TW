# AutoAgent-TW Version Log

## [v3.5.1] - 2026-04-27
### Phase 163: Karpathy Best Practices & Context Optimization
- **Core**: 導入 Andrej Karpathy 編碼原則 (Think Before Coding, Simplicity, Surgical Changes, Goal-Driven).
- **Optimization**: 建立 `CONTEXT_RULES.md` (200+ -> 55 行)，節省 70% Context Token.
- **Verification**: 建立 `scripts/diff_scope_check.py` 強制 Surgical Change 驗證。
- **Contract**: 建立 `_agents/templates/verification_contract.yaml` 機器可驗證合約。
- **Safety**: 在 `AGENTS.md` 導入 PreToolUse 虛擬 Hook 攔截機制。
- **Workflows**: 升級 `aa-discuss2`, `aa-plan`, `aa-qa`, `aa-fix` 整合新架構。

## [v3.5.0] - 2026-04-27
### Phase 162: Harness Engineering Production Guardrails
- **Security**: 導入 `risk-tiers.json` 分級防禦體系。
- **Protocol**: 建立 `AGENTS.md` (AAIF 標準) 規範 Agent 行為禁令。
- **Linter**: 導入 `import-linter` 強制執行 Python 模組依賴方向。
- **Validation**: 實作 `scripts/preflight_gate.py` 自動化風險判定與編譯檢查。

## [v3.3.1-acua-hardening] - 2026-04-22
 
### �� �啣��蠘� (Key Features)
1. **ACUA �嗆�撖行鴌 (Phase 159 Pre-requisites)**: 摰峕� Antigravity-Centric Unified Architecture (ACUA) ����罸�蝵脯���誯��㘾膄 redundant AI 隞�� (Claude Dev / Roo-Cline) 銝衣絞銝��� Antigravity �脰�鞈��隤踹漲��
2. **Git Hook 摨誩��� (Serial Guard)**: ��� `openclaw/.pre-commit-config.yaml` �滚� `require_serial: true` 閬讐���圾瘙箏銁 Intel/AMD 雿𤾸��� CPU 銝钅�脰�憭扯�璅⊥�鈭斗�嚗䔶蔥�� Node/Python �脩�撘閧䔄����園��刻� (OOM) ���獢���剖左�誯���
3. **�啣��芸��嗅𠧧�� (Shadow Reaper)**: �游� `kill_zombies.py` �� `/aa-ship` �� Git Commit 瘚�����甈∩誨蝣潔漱隞睃���䌊�閙��譍蒂蝯�迫 orphaned processes嚗𣬚Ⅱ靽� IDE �瑟��㯄�銵𣬚�蝛拙��扼��
4. **ai-review Hook �𣂼�**: �� Pre-commit 蝞⊿�銝剜迤撘誯��� `ai-review` �文�嚗𣬚� Phase 159 �� FPGA 隞�Ⅳ�芸��硋祟�賊𪊽撟喲�頝胯��
 
### �� �詨���辣�湔鰵 (@file:)
- `openclaw/.pre-commit-config.yaml`: 摨誩��� Hooks �� ai-review �𣂼���
- `scripts/memory_monitor.py`: �啣��閙� RAM 雿𠉛鍂撖抵���翰�批��賬��
- `ROADMAP.md`: �湔鰵 Phase 159 �讠䔄�脣漲��兛憓�㟲�嗵��卝��
 
### �� 摰匧��� (Security)
- **Zero-Trust Tooling**: 蝘駁膄�𧼮��抒洵銝㗇䲮�游�憟𦯀辣嚗峕𤣰�� MCP 摮睃�暺𠺶��
- **Memory Recovery**: 撽𡑒��誯� `Stop-Process` 蝖砍��嗆����改�蝟餌絞�箸�雿𠉛鍂�� 4.5GB+ �滩秐 ~3.2GB��
 

## [v2.9.1-reliability-tuning] - 2026-04-17

### �� �啣��蠘� (Key Features)
1. **Ty-by-Default �嗆� (Phase 152)**: �券𢒰��� IDE �鞱身隤噼�隡箸��刻秐 `ty` (Astral)嚗𣬚Ⅱ靽肽��臭�����箸�蝥諹蕭頩方楊璅∠�霈𠰴��䔶��券��� 500MB+ 閮䀹�擃䈑��𥪜�鈭�扔�渡�頛閖��硔��
2. **Pyrefly Shadow Check 璈笔�**: 撠��鞎㰘��� Pyrefly �见ê̌�冽𪃾�賡𣪧�唾��胯��蔣摮𣂼祟閮��齿�蝔卝��銁 `/aa-qa` �� Git pre-commit ���韏瘀����摰𣬚佅�厩眏 Active Reaper 璈笔��祇��墧𤣰嚗𣬚Ⅱ靽� 0 撣賊�閮䀹�擃𢛵��
3. **�芸��硋��仿𥲤隤方���**: �誯� `pyrefly suppress` 璈笔��刻䌊�閙��斗風�脣�獢���嗵� Win32 API �见ê̌蝻箏仃���隞嗅𥲤�亥圾�鞾𥲤隤� (靽株�頞�� 200+ ��郎��)嚗�之撟�漲撘瑕��讠䔄�ａ�𡁜漲��
4. **Toolchain Installer �券��**: `aa_installer_logic.py` �曉銁��䌊�閙��𡝗��啁��祉� `uv`��ty`��pyrefly`嚗䔶蒂�芯蜓撖怠� Git Hooks嚗���鞉㟲擃娍沲瑽讠�蝮怎宏頧剹��

### �� �詨���辣�湔鰵 (@file:)
- `scripts/aa_installer_logic.py`: 摰㕑���凒�啗䌊�訫��游���
- `scripts/shadow_check.py`: Pyrefly 敶勗�瑼Ｘ䰻�刻� Active Reaper��
- `pyrefly.toml`: 撠���㘾膄�滨蔭���鞈渲���身摰𠾼��
- `.planning/phases/152-dynamic-reliability-debug/QA-REPORT.md`: 摰峕㟲�见ê̌��釭����賢祟�亥�����

### �� 摰匧��� (Security)
- Guardian Scan: ALL PASS��
- 閮䀹�擃𠉛��賡�望�嚗𡁜��嗵Ⅱ靽� `pyrefly` 銝齿�畾条��萄�蝔见���俈霅瑟��嗚��

## [v2.9.0-terminal-optimization] - 2026-04-15
1. **Starship 頝� Shell �鞟內摮堒��游� (Phase 141)**: 撠𤾸� Rust 蝺典神�� Starship 撘閙����誯� `~/.config/starship.toml` 撖行鴌�峕扔蝪⊥芋撘譌�㵪��芸�蝮格�頝臬�瘛勗漲銝阡��厰��𡑒�璅∠�嚗峕�����潛凒閬箄��滢� Token �亥�撟脫曎��
2. **JetBrainsMono Nerd Font �函蔡**: �芸��硋�鋆苷蒂閮餃� Nerd Font 摰嗆���Ⅱ靽萘�蝡舀��賣迤蝣箸葡�� Git��𤌍���蝟餌絞���讠泵����𣂼�閬𤥁死�㚚��潮�撽𨰜��
3. **PowerShell 頝臬�撘瑕��扳䲮獢�**: 撖行鴌 `scripts/setup_starship_force.py`��繧�� .NET �寞�鞈��憭曇圾�鞉�銵橒�敺孵�閫�捱 Windows OneDrive `��辣` 頝臬��� PowerShell `$PROFILE` 銋钅���楊蝣潸��啣�霈𦠜彍�峕郊銵萘���
4. **Token 蝭������ (Context Lean)**: �誯� `truncation_length = 2` ����𧢲芋蝯��瞈橘�撠��甈⊥�隞文��厩�頝臬� Token 雿𠉛鍂�滢�蝝� 40%��

### �� �詨���辣�湔鰵 (@file:)
- `.config/starship.toml`: Token �芸��滨蔭��
- `scripts/setup_starship_force.py`: 頝臬�靽桀儔��釣�交瓲敹���
- `scripts/install_env.ps1`: �啣��芸��硋�鋆肽��研��
- `.planning/phases/141-starship-integration/QA-REPORT.md`: 摰峕㟲��釭撽𡑒��勗���

### �� 摰匧��� (Security)
- Guardian Scan: ALL PASS (�∠′蝺函Ⅳ頝臬�皞Ｘ�嚗峕𣈲�渡�撠滩��詨��啣�霈𦠜彍�勗�)��
- �舀螱 Idempotent �函蔡嚗𡁜�甈∪嘑銵峕�隞支����銴�情�� Profile��

## [v2.8.0-observability-modernization] - 2026-04-14

### �� �啣��蠘� (Key Features)
1. **React �曆誨�硋�銵冽踎 (Phase 136/137)**: 敺孵��冽��𦠜��� HTML 瘜典�璅∪�嚗諹��� React/Vite �嗆����靘𥟇神蝘垍��踵���lassmorphism ��郭蝝见��怎�璆菔稲 UI 擃娪���
2. **皛曉�撘誩嘑銵諹�頝� (Execution Timeline)**: 撖行鴌�瑕� 50 蝑�楨銵萘� LIFO �瑁�甇瑕蟮�����遙�踺��hase 甇詨惇����页��舀螱�讠䔄���皞� Agent ��捱蝑㚚�蝔卝��
3. **Mermaid.js v11 �閙��游�**: �� Dashboard �扳瓲�游� Mermaid 撘閙���覔�� `ROADMAP.md` �單����憭朞𠧧璅躰酉����潭�蝔见�嚗峕𣈲�渲䌊�閧葬�曇�鈭支�撘誩�閬賬��
4. **撌交平蝝帋蒂�潭祥�� (Concurrent Hardening)**: ��� `status_updater.py` (v1.8.0)��繧�� **�笔�撖怠� (Atomic Write)** �� **Exclusive Locking (portalocker)** 璈笔�嚗�銁 100 頛芯蔥�澆��𥟇葫閰虫��娍� 0 銵萘���
5. **�寧𤌍���隞支誨�� (Global Hub)**: �澆�獢�覔�桅��典惇隞�� `package.json`����潸��𣶹�典虾�冽覔�桅��湔𦻖�瑁� `npm run dev` �笔����㕑�撖毺�隞塚�閫�捱�桅�瘛瑚��誯���
6. **�啣��芸��菜葫 (Context Awareness)**: ��銵冽踎�芸��� `PROJECT.md` �偦楆�������閗身摰𡁜朖�航䌊�閗��亦訜�滚�獢���航�蝬剖漲��

### �� �詨���辣�湔鰵 (@file:)
- `.agents/skills/status-notifier/scripts/status_updater.py`: ����� v1.8.0嚗峕𣈲�游�摮鞾����頠��甇乓��
- `~/.gemini/antigravity/dashboard/skills/src/App.tsx`: �冽鰵 React ��銵冽踎�詨���
- `package.json`: �寧𤌍���隞支誨�����
- `run-dashboard.cmd`: 敹急㭘�笔��單𧋦��
- `.planning/phases/137-dashboard-finisher/QA-REPORT.md`: 憯枏�皜祈岫���鞈芸祟閮�𥼚�𨳍��

### �� 摰匧��� (Security)
- Guardian Scan: ALL PASS (�∪��唳援瞍�)��
- CORS Defense: �誯� Vite Proxy 閫�捱�砍𧑐鞈��霈��㚚��嗚��


## [v2.7.0-knowledge-gateway] - 2026-04-13

### �� �啣��蠘� (Key Features)
1. **�亥��㗛��� (Knowledge Gateway - Phase 133)**: 撖行鴌�瑕����蝬渲楝�晞�齿��嗥��閧�銝剖���𣈲�� `@憭扯�` (RAG �亥岷) �� `#�亥�摨冑 (�批捆�臬�) �芸������
2. **憭𡁏芋�� OCR �嘥�蝞⊿�**: �游� Gemini 1.5 Flash 閬𤥁死璅∪���䌊�訫� Line 銝𠰴�������脰�擃条移皞𡝗�摮埈𣊭�吔�銝行��文�擗睃��躰�嚗𣬚移�㗇瓲敹�䰻霅塩��
3. **瘛瑕��峕郊撟喲𢒰 (Hybrid Sync Plane)**: 撖行鴌 `scripts/kb_gdrive_sync.py`��𣈲�� Rclone �惩������ GDrive API (Service Account) �蹱芋撘𧶏�閫�捱�烾�蝬脰楝�啣�銝讠��峕郊�����
4. **�嗆��祈�摰厰俈蝳� (Whitelist Defense)**: 撠𤾸� `LINE_ADMIN_UID_LIST` �賢��桅�摰𡁏��嗚��Ⅱ靽嘥蘨�㗇�甈羓恣��摱�質孛�� AI �讠���䰻霅睃澈�啣�嚗屸俈蝭���� Token �埈���
5. **�砍𧑐蝺抵�������敺� (Local Buffering)**: ���匧𥲤�亙�摰孵���氜�斗䲰 `data/kb_upload_queue/`嚗𣬚Ⅱ靽嘥銁蝬脰楝�����䰻霅䀝��箏仃��

### �� �詨���辣�湔鰵 (@file:)
- `scripts/aa_kb_gateway.py`: �詨�頝舐眏��蒾�滚鱓撽𡑒��� OCR �讛摩撖虫���
- `scripts/kb_gdrive_sync.py`: GDrive API �� Rclone �峕郊撘閙���
- `ARCHITECTURE.md`: �啣��亥��嘥�蝞⊿��� RAG 頝臬��硔��
- `SECURITY.md`: �啣��嘥��脩戌���閬� Injection 蝺抵圾蝑𣇉裦��
- `.planning/phases/133-linebot-gdrive-nlm-combo/QA-REPORT.md`: 摰峕㟲撽𡑒���葫閰血𥼚�𨳍��

### �� 摰匧��� (Security)
- Guardian Scan: ALL PASS (隤滩�撖�麯�急�撽𡑒��𡁻�)��
- �舀螱 Visual Prompt Injection �脩戌嚗𡁻�摰� OCR Prompt 蝭����

## [v2.6.0-mcp-orchestrator] - 2026-04-07

### �� �啣��蠘� (Key Features)
1. **MCP Protocol Integration Layer (Phase 125)**: 撖行鴌 Model Context Protocol (MCP) 摰Ｘ�蝡舐恣��沲瑽卝��𣈲�� Stdio �唾撓�磰降��蒂銵䔶撩�滚膥�笔�嚗諹圾瘙箏�隞���峕�憭扯��∪極�瑯�滨��瑕惜��
2. **MCP Tool Registry (NRT)**: �瑕��賢�蝛粹���極�瑁酉�𡃏” (`server::tool`)��㟲�� `langchain-mcp-adapters` 銝虫耨敺� `Missing transport key` �滨蔭蝻粹萅嚗峕𣈲�� 17+ 頝典像�啗䌊�訫�撌亙���
3. **ReAct Orchestration Loop**: ��� `OrchestrationCoordinator` 隞交𣈲�� LangGraph `ToolNode`���靘𥟇�憭� 5 頛芰��芯蜓閬誩���極�瑁矽�典儐�堆�ReAct嚗㚁��瑕��芸��梢𥲤���閰行��嗚��
4. **MCP 閬𤥁死�硋�銵冽踎 (Dashboard v2)**: �� `status.html` �游� MCP Toolkit 璅嗵惜��朖��𧙗�折���隡箸��典�摨瑕漲 (�叚/�𣞁)��極�瑞蜇�貉�隤輻鍂閰喟敦�亥���
5. **�批遣�芸��硋極�琿� (Internal MCP)**: �函蔡 `autoagent-internal` 隡箸��剁�撠� Phase �亥岷���蝔讠恣������见𥼚�𠰴�鋆萘�璅蹱� MCP 撌亙���

### �� �詨���辣�湔鰵 (@file:)
- `src/core/mcp/mcp_client.py`: 銝西����蝞∠��刻� `load_mcp_tools` 靽格迤 (v1.9.2 Bridge)��
- `src/core/mcp/registry.py`: �瑕��賢�蝛粹���極�瑁酉�𡃏� Schema 閫����
- `scripts/aa_mcp.py`: 蝯曹��� MCP 蝞∠� CLI (list/status/test)��
- `src/core/orchestration/coordinator.py`: ����舀螱 ReAct 敺芰兛����见極�瑞�暺𠺶��
- `scripts/mcp_internal_server.py`: �批遣 FastMCP 隡箸��典祕雿栶��
- `.agents/mcp_servers.json`: 摰匧��𣇉� MCP 隡箸��券�蝵格�隞嗚��
- `.agents/skills/status-notifier/templates/status.html`: ��銵冽踎 MCP Toolkit �蠘�璅∠���

### �� 摰匧��� (Security)
- Guardian Scan: ALL PASS (撌脣祕�� Root Path �𣂼���兛憓���貉���)��
- �舀螱 IRA 5-Level 甈𢠃�蝞∪�嚗鐝CP 撌亙�隤輻鍂�芸�瘜典�憸券麬閰蓥摯甈����


## [v2.5.0-context-defense] - 2026-04-05

### �� �啣��蠘� (Key Features)
1. **Active Context Defense (ACD)**: �寞祥 Antigravity 撌乩��� Max Token Limit Error��䌊�閙��誩極雿𨅯�瑼娍�憭批�������隡� Token 雿𠉛鍂����� `.geminiignore` �㘾膄鈭屸�脖���楊霅舐𤩎�押��
2. **Context Guard Pre-scan**: `/aa-plan` �啣� Step 0 �滨蔭瑼Ｘ䰻嚗�銁頛匧�隞颱�銝𠹺�������霅� Token �鞟�摰匧��扼����� 100K tokens �唾孛�澆�霅艾��
3. **�芸� .geminiignore ���**: `/aa-new-project` �啣� Step 1.5嚗��憪见�撠����䌊�訫遣蝡� `.geminiignore`嚗𣬚Ⅱ靽脲��𧢲鰵撠��敺䂿洵銝�憭拙停�堒�靽肽風��
4. **Windows cp950 �詨捆**: ���� CLI 頛詨枂�寧鍂 ASCII-safe 璅躰� + UTF-8 撘瑕�頛詨枂嚗諹圾瘙箇�擃𥪯葉�� Windows 銝讠� emoji crash��

### �� �𣈯枤�豢� (Impact)
- **z:\ac 靽桀儔��**: 512 MB / 16,888 瑼娍� �� Token ��� (800K+ tokens)
- **z:\ac 靽桀儔敺�**: `.geminiignore` �㘾膄敺��蝝Ｗ� ~13 MB �笔�蝣� �� 摰匧�蝭��

### �� �啣�/靽格㺿��辣 (@file:)
- `scripts/context_guard.py`: Context Guard �詨����撘閙� (220 lines)��
- `.geminiignore`: AutoAgent-TW 撌乩��� Antigravity 蝝Ｗ��㘾膄閬誩���
- `z:\ac\.geminiignore`: OpenClaw 撌乩����單�靽桀儔��
- `_agents/workflows/aa-plan.md`: �啣� Step 0 Context Guard pre-scan��
- `_agents/workflows/aa-new-project.md`: �啣� Step 1.5 �芸���� .geminiignore��
- `.planning/phases/123-context-guard/CONTEXT.md`: �孵������身閮�捱蝑硔��
- `.planning/phases/123-context-guard/GUARD-REPORT.md`: 摰匧�����勗� (ALL PASS)��
- `.planning/phases/123-context-guard/QA-REPORT.md`: ��釭撽𡑒��勗� (7/7 UAT PASS)��

### �� 摰匧��� (Security)
- Guardian Scan: ALL PASS (�嗆援瞍譌��妟瘜典�憸券麬)
- 1 �� LOW-risk finding: `shell=True` �潮��� `npm.cmd install` �賭誘嚗�歇璅躰酉嚗�


## [v2.4.0-final-bridge] - 2026-04-04

### �� �啣��蠘� (Key Features)
1. **IDE-Bridge ��誘頧厩䔄 (Brain Delegation Mode)**: 撖行鴌�瑕� FastAPI 敺𣬚垢�� `aa-bridge` 隞��隡箸��具���閮勗��� AI 隞�� (憒� OpenClaw) �∠葦摮睃� Antigravity IDE �批遣�� AI �函��賢�嚗諹圾瘙箸𧋦�� API Key 蝻箏仃��楊��𤌍璅∪��曹澈�����
2. **OpenClaw �冽䲮雿漤��� (Standalone Decoupling)**: 摰㕑�蝔见��曉銁�舀� OpenClaw �詨�����钅�蝵脯��䌊�蓥耨敺� Metadata �箏仃��′蝺函Ⅳ頝臬�靘肽陷嚗�遣蝡见抅�� `OPENCLAW_HOME` ��虾蝘餅��扳沲瑽卝��
3. **�典���誘��楲�� (CLI Ecosystem)**: �啣� `autoagent` (銝餅綉)��openclaw-skills` (���賜恣��) �� `aa-bridge` (憭扯�銝剛�) 銝匧之�詨���誘嚗䔶蒂�芸�閮餃��喟頂蝯� PATH��
4. **AutoSkills �芣��脣�撘閙� (Evolution Engine)**: 撖行鴌�刻䌊�閧����賢�瑼Ｚ��滨𤩎璈笔���頂蝯望���綉���賣��毺�嚗𣬚訜雿擧䲰 85% ��䌊�訫��閖�脣�敺芰兛隞乩耨鋆𦦵撩�瑯��

### �� �詨���辣�湔鰵 (@file:)
- `scripts/aa_installer_logic.py`: 憭批��湔鰵摰㕑��讛摩嚗���急瓲敹� `src/` �函蔡��penClaw �啣��𡝗鼧鞎肽��典���誘閮餃���
- `src/bridge/ai_proxy.py`: IDE-Bridge �詨�隞��撖虫���
- `aa-bridge.cmd` & `openclaw-skills.cmd`: �典��笔��單𧋦��
- `src/agents/skills/skill_metrics.py`: ���賢�摨瑕漲餈質馱�詨���
- `src/cron/skill_evolution.py`: ���質䌊�閖�脣�撘閙���
- `.planning/phases/122-openclaw-bridge-installer/`: �𠉛䔄閮�𧞄���霅匧𥼚�� (PLAN/QA)��

## [v2.3.0-autoskills-security] - 2026-04-04

### �� �啣��蠘� (Key Features)
1. **IRA 5 蝝𡁏��鞟頂蝯� (Interactive Requirement Analysis)**: 撱箇��閙�撌亙�憸券麬蝞∪��㗛���𣈲�� 5 蝝𡁻◢�芸�蝝� (Fatal, High, Medium, Low, Read)嚗屸�撠漤�憸券麬�滢��芸�閫貊䔄 LangGraph 銝剜𪃾��犖撌亙祟�詻��
2. **AutoSkills �芸����賢��� (Skill Orchestration)**: 撖行鴌 Skill Package v2 閬讐���𣈲�游抅�� `manifest.json` ����𣂼恐�𡃏� Zod-like (Pydantic) �𨀣�撽𡑒���
3. **�閙����賜��鞱��𨅯� (Discovery & Generation)**: �𣂷� `skills.discover` �� `skills.generate` 撌亙�嚗諹��寞�隞餃��誩��芸��𨅯��砍𧑐/�删垢���賣��閙��Ｙ�蝚血�閬讐�����賢���
4. **摰匧�瘝嗵�撽𡑒� (Sandbox Tester)**: �典�鋆嘥��芸��㚚�霅㗇��質��綽�蝣箔��單𧋦�瑁�銝滩��箏恐�𦠜��鞟��溻��

### �� �啣�/靽格㺿��辣 (@file:)
- `src/core/state.py` & `src/core/graph.py`: IRA �詨����𧢲��� LangGraph 摰��蝭�暺𠺶��
- `src/core/permission_engine.py`: 撌亙�憸券麬蝑厩�閮餃���葉�琿�頛胯��
- `src/core/skill_manifest.py`: Skill Package v2 Pydantic Schema 摰𡁶儔��
- `src/agents/tools/skills_discover.py` & `src/agents/tools/skills_generate.py`: ���賜䔄�曇����撘閙���
- `src/agents/skills/skill_sandbox_test.py`: ���賢��冽�扯�銵𣬚��閙�撽𡑒��具��
- `src/cli/openclaw_skills.py`: 蝯曹��� AutoSkills 蝞∠��賭誘�� (Discover/Generate/Test)��
- `.planning/phases/120-ira-permission-system/`: 摰峕㟲����潭�瑼� (PLAN/RESEARCH/QA)��

## [v2.2.0-pisrc-resilience] - 2026-04-03

### �� �啣��蠘� (Key Features)
1. **PISRC �芣�靽桀儔獢�沲 (Persistent Issue Self-Review & Correction)**: �箸䲰 LangGraph ������见��嗆�嚗��隞��蝯梢��贝艘����𣈲�游�撅斤��齿�肽� 5-Whys �孵������
2. **Installer 摰匧��批��� (Installer Hardening)**: 敺孵�閫�捱 Windows 銝� `setx` �啣�霈𦠜彍�瑕漲銝𢠃���ID ���隞亙�頝券��桃��𧢲情�梶��𣈯枤�函蔡瞍𤩺���
3. **�唳郊����碶葉�� (Human-in-the-Loop)**: �𣇉��贝䌊�閙�銋��嚗�仃�埈��𥡝絲銝衣�敺�犖撌乩��伐��舀螱�琿�蝥����

### �� �啣�/靽格㺿��辣 (@file:)
- `scripts/resilience/pisrc_graph.py`: PISRC �詨��𣇉�瑽贝�蝭�暺𧼮祕雿栶��
- `scripts/aa_installer_logic.py`: 摰㕑���兛憓�身蝵桅�頛臭耨敺押��
- `_agents/workflows/aa-fix.md`: �券𢒰�寞𦻖 LangGraph PISRC 閮箸𪃾�讛摩��
- `requirements.txt` & `build_requirements.txt`: 撘訫� `langgraph`, `langchain-core` 銝西圾�行���極�瑯��
- `.planning/phases/119-pisrc-installer-integration/`: 摰峕㟲�𠉛䔄�望������

## [v2.1.0-custom-workflow] - 2026-04-02

### �� �啣��蠘� (Key Features)
1. **撌乩�瘚�恥鋆賢�蝟餌絞 (Workflow Customization)**: �誯� `CLAUDE.md` �芸�瘜典���𤌍蝝��閬讐���
2. **�閙��笔𦶢�望��文� (Lifecycle Hooks)**: �舀螱 `.agents/hooks.json` �滨蔭嚗諹䌊�訫嘑銵� Lint��uff ��䌊�蓥耨敺押��
3. **Markdown ���賣�頛� (Skill Loader)**: ��� `.agents/skills/*.md` �閙��游�蝷箇頂蝯望�隞歹��⊿�靽格㺿�詨���
4. **�滚�靽肽風�� (Re-entry Guard)**: �唳郊鈭衤辣�瑁�摰匧��批��綽��脫迫 Hook �⊿�敺芰兛��
5. **蝞∠���誘�� (CLI)**: �啣� `/aa-skill` (���賣䰻��) �� `/aa-hook` (�文�蝞∠�) ��誘��

### �� �啣�/靽格㺿��辣 (@file:)
- `scripts/hooks/hook_manager.py`: �齿� Hook �詨�隞交𣈲�� JSON �滨蔭��
- `scripts/skills/skill_loader.py`: 撖虫� MD ���質圾�鞱��芸��潛𣶹��
- `scripts/config/claude_loader.py`: 撖虫� CLAUDE.md 閬讐�頛匧���
- `scripts/aa_skill_cli.py` & `scripts/aa_hook_cli.py`: 蝞∠� CLI 撌亙���
- `.agents/hooks.json`: �嘥� Hook �滨蔭��辣��
- `CLAUDE.md`: ��𤌍閬讐�蝭�𧋦��
- `.planning1/phases/003-workflow-customization/`: 摰峕㟲����潭�瑼� (CONTEXT/RESEARCH/PLAN/QA/SUMMARY)��

---

## [v1.5.0-v0.3-transparency] - 2026-03-31

### �� �啣��蠘� (Key Features)
1. **�單�閬𤥁死�硋�銵冽踎 (Status Dashboard)**: �𣂷��瑁��脣漲���銝�甇亦𤌍璅躰����钅＊蝷箝��
2. **�閙��瑁�璅� (Execution Tree)**: 雿輻鍂 Mermaid.js �芸�皜脫� ROADMAP.md ����潸楝敺㻫��
3. **�單��亥�瘚� (Live Logs)**: �函�讛汗�其葉�湔𦻖�亦� Agent �衤��亥�嚗�鉄皛穃��閧𧞄��
4. **�𨀣趙�菜葫�� LINE 霅血𥼚 (Stagnation & Alerts)**: 90 蝘鍦嘑銵𣬚��墧�霅血��� LINE Notify �删垢�券����
5. **憭𡁶垢�峕郊 (Backend State Sync)**: Python Backend �峕郊���贝秐 JSON/JS嚗𣬚��� CORS ��楨摮㗛��嗚��

### �� �啣�/靽格㺿��辣 (@file:)
- `.agents/skills/status-notifier/SKILL.md`: ���質牧�舘���������
- `.agents/skills/status-notifier/scripts/status_updater.py`: ���𧢲凒�啗����𧢲��典��詨���
- `.agents/skills/status-notifier/scripts/roadmap_parser.py`: ROADMAP Markdown 頧� Mermaid Parser��
- `.agents/skills/status-notifier/scripts/line_notifier.py`: LINE Notify API �亙藁��
- `.agents/skills/status-notifier/templates/status.html`: 閬𤥁死�� Dashboard �滨垢 (Tailwind + Lucide + Mermaid)��
- `_agents/workflows/aa-progress.md`: 瘜典���銵冽踎�瑟鰵�����憿舐內�讛摩��
- `README.md`: �湔鰵�讠䔄��𧋦鞈������賭�蝝嫘��
- `.planning/`: 摰峕㟲����桃��潭�蝔𧢲�隞� (PROJECT/ROADMAP/STATE/PHASES)��

### �� ��銵梶敦蝭� (Technical Details)
- **CORS Fix**: �∠鍂 Script Inject 璅∪� (`window.AA_STATUS`) 閫�捱 `file://` �𥪜�銝讠�摰匧��折��嗚��
- **Encoding Fix**: �� Windows �啣�撘瑕� Python 雿輻鍂 UTF-8 reconfigure `stdout` 隞交𣈲�渲”��泵�蠘撓�箝��
- **Visual Polish**: �∠鍂 Glassmorphism 閮剛�隤墧�嚗峕���䌊�訫�隞����嘑銵屸�𤩺�摨艾��

---
*Generated by AutoAgent-TW*

## [v3.3.1] - 2026-04-22 (Phase 158.5)
### ?? 核心優化：IDE Memory Stealth Mode
- **架構轉型**: 成功將 Pyrefly LSP 從常駐模式切換為 One-Shot CLI 模式。
- **資源回收**: 常駐記憶體降幅達 95.7% (4.2GB -> 180MB)。
- **技術實作**:
  - exe.disabled 鎖定機制防止 IDE 自動重啟。
  - shadow_check.py v2.0 支援按需自動解鎖與隱形稽核。
  - pyrefly_mode.py 模式管理器。
- **驗證**: QA-REPORT 100% 通過。

## [v3.3.2] - 2026-04-25 (Phase 160)
### AutoCLI Integration (Eye-2 Rust Engine)
- **Integration**: 導入 ashsu/AutoCLI (Rust) 作為 Eye-2 Web 抓取引擎。
- **Performance**: 響應延遲 46.8ms，常駐記憶體 13.4MB (Stealth Mode)。
- **Artifacts**:
  - `autocli_guard.py`: 監控與安全防護。
  - `openclaw/skills/autocli`: 封裝好的 AI Skill。
- **Verification**: QA-REPORT 與 REVIEW-REPORT 全數通過。

---
*Generated by Tom (AutoAgent-TW Ship Workflow)*

## [v3.3.3] - 2026-04-25 (Phase 129 Headless CI/CD)
### Added
- **LogSanitizer**: Zero-Trust log scrubbing for API keys and tokens.
- **Headless Flag**: CLI support for --headless mode, disabling all interactive prompts.
- **Orchestration Guard**: Strict loop limits (max 3) for unattended CI/CD runs.
- **CI/CD Infrastructure**: Multi-stage Dockerfile and GitHub Actions workflow for automated PR reviews.

### Fixed
- Health checks now gracefully skip GUI/Vision modules in headless environments.

### Files
- @file:src/core/security/log_sanitizer.py
- @file:src/harness/cli/main.py
- @file:src/core/orchestration/coordinator.py
- @file:Dockerfile
- @file:.github/workflows/autoagent-review.yml

---

### Phase 163 (2026-04-27)
- 導入 Andrej Karpathy 的 AI Coding 核心原則：Surgical Changes, Verification Contracts, Simplicity.
- 實作 `scripts/diff_scope_check.py` 以確保代碼變更的原子性。
- 統一 `CONTEXT_RULES.md` 規範。

### Phase 164 (2026-04-27)
- **子代理語境隔離 (Subagent Isolation)**：實作 Axis 2 架構。
- 建立專家角色庫 (`subagents.json`, `.agents/personas/`)。
- 升級 `spawn_manager.py` 支援角色感知環境注入。
- 實作 `vfs_guard.py` (邏輯 VFS 沙盒) 與 `rtk_prune.py` (角色感知裁剪)。
- 通過 5 項整合測試，確保權限隔離與 Token 優化有效。

### Hotfix (2026-04-27)
- **編碼衝突修復**: 解決了 `ROADMAP.md`, `STATE.md`, `PROJECT.md` 在 Windows 環境下的 UTF-8 與 CP950 (Big5) 亂碼問題。
- **還原內容**: 從備份 (`planning_orig`) 還原了所有損壞的中文描述。
- **強制規範**: 全面轉換為標準 UTF-8 編碼，防止後續 AI 修改時再次發生 Mojibake。
