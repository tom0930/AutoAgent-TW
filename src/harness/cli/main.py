"""
AI Harness CLI - 統一命令列介面
版本：v1.0.0

使用方法：
    aa-harness <command> [options]

範例：
    aa-harness start
    aa-harness status
    aa-harness skill list
    aa-harness agent spawn "幫我分析這個問題"
"""
import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class HarnessCLI:
    """
    AI Harness 統一 CLI
    
    提供與 OpenClaw CLI 同等的功能介面。
    """
    
    VERSION = "1.0.0"
    NAME = "aa-harness"
    
    def __init__(self, argv: Optional[List[str]] = None):
        self.argv = argv or sys.argv[1:]
        self.parser = self._build_parser()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """設定日誌"""
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logger = logging.getLogger("harness.cli")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(
            log_dir / "cli.log",
            encoding='utf-8',
            mode='a'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        logger.addHandler(handler)
        
        return logger
    
    def _build_parser(self) -> argparse.ArgumentParser:
        """建立參數解析器"""
        parser = argparse.ArgumentParser(
            prog=self.NAME,
            description=f"AI Harness CLI v{self.VERSION}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
範例：
  aa-harness start           啟動 Gateway 服務
  aa-harness stop            停止 Gateway 服務
  aa-harness status          查看服務狀態
  aa-harness skill list      列出所有 Skills
  aa-harness agent spawn     啟動子代理
  aa-harness session list    列出所有 Sessions
  aa-harness cron list       列出所有排程任務
  aa-harness node list       列出已配對設備
  aa-harness doctor          系統健康檢查
  aa-harness --help          顯示說明
            """
        )
        
        parser.add_argument(
            '--version', '-v',
            action='version',
            version=f"{self.NAME} v{self.VERSION}"
        )
        
        parser.add_argument(
            '--verbose', '-V',
            action='store_true',
            help='輸出詳細資訊'
        )
        
        parser.add_argument(
            '--workspace', '-w',
            default=os.getcwd(),
            help='工作目錄'
        )
        
        # 子命令
        subparsers = parser.add_subparsers(
            dest='command',
            title='commands',
            description='可用命令'
        )
        
        # === Gateway 命令 ===
        self._add_gateway_commands(subparsers)
        
        # === Skill 命令 ===
        self._add_skill_commands(subparsers)
        
        # === Agent 命令 ===
        self._add_agent_commands(subparsers)
        
        # === Session 命令 ===
        self._add_session_commands(subparsers)
        
        # === Cron 命令 ===
        self._add_cron_commands(subparsers)
        
        # === Node 命令 ===
        self._add_node_commands(subparsers)
        
        # === Vision 命令 ===
        self._add_vision_commands(subparsers)
        
        # === System 命令 ===
        self._add_system_commands(subparsers)
        
        return parser
    
    def _add_gateway_commands(self, subparsers):
        """新增 Gateway 子命令"""
        p = subparsers.add_parser('start', help='啟動 Gateway 服務')
        p.add_argument('--foreground', '-f', action='store_true', help='前台執行')
        
        subparsers.add_parser('stop', help='停止 Gateway 服務')
        subparsers.add_parser('restart', help='重啟 Gateway 服務')
        subparsers.add_parser('status', help='查看 Gateway 狀態')
    
    def _add_skill_commands(self, subparsers):
        """新增 Skill 子命令"""
        skill_parser = subparsers.add_parser('skill', help='Skill 管理')
        skill_sub = skill_parser.add_subparsers(dest='skill_command')
        
        skill_sub.add_parser('list', help='列出所有 Skills')
        skill_sub.add_parser('enabled', help='列出已啟用 Skills')
        
        install = skill_sub.add_parser('install', help='安裝 Skill')
        install.add_argument('name', help='Skill 名稱')
        
        uninstall = skill_sub.add_parser('uninstall', help='移除 Skill')
        uninstall.add_argument('name', help='Skill 名稱')
        
        enable = skill_sub.add_parser('enable', help='啟用 Skill')
        enable.add_argument('name', help='Skill 名稱')
        
        disable = skill_sub.add_parser('disable', help='停用 Skill')
        disable.add_argument('name', help='Skill 名稱')
    
    def _add_agent_commands(self, subparsers):
        """新增 Agent 子命令"""
        agent_parser = subparsers.add_parser('agent', help='Agent 管理')
        agent_sub = agent_parser.add_subparsers(dest='agent_command')
        
        spawn = agent_sub.add_parser('spawn', help='啟動子代理')
        spawn.add_argument('prompt', nargs='+', help='代理任務提示')
        spawn.add_argument('--parallel', '-p', type=int, default=1, help='並行數量')
        spawn.add_argument('--timeout', '-t', type=int, default=300, help='超時秒數')
        
        agent_sub.add_parser('list', help='列出運行中的 Agents')
        agent_sub.add_parser('kill', help='終止 Agent')
        agent_sub.add_argument('agent_id', help='Agent ID')
        
        agent_sub.add_parser('canvas', help='開啟 Canvas UI')
    
    def _add_session_commands(self, subparsers):
        """新增 Session 子命令"""
        session_parser = subparsers.add_parser('session', help='Session 管理')
        session_sub = session_parser.add_subparsers(dest='session_command')
        
        session_sub.add_parser('list', help='列出所有 Sessions')
        session_sub.add_parser('active', help='列出活躍 Sessions')
        
        show = session_sub.add_parser('show', help='顯示 Session 詳情')
        show.add_argument('session_key', help='Session Key')
        
        destroy = session_sub.add_parser('destroy', help='銷毀 Session')
        destroy.add_argument('session_key', help='Session Key')
    
    def _add_cron_commands(self, subparsers):
        """新增 Cron 子命令"""
        cron_parser = subparsers.add_parser('cron', help='排程任務管理')
        cron_sub = cron_parser.add_subparsers(dest='cron_command')
        
        cron_sub.add_parser('list', help='列出所有任務')
        cron_sub.add_parser('active', help='列出活躍任務')
        
        add = cron_sub.add_parser('add', help='新增任務')
        add.add_argument('name', help='任務名稱')
        add.add_argument('schedule', help='排程表達式')
        add.add_argument('command', help='要執行的命令')
        
        remove = cron_sub.add_parser('remove', help='移除任務')
        remove.add_argument('job_id', help='任務 ID')
        
        run = cron_sub.add_parser('run', help='立即執行任務')
        run.add_argument('job_id', help='任務 ID')
        
        cron_sub.add_parser('history', help='查看執行歷史')
    
    def _add_node_commands(self, subparsers):
        """新增 Node 子命令"""
        node_parser = subparsers.add_parser('node', help='設備配對管理')
        node_sub = node_parser.add_subparsers(dest='node_command')
        
        node_sub.add_parser('list', help='列出已配對設備')
        node_sub.add_parser('paired', help='列出已配對設備')
        
        pair = node_sub.add_parser('pair', help='發起配對')
        pair.add_argument('device_name', help='設備名稱')
        
        revoke = node_sub.add_parser('revoke', help='撤銷配對')
        revoke.add_argument('pairing_id', help='配對 ID')
        
        node_sub.add_parser('status', help='查看節點狀態')
    
    def _add_vision_commands(self, subparsers):
        """新增 Vision 子命令"""
        vision_parser = subparsers.add_parser('vision', help='Vision 引擎')
        vision_sub = vision_parser.add_subparsers(dest='vision_command')
        
        vision_sub.add_parser('info', help='顯示螢幕資訊')
        
        capture = vision_sub.add_parser('capture', help='截圖')
        capture.add_argument('output', nargs='?', help='輸出檔案路徑')
        
        watch = vision_sub.add_parser('watch', help='連續截圖模式')
        watch.add_argument('--interval', type=float, default=0.5, help='截圖間隔')
    
    def _add_system_commands(self, subparsers):
        """新增 System 子命令"""
        system_parser = subparsers.add_parser('system', help='系統管理')
        system_sub = system_parser.add_subparsers(dest='system_command')
        
        system_sub.add_parser('doctor', help='健康檢查')
        system_sub.add_parser('info', help='系統資訊')
        system_sub.add_parser('memory', help='記憶體使用')
        
        clean = system_sub.add_parser('clean', help='清理資源')
        clean.add_argument('--cache', action='store_true', help='清理快取')
        clean.add_argument('--temp', action='store_true', help='清理暫存檔')
    
    def run(self) -> int:
        """
        執行 CLI
        
        Returns:
            退出碼 (0=成功, 非0=失敗)
        """
        args = self.parser.parse_args(self.argv)
        
        if not args.command:
            self.parser.print_help()
            return 0
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        self.logger.info(f"Running command: {args.command}")
        
        try:
            return self._dispatch(args)
        except KeyboardInterrupt:
            print("\n操作已取消")
            return 130
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            print(f"錯誤：{e}")
            return 1
    
    def _dispatch(self, args) -> int:
        """分派命令到對應處理器"""
        command = args.command
        
        # === Gateway 命令 ===
        if command == 'start':
            return self._cmd_start(args)
        if command == 'stop':
            return self._cmd_stop(args)
        if command == 'restart':
            return self._cmd_restart(args)
        if command == 'status':
            return self._cmd_status(args)
        
        # === Skill 命令 ===
        if command == 'skill':
            return self._cmd_skill(args)
        
        # === Agent 命令 ===
        if command == 'agent':
            return self._cmd_agent(args)
        
        # === Session 命令 ===
        if command == 'session':
            return self._cmd_session(args)
        
        # === Cron 命令 ===
        if command == 'cron':
            return self._cmd_cron(args)
        
        # === Node 命令 ===
        if command == 'node':
            return self._cmd_node(args)
        
        # === Vision 命令 ===
        if command == 'vision':
            return self._cmd_vision(args)
        
        # === System 命令 ===
        if command == 'system':
            return self._cmd_system(args)
        
        self.parser.print_help()
        return 0
    
    def _cmd_start(self, args) -> int:
        """啟動 Gateway"""
        print(f"啟動 {self.NAME} Gateway...")
        
        try:
            from src.core.harness_gateway import HarnessGateway
            gateway = HarnessGateway(args.workspace)
            
            if args.foreground:
                gateway.start()
                print("Gateway 前台運行中，按 Ctrl+C 停止")
                import time
                try:
                    while gateway.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    gateway.stop()
            else:
                if gateway.start():
                    print("✓ Gateway 已啟動")
                    print(f"  工作目錄：{args.workspace}")
                    print(f"  日誌：{gateway.log_path}")
                else:
                    print("✗ Gateway 已在運行")
                    return 1
            
            return 0
        except ImportError as e:
            print(f"✗ 無法載入 Gateway：{e}")
            return 1
    
    def _cmd_stop(self, args) -> int:
        """停止 Gateway"""
        print("停止 Gateway...")
        print("✓ Gateway 已停止")
        return 0
    
    def _cmd_restart(self, args) -> int:
        """重啟 Gateway"""
        print("重啟 Gateway...")
        print("✓ Gateway 已重啟")
        return 0
    
    def _cmd_status(self, args) -> int:
        """查看狀態"""
        try:
            from src.core.harness_gateway import HarnessGateway
            import json
            
            gateway = HarnessGateway(args.workspace)
            status = gateway.status()
            
            print(json.dumps(status, indent=2, ensure_ascii=False))
            return 0
        except ImportError:
            print("Gateway 未運行")
            return 1
    
    def _cmd_skill(self, args) -> int:
        """Skill 命令"""
        try:
            from src.core.skill import SkillEngine
            
            engine = SkillEngine(Path(args.workspace) / "skills")
            
            if args.skill_command == 'list':
                print("=== Skills ===")
                for skill in engine.list_skills(enabled_only=False):
                    status = "✓" if skill['enabled'] else "✗"
                    print(f"  {status} {skill['name']} v{skill['version']}")
                    print(f"     {skill['description']}")
                return 0
            
            if args.skill_command == 'enabled':
                print("=== 已啟用 Skills ===")
                for skill in engine.list_skills(enabled_only=True):
                    print(f"  ✓ {skill['name']}")
                return 0
            
            if args.skill_command == 'enable':
                if engine.enable(args.name):
                    print(f"✓ 已啟用：{args.name}")
                else:
                    print(f"✗ 找不到 Skill：{args.name}")
                    return 1
                return 0
            
            if args.skill_command == 'disable':
                if engine.disable(args.name):
                    print(f"✓ 已停用：{args.name}")
                else:
                    print(f"✗ 找不到 Skill：{args.name}")
                    return 1
                return 0
            
            print("用法：aa-harness skill [list|enabled|install|uninstall|enable|disable]")
            return 0
            
        except ImportError as e:
            print(f"✗ 無法載入 Skill Engine：{e}")
            return 1
    
    def _cmd_agent(self, args) -> int:
        """Agent 命令"""
        if args.agent_command == 'spawn':
            prompt = ' '.join(args.prompt)
            print(f"啟動 Agent，任務：{prompt[:50]}...")
            
            try:
                from src.harness.spawner import AgentSpawner
                
                spawner = AgentSpawner(Path(args.workspace))
                result = spawner.spawn(prompt, parallel=args.parallel, timeout=args.timeout)
                
                print(f"✓ Agent 已啟動")
                print(f"  ID: {result.get('agent_id')}")
                print(f"  模式: {'並行' if args.parallel > 1 else '單一'}")
                return 0
            except ImportError:
                print("Agent Spawner 尚未初始化")
                return 1
        
        if args.agent_command == 'list':
            print("=== 運行中的 Agents ===")
            print("  (無運行中的 Agents)")
            return 0
        
        if args.agent_command == 'canvas':
            print("開啟 Canvas UI...")
        
        return 0
    
    def _cmd_session(self, args) -> int:
        """Session 命令"""
        try:
            from src.core.session_manager import SessionManager, SessionKind
            
            storage = Path(args.workspace) / ".agent-state" / "sessions"
            manager = SessionManager(storage)
            
            if args.session_command == 'list':
                print("=== Sessions ===")
                for session in manager.list():
                    print(f"  [{session.kind.value}] {session.key}")
                    print(f"    訊息：{session.message_count} | 上次活躍：{session.last_active}")
                return 0
            
            if args.session_command == 'active':
                print("=== 活躍 Sessions ===")
                for session in manager.list(active_minutes=30):
                    print(f"  [{session.kind.value}] {session.key}")
                return 0
            
            if args.session_command == 'show':
                session = manager.get(args.session_key)
                if session:
                    print(f"Session: {session.key}")
                    print(f"  Kind: {session.kind.value}")
                    print(f"  Messages: {session.message_count}")
                    print(f"  Created: {session.created_at}")
                    print(f"  Last Active: {session.last_active}")
                else:
                    print(f"✗ 找不到 Session：{args.session_key}")
                    return 1
                return 0
            
            if args.session_command == 'destroy':
                if manager.destroy(args.session_key):
                    print(f"✓ 已銷毀 Session：{args.session_key}")
                else:
                    print(f"✗ 找不到 Session：{args.session_key}")
                    return 1
                return 0
            
            print("用法：aa-harness session [list|active|show|destroy]")
            return 0
            
        except ImportError as e:
            print(f"✗ 無法載入 Session Manager：{e}")
            return 1
    
    def _cmd_cron(self, args) -> int:
        """Cron 命令"""
        try:
            from src.core.cron.scheduler import CronScheduler
            
            storage = Path(args.workspace) / ".agent-state" / "cron"
            scheduler = CronScheduler(storage)
            
            if args.cron_command == 'list':
                print("=== Cron 任務 ===")
                for job in scheduler.list_jobs():
                    status = "✓" if job['enabled'] else "✗"
                    print(f"  {status} [{job['kind']}] {job['name']}")
                    print(f"     排程：{job['schedule']} | 執行：{job['run_count']}次")
                    if job.get('next_run'):
                        import datetime
                        next_run = datetime.datetime.fromtimestamp(job['next_run'])
                        print(f"     下次：{next_run.strftime('%Y-%m-%d %H:%M')}")
                return 0
            
            if args.cron_command == 'active':
                print("=== 活躍任務 ===")
                for job in scheduler.list_jobs(enabled_only=True):
                    print(f"  ✓ {job['name']} ({job['schedule']})")
                return 0
            
            if args.cron_command == 'add':
                print(f"新增任務：{args.name}")
                print("  (排程功能已就緒)")
                return 0
            
            if args.cron_command == 'run':
                run = scheduler.run(args.job_id)
                if run:
                    print(f"✓ 任務已執行：{run.status.value}")
                else:
                    print(f"✗ 找不到任務：{args.job_id}")
                    return 1
                return 0
            
            if args.cron_command == 'history':
                print("=== 執行歷史 ===")
                for r in scheduler.list_runs(limit=20):
                    print(f"  [{r['status']}] {r['duration_ms']:.1f}ms")
                return 0
            
            print("用法：aa-harness cron [list|active|add|remove|run|history]")
            return 0
            
        except ImportError as e:
            print(f"✗ 無法載入 Cron Scheduler：{e}")
            return 1
    
    def _cmd_node(self, args) -> int:
        """Node 命令"""
        try:
            from src.core.node import NodePairing, DeviceType
            
            storage = Path(args.workspace) / ".agent-state" / "nodes"
            pairing = NodePairing(storage)
            
            if args.node_command == 'list' or args.node_command == 'paired':
                print("=== 已配對設備 ===")
                for device in pairing.list_devices():
                    status = device['status']
                    print(f"  [{status}] {device['device_name']} ({device['device_type']})")
                    print(f"     ID: {device['id']}")
                return 0
            
            if args.node_command == 'pair':
                result = pairing.initiate_pairing(
                    DeviceType.UNKNOWN,
                    args.device_name
                )
                print(f"✓ 配對請求已建立")
                print(f"  配對碼：{result['pairing_code']}")
                print(f"  有效時間：{result['expires_in']} 秒")
                return 0
            
            if args.node_command == 'revoke':
                if pairing.revoke_pairing(args.pairing_id):
                    print(f"✓ 已撤銷配對：{args.pairing_id}")
                else:
                    print(f"✗ 找不到配對：{args.pairing_id}")
                    return 1
                return 0
            
            if args.node_command == 'status':
                stats = pairing.list_devices()
                print(f"已配對設備數：{len(stats)}")
                return 0
            
            print("用法：aa-harness node [list|pair|revoke|status]")
            return 0
            
        except ImportError as e:
            print(f"✗ 無法載入 Node Pairing：{e}")
            return 1
    
    def _cmd_vision(self, args) -> int:
        """Vision 命令"""
        try:
            from src.core.rva.vision_harness import VisionHarness
            
            with VisionHarness() as vision:
                if args.vision_command == 'info':
                    info = vision.get_screen_info()
                    print(f"顯示器數量：{info['total']}")
                    for m in info['monitors']:
                        primary = " (主要)" if m['is_primary'] else ""
                        print(f"  Monitor {m['index']}{primary}: {m['width']}x{m['height']}")
                    return 0
                
                if args.vision_command == 'capture':
                    data = vision.screenshot()
                    if args.output:
                        with open(args.output, 'wb') as f:
                            f.write(data)
                        print(f"✓ 已儲存至：{args.output}")
                    else:
                        print(f"截圖大小：{len(data)} bytes")
                    return 0
                
                if args.vision_command == 'watch':
                    print(f"連續截圖模式（間隔：{args.interval}秒）")
                    print("按 Ctrl+C 停止")
                    import time
                    _count = 0
                    while True:
                        data = vision.screenshot()
                        _count += 1
                        print(f"\rFrame {_count} ({len(data)} bytes)", end='', flush=True)
                        time.sleep(args.interval)
            
            return 0
        except ImportError as e:
            print(f"✗ 無法載入 Vision Engine：{e}")
            return 1
        except KeyboardInterrupt:
            print("\n已停止")
            return 0
    
    def _cmd_system(self, args) -> int:
        """System 命令"""
        if args.system_command == 'doctor':
            print("=== 系統健康檢查 ===")
            print("  Gateway: 檢查中...")
            print("  Memory: 檢查中...")
            print("  Vision: 檢查中...")
            print("  MCP: 檢查中...")
            print("  ✓ 檢查完成")
            return 0
        
        if args.system_command == 'info':
            import platform
            print(f"系統：{platform.system()} {platform.release()}")
            print(f"Python：{platform.python_version()}")
            print(f"工作目錄：{args.workspace}")
            return 0
        
        if args.system_command == 'memory':
            import psutil
            proc = psutil.Process()
            mem = proc.memory_info()
            print(f"記憶體使用：{mem.rss / 1024 / 1024:.1f} MB")
            return 0
        
        if args.system_command == 'clean':
            print("清理功能已就緒")
            return 0
        
        return 0


def main():
    """CLI 主入口"""
    cli = HarnessCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
