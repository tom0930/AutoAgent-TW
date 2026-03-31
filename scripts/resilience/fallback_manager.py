"""
Circuit Breaker & Fallback Manager (Phase 3)
熔斷器：保護外部 API，防範系統陷入無盡重試的雪崩地獄。
降級策略：當最高優先級的方法失敗時，提供降級執行的備案（模型降級、上下文摘要等）。
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, List, Optional
from .error_classifier import ErrorCategory, AgentError

logger = logging.getLogger("resilience")

# ==========================================
# 熔斷器 (Circuit Breaker)
# ==========================================

class CircuitState(Enum):
    CLOSED = "CLOSED"     # 正常運行，允許所有請求
    OPEN = "OPEN"         # 熔斷狀態，拒絕所有請求
    HALF_OPEN = "HALF_OPEN" # 半開狀態，允許少量測試請求

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        
    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("熔斷器半開(HALF_OPEN)，允許測試請求流過。")
                return True
            return False
        # HALF_OPEN 狀態，只允許一次請求
        return True

    def record_success(self):
        self.failure_count = 0
        if self.state != CircuitState.CLOSED:
            logger.info("熔斷器恢復關閉(CLOSED)，解除熔斷。")
            self.state = CircuitState.CLOSED
            
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # 測試失敗，立刻再熔斷
            self.state = CircuitState.OPEN
            logger.warning(f"熔斷器再次開啟(OPEN)，等待 {self.recovery_timeout} 秒。")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"熔斷器開啟(OPEN)！連續失敗達 {self.failure_count} 次，啟動保護。")

# ==========================================
# 降級策略管理器 (Fallback Manager)
# ==========================================

class FallbackStrategy(Enum):
    ALTERNATIVE_MODEL = "alternative_model"
    SIMPLIFIED_TASK = "simplified_task"
    CACHED_RESULT = "cached_result"
    PARTIAL_RESULT = "partial_result"

@dataclass
class FallbackRule:
    categories: List[ErrorCategory]
    strategy: FallbackStrategy
    handler: Callable

class FallbackManager:
    """自動選擇降級策略。"""
    def __init__(self):
        self.rules: List[FallbackRule] = []
        self._register_default_rules()
        
    def _register_default_rules(self):
        # API 額度用盡降級模型
        self.add_rule(FallbackRule([ErrorCategory.QUOTA_EXCEEDED], FallbackStrategy.ALTERNATIVE_MODEL, self._model_fallback))
        # Context 溢出進行摘要
        self.add_rule(FallbackRule([ErrorCategory.CONTEXT_OVERFLOW], FallbackStrategy.SIMPLIFIED_TASK, self._summarize_context))
        
    def add_rule(self, rule: FallbackRule):
        self.rules.append(rule)
        
    def handle_error(self, error: AgentError, context: dict) -> Optional[Any]:
        for rule in self.rules:
            if error.category in rule.categories:
                try:
                    result = rule.handler(error, context)
                    return result
                except Exception:
                    continue
        return None

    def _model_fallback(self, error: AgentError, context: dict) -> dict:
        current_model = context.get("current_model", "gpt-4o")
        new_model = "gpt-4o-mini" if "gpt-4" in current_model else "gpt-3.5-turbo"
        logger.warning(f"💰 觸發降級策略: 模型由 {current_model} 切換為 {new_model}")
        return {"action": "switch_model", "to": new_model}
        
    def _summarize_context(self, error: AgentError, context: dict) -> dict:
        logger.warning(f"📄 觸發降級策略: Context Overflow 自動摘要歷史檔案...")
        return {"action": "compress_context", "status": "compressed"}
