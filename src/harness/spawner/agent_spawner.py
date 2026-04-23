"""
AI Harness Agent Spawner
功能：子代理管理、並行執行、任務分派
版本：v1.0.0
"""
import os
import sys
import time
import json
import uuid
import queue
import threading
import subprocess
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AgentRuntime(Enum):
    SUBAGENT = "subagent"    # OpenClaw subagent session
    ACP = "acp"             # ACP protocol (Codex/Pi)
    PROCESS = "process"     # 獨立行程


@dataclass
class AgentConfig:
    """Agent 配置"""
    agent_id: str
    prompt: str
    runtime: AgentRuntime = AgentRuntime.SUBAGENT
    model: Optional[str] = None
    timeout_seconds: int = 300
    max_retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Spawn 選項
    mode: str = "run"  # "run" (one-shot) | "session" (persistent)
    label: Optional[str] = None
    cwd: Optional[str] = None
    thinking: Optional[str] = None  # "on" | "off"
    thread: bool = False


@dataclass
class AgentResult:
    """Agent 執行結果"""
    agent_id: str
    status: AgentStatus
    started_at: float
    completed_at: Optional[float] = None
    duration_ms: float = 0
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None


class AgentSpawner:
    """
    Agent Spawner - 子代理管理系統
    
    功能：
    - Spawn 子代理（subagent / acp / process）
    - 並行執行控制
    - 任務超時處理
    - 結果收集
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, workspace: Path, config: Optional[Dict] = None):
        self.workspace = Path(workspace)
        self.config = config or {}
        self.logger = logging.getLogger("harness.spawner")
        
        # 運行中的 Agents
        self.agents: Dict[str, AgentConfig] = {}
        self.results: Dict[str, AgentResult] = {}
        
        # 結果佇列
        self.result_queue: queue.Queue = queue.Queue()
        
        # 並行控制
        self._lock = threading.RLock()
        self._max_parallel = self.config.get('max_parallel', 3)
        self._running_count = 0
        
        # 執行緒
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
    
    def spawn(self,
              prompt: str,
              runtime: AgentRuntime = AgentRuntime.SUBAGENT,
              model: Optional[str] = None,
              timeout: int = 300,
              parallel: int = 1,
              mode: str = "run",
              **kwargs) -> Dict[str, Any]:
        """
        Spawn 子代理
        
        Args:
            prompt: 代理任務提示
            runtime: 執行環境
            model: 模型名稱
            timeout: 超時秒數
            parallel: 並行數量
            mode: "run" 或 "session"
            **kwargs: 其他選項
        
        Returns:
            Spawn 結果
        """
        if parallel > self._max_parallel:
            parallel = self._max_parallel
        
        spawned = []
        
        for i in range(parallel):
            agent_id = f"agent_{uuid.uuid4().hex[:12]}"
            
            config = AgentConfig(
                agent_id=agent_id,
                prompt=prompt,
                runtime=runtime,
                model=model,
                timeout_seconds=timeout,
                mode=mode,
                metadata={str(k): v for k, v in kwargs.items()}  # type: ignore[arg-type]
            )
            
            with self._lock:
                self.agents[agent_id] = config
                self._running_count += 1
            
            # 啟動執行緒
            thread = threading.Thread(
                target=self._run_agent,
                args=(agent_id,),
                daemon=True,
                name=f"Agent-{agent_id[:8]}"
            )
            thread.start()
            
            spawned.append({
                'agent_id': agent_id,
                'runtime': runtime.value,
                'mode': mode
            })
        
        self._ensure_worker()
        
        return {
            'spawned': spawned,
            'count': len(spawned),
            'mode': mode
        }
    
    def _ensure_worker(self):
        """確保工作執行緒運行"""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._result_worker,
            daemon=True,
            name="AgentResult-Worker"
        )
        self._worker_thread.start()
    
    def _run_agent(self, agent_id: str):
        """執行 Agent"""
        config = self.agents.get(agent_id)
        if not config:
            return
        
        started_at = time.time()
        result = AgentResult(
            agent_id=agent_id,
            status=AgentStatus.RUNNING,
            started_at=started_at
        )
        
        self.logger.info(f"Starting agent: {agent_id}")
        
        try:
            if config.runtime == AgentRuntime.SUBAGENT:
                output = self._run_subagent(config)
            elif config.runtime == AgentRuntime.ACP:
                output = self._run_acp(config)
            elif config.runtime == AgentRuntime.PROCESS:
                output = self._run_process(config)
            else:
                output = self._run_default(config)
            
            result.status = AgentStatus.COMPLETED
            result.output = output
            
        except subprocess.TimeoutExpired:
            result.status = AgentStatus.TIMEOUT
            result.error = f"Agent timed out after {config.timeout_seconds}s"
            
        except Exception as e:
            result.status = AgentStatus.FAILED
            result.error = str(e)
            self.logger.error(f"Agent {agent_id} failed: {e}")
        
        finally:
            result.completed_at = time.time()
            result.duration_ms = (result.completed_at - started_at) * 1000
            
            self.results[agent_id] = result
            self.result_queue.put(result)
            
            with self._lock:
                self._running_count -= 1
            
            self.logger.info(f"Agent {agent_id} finished: {result.status.value}")
    
    def _run_subagent(self, config: AgentConfig) -> str:
        """透過 OpenClaw sessions_spawn 執行"""
        # 這裡呼叫 OpenClaw 的 sessions_spawn API
        # 由於是獨立的 Python 程式，使用 subprocess 呼叫 openclaw CLI
        cmd = [
            sys.executable, "-m", "openclaw",
            "agent", "spawn",
            "--prompt", config.prompt,
            "--mode", config.mode
        ]
        
        if config.model:
            cmd.extend(["--model", config.model])
        
        if config.label:
            cmd.extend(["--label", config.label])
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds,
            cwd=self.workspace
        )
        
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or f"Exit code: {proc.returncode}")
        
        return proc.stdout
    
    def _run_acp(self, config: AgentConfig) -> str:
        """透過 ACP 執行（Codex/Pi）"""
        cmd = [
            "codex",  # 或 "pi"
            "--prompt", config.prompt,
            "--non-interactive"
        ]
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds
        )
        
        return proc.stdout
    
    def _run_process(self, config: AgentConfig) -> str:
        """作為獨立行程執行"""
        script_path = self.workspace / "temp" / f"agent_{config.agent_id}.py"
        script_path.parent.mkdir(exist_ok=True)
        
        # 生成腳本
        script_content = f'''"""
Agent: {config.agent_id}
Task: {config.prompt[:100]}
"""
import sys

def main():
    print("Agent task: {config.prompt}")
    # 在此實作代理邏輯
    # ...

if __name__ == "__main__":
    main()
'''
        script_path.write_text(script_content, encoding='utf-8')
        
        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=config.timeout_seconds,
                cwd=self.workspace
            )
            
            return proc.stdout
        finally:
            if script_path.exists():
                script_path.unlink()
    
    def _run_default(self, config: AgentConfig) -> str:
        """預設執行（直接返回成功）"""
        return json.dumps({
            "status": "ok",
            "agent_id": config.agent_id,
            "prompt": config.prompt[:100]
        })
    
    def _result_worker(self):
        """結果收集執行緒"""
        while self._running:
            try:
                result = self.result_queue.get(timeout=1)
                self._handle_result(result)
            except queue.Empty:
                continue
    
    def _handle_result(self, result: AgentResult):
        """處理 Agent 結果"""
        self.logger.info(f"Result for {result.agent_id}: {result.status.value}")
    
    def list_agents(self, 
                   status: Optional[AgentStatus] = None) -> List[Dict[str, Any]]:
        """列出 Agents"""
        with self._lock:
            result = []
            
            for agent_id, config in self.agents.items():
                res = self.results.get(agent_id)
                
                if status and res and res.status != status:
                    continue
                
                info = {
                    'agent_id': agent_id,
                    'runtime': config.runtime.value,
                    'mode': config.mode,
                    'prompt': config.prompt[:100]
                }
                
                if res:
                    info["status"] = str(res.status.value)
                    info["duration_ms"] = str(float(res.duration_ms))  # type: ignore[assignment]
                    info["output"] = str(res.output) if res.output else ""
                    info["error"] = str(res.error) if res.error else ""  # type: ignore[assignment]
                else:
                    info['status'] = AgentStatus.RUNNING.value if agent_id in self.agents else 'unknown'
                
                result.append(info)
            
            return result
    
    def get_result(self, agent_id: str) -> Optional[AgentResult]:
        """取得 Agent 結果"""
        return self.results.get(agent_id)
    
    def cancel(self, agent_id: str) -> bool:
        """取消 Agent"""
        # 對於正在運行的 Agent，標記為取消
        if agent_id in self.agents:
            config = self.agents[agent_id]
            # 這裡需要實作實際的取消邏輯
            return True
        return False
    
    def wait(self, agent_ids: Optional[List[str]] = None, timeout: Optional[float] = None) -> List[AgentResult]:
        """
        等待 Agent 完成
        
        Args:
            agent_ids: 要等待的 Agent ID 列表，None 表示全部
            timeout: 超時秒數
        
        Returns:
            結果列表
        """
        deadline = time.time() + timeout if timeout else None
        results = []
        pending = set(agent_ids) if agent_ids else set(self.agents.keys())
        
        while pending:
            remaining = deadline - time.time() if deadline else None
            if remaining and remaining <= 0:
                break
            
            try:
                result = self.result_queue.get(timeout=min(remaining, 1) if remaining else 1)
                
                if agent_ids is None or result.agent_id in agent_ids:
                    results.append(result)
                    pending.discard(result.agent_id)
                    
            except queue.Empty:
                continue
        
        return results
    
    def stop(self):
        """停止 Spawner"""
        self._running = False
        for agent_id in list(self.agents.keys()):
            self.cancel(agent_id)
        self.logger.info("AgentSpawner stopped")


def main():
    """測試"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        spawner = AgentSpawner(Path(tmpdir))
        
        # Spawn 一個測試 Agent
        result = spawner.spawn(
            prompt="測試任務：說 Hello",
            runtime=AgentRuntime.PROCESS,
            timeout=10,
            parallel=2
        )
        
        print(f"Spawned {result['count']} agents:")
        for a in result['spawned']:
            print(f"  {a['agent_id']}")
        
        # 等待完成
        results = spawner.wait(timeout=15)
        print(f"\nResults:")
        for r in results:
            print(f"  {r.agent_id}: {r.status.value} ({r.duration_ms:.1f}ms)")
            if r.output:
                print(f"    {r.output[:100]}")


if __name__ == '__main__':
    main()
