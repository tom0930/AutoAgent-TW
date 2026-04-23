"""
AI Harness Gateway - 守護行程服務
功能：啟動時自動初始化所有服務，支援 start/stop/restart/status 命令
版本：v1.0.0
"""
import sys
import os
import time
import json
import signal
import threading
import queue
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ServiceStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class Service:
    id: str
    name: str
    status: ServiceStatus
    started_at: float = 0
    error: Optional[str] = None
    restart_count: int = 0


class HarnessGateway:
    """
    AI Harness Gateway Daemon
    
    這是 autoagent-TW 的核心服務管理器，提供與 OpenClaw Gateway 同等的功能。
    """
    
    VERSION = "1.0.0"
    SERVICE_NAME = "AutoAgent-TW Harness Gateway"
    
    def __init__(self, workspace: Optional[str] = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.running = False
        self.services: Dict[str, Service] = {}
        self.event_queue: queue.Queue = queue.Queue()
        self.start_time: float = 0.0  # Will be set in start()
        
        # 初始化日誌
        self.log_path = self.workspace / "logs" / "gateway.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logging()
        
        # 載入配置
        self.config = self._load_config()
        
        # 設定訊號處理
        self._setup_signal_handlers()
    
    def _setup_logging(self) -> logging.Logger:
        """設定日誌"""
        logger = logging.getLogger("harness.gateway")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        
        # 檔案處理器
        file_handler = logging.FileHandler(
            self.log_path, encoding='utf-8', mode='a'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置"""
        config_path = self.workspace / "config" / "harness.toml"
        default_config = {
            'gateway': {
                'version': self.VERSION,
                'log_level': 'INFO',
                'auto_restart': True,
                'restart_delay': 5,
            },
            'services': {
                'memory': {'enabled': True, 'priority': 1},
                'vision': {'enabled': True, 'priority': 2},
                'mcp': {'enabled': True, 'priority': 3},
                'cron': {'enabled': True, 'priority': 4},
                'security': {'enabled': True, 'priority': 0},
            }
        }
        
        if config_path.exists():
            try:
                import tomllib
                with open(config_path, 'rb') as f:
                    config = tomllib.load(f)
                    # 合併配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except ImportError:
                import tomli
                with open(config_path, 'rb') as f:
                    config = tomli.load(f)
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}, using defaults")
        
        return default_config
    
    def _setup_signal_handlers(self):
        """設定訊號處理"""
        def handle_signal(signum, frame):
            signal_name = signal.Signals(signum).name
            self.logger.info(f"Received signal {signal_name}, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
    
    def start(self) -> bool:
        """啟動 Gateway 服務"""
        if self.running:
            self.logger.warning("Gateway already running")
            return False
        
        self.logger.info("=" * 60)
        self.logger.info(f"Starting {self.SERVICE_NAME} v{self.VERSION}")
        self.logger.info(f"Workspace: {self.workspace}")
        self.logger.info("=" * 60)
        
        self.start_time: float = time.time()
        self.running = True
        
        # 初始化所有服務
        self._init_services()
        
        # 啟動背景工作執行緒
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.name = "Gateway-Worker"
        self._worker_thread.start()
        
        # 啟動健康檢查執行緒
        self._health_thread = threading.Thread(target=self._health_checker, daemon=True)
        self._health_thread.name = "Gateway-Health"
        self._health_thread.start()
        
        self.logger.info("Gateway started successfully")
        self.logger.info(f"Uptime: {self._format_uptime()}")
        
        return True
    
    def _init_services(self):
        """初始化所有子服務"""
        service_defs = [
            ('security', 'Security Sentinel', 0),
            ('memory', 'MemPalace Service', 1),
            ('vision', 'Vision Engine', 2),
            ('mcp', 'MCP Hub', 3),
            ('cron', 'Cron Scheduler', 4),
        ]
        
        for service_id, service_name, priority in service_defs:
            cfg = self.config.get('services', {}).get(service_id, {})
            
            if not cfg.get('enabled', True):
                self.logger.info(f"Skipping disabled service: {service_id}")
                continue
            
            self.logger.info(f"Initializing {service_name}...")
            
            service = Service(
                id=service_id,
                name=service_name,
                status=ServiceStatus.STARTING,
                started_at=time.time()
            )
            
            try:
                # 這裡應該呼叫實際的服務初始化
                # 目前是 placeholder，實際會依賴各服務模組
                self._init_service_module(service_id)
                service.status = ServiceStatus.RUNNING
                self.logger.info(f"  ✓ {service_name} started")
            except Exception as e:
                service.status = ServiceStatus.ERROR
                service.error = str(e)
                self.logger.error(f"  ✗ {service_name} failed: {e}")
            
            self.services[service_id] = service
    
    def _init_service_module(self, service_id: str):
        """初始化具體服務模組"""
        # 根據 service_id 初始化對應模組
        # 這裡是鉤子，實際實作在各服務模組中
        pass
    
    def _worker(self):
        """背景工作執行緒"""
        self.logger.debug("Worker thread started")
        
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
        
        self.logger.debug("Worker thread stopped")
    
    def _handle_event(self, event: Dict[str, Any]):
        """處理事件"""
        event_type = event.get('type', 'unknown')
        
        handlers = {
            'check_health': self._check_health,
            'reload_config': self._reload_config,
            'restart_service': self._restart_service,
            'emergency_stop': self._emergency_stop,
        }
        
        handler = handlers.get(event_type)
        if handler:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def _check_health(self, event: Dict[str, Any]):
        """健康檢查"""
        for service_id, service in self.services.items():
            if service.status == ServiceStatus.RUNNING:
                uptime = time.time() - service.started_at
                self.logger.debug(
                    f"  {service.name}: OK (uptime: {self._format_duration(uptime)})"
                )
    
    def _reload_config(self, event: Dict[str, Any]):
        """重新載入配置"""
        self.logger.info("Reloading configuration...")
        self.config = self._load_config()
        self.logger.info("Configuration reloaded")
    
    def _restart_service(self, event: Dict[str, Any]):
        """重啟服務"""
        service_id = event.get('service_id')
        if service_id in self.services:
            self.logger.info(f"Restarting service: {service_id}")
            self.services[service_id].restart_count += 1
            self._init_service_module(service_id)
    
    def _emergency_stop(self, event: Dict[str, Any]):
        """緊急停止"""
        self.logger.critical("Emergency stop triggered!")
        self.stop()
    
    def _health_checker(self):
        """健康檢查執行緒"""
        while self.running:
            time.sleep(60)  # 每分鐘檢查一次
            
            if not self.running:
                break
            
            self.event_queue.put({'type': 'check_health', 'timestamp': time.time()})
    
    def stop(self):
        """停止 Gateway 服務"""
        self.logger.info("Stopping Gateway...")
        self.running = False
        
        # 優雅關閉所有服務
        for service_id, service in self.services.items():
            service.status = ServiceStatus.STOPPING
            self.logger.info(f"  Stopping {service.name}...")
            # 這裡應該呼叫實際的服務停止邏輯
            service.status = ServiceStatus.STOPPED
        
        self.logger.info("Gateway stopped")
    
    def restart(self) -> bool:
        """重啟 Gateway"""
        self.logger.info("Restarting Gateway...")
        self.stop()
        time.sleep(1)
        return self.start()
    
    def status(self) -> Dict[str, Any]:
        """獲取服務狀態"""
        uptime = time.time() - self.start_time if self.running else 0
        
        services_status = {}
        for service_id, service in self.services.items():
            services_status[service_id] = {
                'name': service.name,
                'status': service.status.value,
                'uptime': time.time() - service.started_at if service.status == ServiceStatus.RUNNING else 0,
                'restart_count': service.restart_count,
                'error': service.error
            }
        
        return {
            'running': self.running,
            'version': self.VERSION,
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_duration(uptime),
            'workspace': str(self.workspace),
            'services': services_status,
            'log_path': str(self.log_path)
        }
    
    def _format_duration(self, seconds: float) -> str:
        """格式化時長"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def _format_uptime(self) -> str:
        """格式化正常運行時間"""
        return self._format_duration(time.time() - self.start_time)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'{HarnessGateway.SERVICE_NAME} v{HarnessGateway.VERSION}'
    )
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status', 'run'],
        help='Gateway command'
    )
    parser.add_argument(
        '--workspace', '-w',
        default=os.getcwd(),
        help='Workspace directory'
    )
    parser.add_argument(
        '--foreground', '-f',
        action='store_true',
        help='Run in foreground (for run command)'
    )
    
    args = parser.parse_args()
    
    gateway = HarnessGateway(args.workspace)
    
    if args.command == 'start':
        if gateway.start():
            print(f"✓ {gateway.SERVICE_NAME} started")
            print(f"  Workspace: {gateway.workspace}")
            print(f"  Log: {gateway.log_path}")
        else:
            print(f"✗ Failed to start (already running?)")
            sys.exit(1)
    
    elif args.command == 'stop':
        gateway.stop()
        print("✓ Gateway stopped")
    
    elif args.command == 'restart':
        if gateway.restart():
            print("✓ Gateway restarted")
        else:
            print("✗ Failed to restart")
            sys.exit(1)
    
    elif args.command == 'status':
        status = gateway.status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.command == 'run':
        # 前台執行模式
        gateway.start()
        print(f"Gateway running in foreground. Press Ctrl+C to stop.")
        try:
            while gateway.running:
                time.sleep(1)
        except KeyboardInterrupt:
            gateway.stop()
            print("\nGateway stopped")


if __name__ == '__main__':
    main()
