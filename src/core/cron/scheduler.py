"""
AI Harness Cron Scheduler
功能：排程任務管理、cron 表達式解析、持久化、執行歷史
版本：v1.0.0
"""
import os
import re
import time
import json
import threading
import queue
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging


class JobKind(Enum):
    ONCE = "once"           # 一次性任務
    CRON = "cron"           # Cron 表達式任務
    INTERVAL = "interval"   # 間隔任務
    HEARTBEAT = "heartbeat"  # 心跳任務


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CronJob:
    """排程任務"""
    id: str
    name: str
    kind: JobKind
    schedule_expr: str  # cron 表達式或間隔秒數
    payload: Dict[str, Any]  # 任務內容
    enabled: bool = True
    created_at: float = 0
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    run_count: int = 0
    fail_count: int = 0
    status: JobStatus = JobStatus.PENDING
    
    # 選項
    timeout_seconds: int = 300
    retry_count: int = 0
    retry_delay_seconds: int = 60
    notification: bool = False
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class JobRun:
    """任務執行記錄"""
    id: str
    job_id: str
    started_at: float
    completed_at: Optional[float] = None
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0


class CronParser:
    """
    Cron 表達式解析器
    
    支援標準 5 欄位 cron：
    ┌───────────── 分鐘 (0-59)
    │ ┌──────────── 小時 (0-23)
    │ │ ┌────────── 日 (1-31)
    │ │ │ ┌──────── 月 (1-12)
    │ │ │ │ ┌────── 星期 (0-6, 0=星期日)
    │ │ │ │ │
    * * * * *
    """
    
    FIELDS = ['minute', 'hour', 'day', 'month', 'weekday']
    
    def __init__(self, expr: str):
        self.expr = expr.strip()
        self.parts = self._parse()
    
    def _parse(self) -> Dict[str, List[int]]:
        """解析 cron 表達式"""
        parts = self.expr.split()
        
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {self.expr}")
        
        result = {}
        for i, (field_name, value) in enumerate(zip(self.FIELDS, parts)):
            result[field_name] = self._parse_field(value, field_name)
        
        return result
    
    def _parse_field(self, value: str, field_name: str) -> List[int]:
        """解析單個欄位"""
        values = set()
        
        # 處理特殊字元
        if value == '*':
            return self._get_range(field_name)
        
        # 處理列表
        for part in value.split(','):
            # 處理範圍
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                values.update(range(start, end + 1))
            # 處理步進
            elif '/' in part:
                range_part, step = part.split('/')
                step = int(step)
                
                if range_part == '*':
                    base = list(self._get_range(field_name))
                elif '-' in range_part:
                    start, end = range_part.split('-')
                    base = list(range(int(start), int(end) + 1))  # type: ignore[arg-type]
                else:
                    base = [int(range_part)]
                
                for i, v in enumerate(base):
                    if i % step == 0:
                        values.add(v)
            # 單一值
            else:
                values.add(int(part))
        
        return sorted(list(values))
    
    def _get_range(self, field_name: str) -> List[int]:
        """取得欄位的有效範圍"""
        ranges = {
            'minute': (0, 59),
            'hour': (0, 23),
            'day': (1, 31),
            'month': (1, 12),
            'weekday': (0, 6)
        }
        start, end = ranges[field_name]
        return list(range(start, end + 1))
    
    def matches(self, t: Optional[time.struct_time] = None) -> bool:
        """檢查指定時間是否匹配"""
        if t is None:
            t = time.localtime()
        
        # 分鐘
        if t.tm_min not in self.parts['minute']:
            return False
        
        # 小時
        if t.tm_hour not in self.parts['hour']:
            return False
        
        # 日
        if t.tm_mday not in self.parts['day']:
            return False
        
        # 月
        if t.tm_mon not in self.parts['month']:
            return False
        
        # 星期
        if t.tm_wday not in self.parts['weekday']:
            return False
        
        return True
    
    def next_run(self, after: Optional[float] = None) -> Optional[float]:
        """計算下一次執行的時間戳"""
        if after is None:
            after = time.time()
        
        t = time.localtime(after)
        
        # 最多往前推 1 年
        for _ in range(366 * 24 * 60):
            # 每分鐘往前推
            t = time.localtime(time.mktime(t) + 60)
            
            if self.matches(t):
                return time.mktime(t)
        
        return None


class CronScheduler:
    """
    Cron Scheduler - 任務排程器
    
    功能：
    - Cron 表達式解析
    - 一次性/循環任務
    - 任務持久化
    - 執行歷史記錄
    - 執行緒安全
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, storage_path: Path, config: Optional[Dict] = None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {}
        self.logger = logging.getLogger("harness.cron")
        
        # 任務註冊表
        self.jobs: Dict[str, CronJob] = {}
        
        # 執行歷史
        self.runs: List[JobRun] = []
        self.max_runs_history = self.config.get('max_runs_history', 1000)
        
        # 執行器回呼
        self.executors: Dict[str, Callable] = {}
        
        # 執行緒狀態
        self.running = False
        self._lock = threading.RLock()
        
        # 事件佇列
        self.event_queue: queue.Queue = queue.Queue()
        
        # 載入已存在的任務
        self._load_jobs()
    
    def _job_file(self, job_id: str) -> Path:
        """取得任務檔案路徑"""
        key_hash = hashlib.md5(job_id.encode()).hexdigest()[:8]
        return self.storage_path / f"job_{key_hash}.json"
    
    def add(self, 
            name: str,
            kind: JobKind,
            schedule_expr: str,
            payload: Dict[str, Any],
            timeout_seconds: int = 300,
            retry_count: int = 0,
            notification: bool = False) -> str:
        """
        新增排程任務
        
        Args:
            name: 任務名稱
            kind: 任務類型
            schedule_expr: 排程表達式
            payload: 任務內容（包含執行指令）
            timeout_seconds: 執行超時
            retry_count: 重試次數
            notification: 是否通知
        
        Returns:
            任務 ID
        """
        job_id = f"job_{hashlib.md5(f'{name}{time.time()}'.encode()).hexdigest()[:12]}"
        
        job = CronJob(
            id=job_id,
            name=name,
            kind=kind,
            schedule_expr=schedule_expr,
            payload=payload,
            created_at=time.time(),
            timeout_seconds=timeout_seconds,
            retry_count=retry_count,
            notification=notification
        )
        
        # 計算下次執行時間
        if kind == JobKind.CRON:
            parser = CronParser(schedule_expr)
            job.next_run = parser.next_run()
        elif kind == JobKind.INTERVAL:
            job.next_run = time.time() + float(schedule_expr)
        
        with self._lock:
            self.jobs[job_id] = job
            self._save_job(job)
        
        self.logger.info(f"Added job: {name} ({job_id})")
        
        return job_id
    
    def remove(self, job_id: str) -> bool:
        """移除任務"""
        with self._lock:
            if job_id not in self.jobs:
                return False
            
            del self.jobs[job_id]
            
            # 刪除檔案
            path = self._job_file(job_id)
            if path.exists():
                path.unlink()
            
            self.logger.info(f"Removed job: {job_id}")
            return True
    
    def enable(self, job_id: str) -> bool:
        """啟用任務"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                job.enabled = True
                self._save_job(job)
                return True
            return False
    
    def disable(self, job_id: str) -> bool:
        """停用任務"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                job.enabled = False
                self._save_job(job)
                return True
            return False
    
    def run(self, job_id: str, now: Optional[float] = None) -> Optional[JobRun]:
        """
        立即執行任務
        
        Args:
            job_id: 任務 ID
            now: 執行時間戳
        
        Returns:
            JobRun 執行記錄
        """
        if now is None:
            now = time.time()
        
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
        
        # 建立執行記錄
        run = JobRun(
            id=f"run_{hashlib.md5(f'{job_id}{now}'.encode()).hexdigest()[:12]}",
            job_id=job_id,
            started_at=now,
            status=JobStatus.RUNNING
        )
        
        self.logger.info(f"Running job: {job.name} ({job_id})")
        
        try:
            # 取得執行器
            executor = self.executors.get(job.kind.value)
            
            if executor:
                result = executor(job, job.payload)
                run.result = result
                run.status = JobStatus.COMPLETED
            else:
                # 沒有執行器，使用預設執行
                result = self._execute_default(job, job.payload)
                run.result = result
                run.status = JobStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Job execution failed: {e}")
            run.status = JobStatus.FAILED
            run.error = str(e)
            
            # 重試
            if job.retry_count > 0 and job.fail_count < job.retry_count:
                self.logger.info(f"Scheduling retry for {job.name}")
                job.fail_count += 1
                job.next_run = time.time() + job.retry_delay_seconds
            else:
                job.fail_count += 1
        
        finally:
            run.completed_at = time.time()
            run.duration_ms = (run.completed_at - run.started_at) * 1000
            
            # 更新任務統計
            job.last_run = run.started_at
            job.run_count += 1
            
            # 計算下次執行時間
            if job.kind == JobKind.CRON:
                parser = CronParser(job.schedule_expr)
                job.next_run = parser.next_run()
            elif job.kind == JobKind.INTERVAL:
                job.next_run = time.time() + float(job.schedule_expr)
            
            # 保存
            self._save_job(job)
            self._add_run(run)
        
        return run
    
    def _execute_default(self, job: CronJob, payload: Dict[str, Any]) -> Any:
        """預設執行器"""
        action = payload.get('action', 'echo')
        
        if action == 'echo':
            return {"status": "ok", "message": payload.get('message', 'Job executed')}
        
        elif action == 'exec':
            # 執行命令
            cmd = payload.get('command', '')
            if not cmd:
                raise ValueError("No command specified")
            
            import subprocess
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=job.timeout_seconds
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        elif action == 'script':
            # 執行 Python 腳本
            script = payload.get('script', '')
            if not script:
                raise ValueError("No script specified")
            
            exec(script, {'job': job, 'payload': payload})
            return {"status": "ok"}
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _load_jobs(self):
        """載入所有任務"""
        for path in self.storage_path.glob("job_*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 轉換 enum
                    if 'kind' in data:
                        data['kind'] = JobKind(data['kind'])
                    if 'status' in data:
                        data['status'] = JobStatus(data['status'])
                    
                    job = CronJob(**data)
                    self.jobs[job.id] = job
                    
            except Exception as e:
                self.logger.warning(f"Failed to load job {path}: {e}")
    
    def _save_job(self, job: CronJob):
        """持久化任務"""
        path = self._job_file(job.id)
        data = asdict(job)
        
        # 轉換 enum 為字串
        data['kind'] = job.kind.value
        data['status'] = job.status.value
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _add_run(self, run: JobRun):
        """新增執行記錄"""
        self.runs.append(run)
        
        # 限制歷史長度
        if len(self.runs) > self.max_runs_history:
            self.runs = self.runs[-self.max_runs_history:]
    
    def register_executor(self, kind: str, executor: Callable):
        """註冊執行器"""
        self.executors[kind] = executor
    
    def list_jobs(self, 
                  enabled_only: bool = False,
                  status: Optional[JobStatus] = None) -> List[Dict[str, Any]]:
        """列出所有任務"""
        with self._lock:
            result = []
            
            for job in self.jobs.values():
                if enabled_only and not job.enabled:
                    continue
                
                if status and job.status != status:
                    continue
                
                result.append({
                    'id': job.id,
                    'name': job.name,
                    'kind': job.kind.value,
                    'schedule': job.schedule_expr,
                    'enabled': job.enabled,
                    'status': job.status.value,
                    'run_count': job.run_count,
                    'fail_count': job.fail_count,
                    'last_run': job.last_run,
                    'next_run': job.next_run,
                    'created_at': job.created_at
                })
            
            return result
    
    def list_runs(self, job_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """列出執行歷史"""
        runs = self.runs
        
        if job_id:
            runs = [r for r in runs if r.job_id == job_id]
        
        runs = runs[-limit:]
        
        return [
            {
                'id': r.id,
                'job_id': r.job_id,
                'started_at': r.started_at,
                'completed_at': r.completed_at,
                'status': r.status.value,
                'duration_ms': r.duration_ms,
                'error': r.error
            }
            for r in runs
        ]
    
    def start(self):
        """啟動排程器"""
        self.running = True
        
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="Cron-Scheduler"
        )
        self._scheduler_thread.start()
        
        self.logger.info("Cron scheduler started")
    
    def stop(self):
        """停止排程器"""
        self.running = False
        self.logger.info("Cron scheduler stopped")
    
    def _scheduler_loop(self):
        """排程主循環"""
        while self.running:
            try:
                now = time.time()
                
                with self._lock:
                    for job in self.jobs.values():
                        if not job.enabled:
                            continue
                        
                        if job.next_run and now >= job.next_run:
                            # 準備執行
                            self.event_queue.put(('run', job.id))
                            # 立即更新下次執行時間
                            if job.kind == JobKind.ONCE:
                                job.enabled = False
                            elif job.kind == JobKind.CRON:
                                parser = CronParser(job.schedule_expr)
                                job.next_run = parser.next_run()
                            elif job.kind == JobKind.INTERVAL:
                                job.next_run = now + float(job.schedule_expr)
                
                # 處理事件
                while True:
                    try:
                        event = self.event_queue.get_nowait()
                        if event[0] == 'run':
                            self.run(event[1])
                    except queue.Empty:
                        break
                
                # 每分鐘檢查一次
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)


def main():
    """測試"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CronScheduler(Path(tmpdir) / "cron")
        
        # 新增 cron 任務
        job_id = scheduler.add(
            name="Every minute test",
            kind=JobKind.CRON,
            schedule_expr="* * * * *",
            payload={"action": "echo", "message": "Hello from cron!"}
        )
        print(f"Added job: {job_id}")
        
        # 列出任務
        print("\n=== Jobs ===")
        for job in scheduler.list_jobs():
            print(f"  {job['name']}: {job['schedule']} (next: {job['next_run']})")
        
        # 立即執行
        print("\n=== Running job ===")
        run = scheduler.run(job_id)
        print(f"Result: {run.result if run else 'None'}")
        
        # 列出歷史
        print("\n=== Run history ===")
        for r in scheduler.list_runs():
            print(f"  {r['status']} - {r['duration_ms']:.1f}ms")


if __name__ == '__main__':
    main()
