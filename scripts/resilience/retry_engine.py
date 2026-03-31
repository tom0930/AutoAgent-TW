"""
Low-Level Retry Engine (Phase 2)
針對 TRANSIENT 等級錯誤使用「指數退避 (Exponential Backoff) + 隨機抖動 (Jitter)」自動重試，不再遇到網路不穩就直接報錯。
"""

import asyncio
import random
import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional, Any, List, Dict
from functools import wraps
from error_classifier import AgentError, ErrorSeverity, ErrorClassifier

# Setting up basic logger for resilience package
logger = logging.getLogger("resilience")

@dataclass
class RetryPolicy:
    """重試策略配置"""
    max_retries: int = 3                    # 最大重試次數
    base_delay: float = 1.0                 # 基礎延遲（秒）
    max_delay: float = 60.0                 # 最大延遲上限
    exponential_base: float = 2.0           # 指數底數
    jitter: bool = True                     # 是否加入隨機抖動
    retryable_severities: List[ErrorSeverity] = field(
        default_factory=lambda: [
            ErrorSeverity.TRANSIENT,
            ErrorSeverity.RECOVERABLE,
        ]
    )

# 各錯誤類型的預設重試策略
DEFAULT_POLICIES = {
    ErrorSeverity.TRANSIENT: RetryPolicy(
        max_retries=5,
        base_delay=1.0,
        max_delay=30.0,
    ),
    ErrorSeverity.RECOVERABLE: RetryPolicy(
        max_retries=2,
        base_delay=2.0,
        max_delay=15.0,
    ),
    ErrorSeverity.DEPENDENCY: RetryPolicy(
        max_retries=1,
        base_delay=5.0,
        max_delay=10.0,
    ),
    # LOGICAL 等級交給 Repair Loop，不需要進行單純等待 API 重新連線
    # FATAL 等級絕對不重試
}

@dataclass
class RetryResult:
    """重試結果記錄"""
    success: bool
    result: Any = None
    error: Optional[AgentError] = None
    total_attempts: int = 0
    total_time: float = 0.0
    attempt_history: List[Dict[str, Any]] = field(default_factory=list)

class RetryEngine:
    """
    重試引擎：根據錯誤分類自動決定重試策略，支援非同步與同步（未來規劃）函式的執行
    """
    def __init__(self):
        self._global_stats = {
            "total_retries": 0,
            "failed_recoveries": 0,
        }
  
    def calculate_delay(self, attempt: int, policy: RetryPolicy) -> float:
        """計算退避延遲時間"""
        delay = policy.base_delay * (policy.exponential_base ** attempt)
        if policy.jitter:
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        return min(delay, policy.max_delay)

    async def execute_with_retry(
        self,
        func: Callable,
        step_id: str = "unknown",
        tool_name: Optional[str] = None,
        policy_override: Optional[RetryPolicy] = None,
        on_fallback: Optional[Callable] = None,
        *args, **kwargs
    ) -> RetryResult:
        start_time = time.time()
        attempt_history = []
        last_error = None
      
        for attempt in range(6):  # 硬上限 6 次
            try:
                # 若 func 是 awaitable 再 await
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
              
                return RetryResult(
                    success=True,
                    result=result,
                    total_attempts=attempt + 1,
                    total_time=time.time() - start_time,
                    attempt_history=attempt_history,
                )
          
            except Exception as e:
                # 分類錯誤
                agent_error = ErrorClassifier.classify(e, step_id, tool_name)
                agent_error.retry_count = attempt
                last_error = agent_error
              
                attempt_history.append({
                    "attempt": attempt + 1,
                    "error_category": agent_error.category.value,
                    "error_message": str(e)[:200],
                    "timestamp": time.time(),
                })
              
                # 判斷是否可重試
                policy = policy_override or DEFAULT_POLICIES.get(
                    agent_error.severity,
                    RetryPolicy(max_retries=0)
                )
              
                if (agent_error.severity not in policy.retryable_severities or attempt >= policy.max_retries):
                    # 重試耗盡，嘗試降級 (Phase 3 Fallback)
                    if on_fallback:
                        try:
                            if asyncio.iscoroutinefunction(on_fallback):
                                fallback_result = await on_fallback(agent_error)
                            else:
                                fallback_result = on_fallback(agent_error)
                            
                            if fallback_result is not None:
                                return RetryResult(True, fallback_result, total_attempts=attempt + 1, total_time=time.time() - start_time, attempt_history=attempt_history)
                        except Exception:
                            pass
                  
                    return RetryResult(False, error=agent_error, total_attempts=attempt + 1, total_time=time.time() - start_time, attempt_history=attempt_history)
              
                # 計算延遲並等待
                delay = self.calculate_delay(attempt, policy)
                
                logger.warning(
                    f"[{step_id}] 重試 {attempt + 1}/{policy.max_retries} | "
                    f"{agent_error.category.value} | 等待 {delay:.1f}s"
                )
              
                self._global_stats["total_retries"] += 1
                await asyncio.sleep(delay)
      
        # 所有重試硬上限失敗
        self._global_stats["failed_recoveries"] += 1
        return RetryResult(False, error=last_error, total_attempts=6, total_time=time.time() - start_time, attempt_history=attempt_history)

def with_retry(max_retries: int = 3, base_delay: float = 1.0, step_id: str = "unknown", tool_name: Optional[str] = None):
    """
    重試裝飾器 (Decorator)
    能夠自動包裝非同步的網路或 API 呼叫，為其附加高韌性的退避機制。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            engine = RetryEngine()
            policy = RetryPolicy(max_retries=max_retries, base_delay=base_delay)
            result = await engine.execute_with_retry(
                func=func, step_id=step_id, tool_name=tool_name, policy_override=policy, *args, **kwargs
            )
            if result.success:
                return result.result
            
            # 發生最終失敗，將 AgentError 退回
            raise result.error.raw_exception or Exception(result.error.to_user_message())
        return wrapper
    return decorator
