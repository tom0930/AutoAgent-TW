# process_infomation.md

```markdown
# AutoAgent-TW 錯誤處理與自動恢復 / 執行過程透明化

> 版本：v1.0.0
> 最後更新：2025-06-15
> 適用於：AutoAgent-TW v2.x+

---

## 目錄

1. [架構總覽](#1-架構總覽)
2. [錯誤分類系統](#2-錯誤分類系統)
3. [自動重試機制](#3-自動重試機制)
4. [降級策略（Fallback）](#4-降級策略fallback)
5. [熔斷器模式（Circuit Breaker）](#5-熔斷器模式circuit-breaker)
6. [恢復工作流（Recovery Workflow）](#6-恢復工作流recovery-workflow)
7. [執行過程透明化](#7-執行過程透明化)
8. [即時狀態面板](#8-即時狀態面板)
9. [執行日誌系統](#9-執行日誌系統)
10. [使用者介入機制](#10-使用者介入機制)
11. [成本與 Token 監控](#11-成本與-token-監控)
12. [完整範例：端到端流程](#12-完整範例端到端流程)
13. [設定檔參考](#13-設定檔參考)
14. [疑難排解](#14-疑難排解)

---

## 1. 架構總覽

```

┌─────────────────────────────────────────────────────────────┐
│                      AutoAgent-TW Core                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │  Task    │───▶│  Execution   │───▶│  Result           │  │
│  │  Input   │    │  Engine      │    │  Aggregator       │  │
│  └──────────┘    └──────┬───────┘    └───────────────────┘  │
│                         │                                     │
│              ┌──────────▼──────────┐                         │
│              │  Error Handler      │                         │
│              │  ┌────────────────┐ │                         │
│              │  │ Classifier     │ │                         │
│              │  │ Retry Engine   │ │                         │
│              │  │ Fallback Mgr   │ │                         │
│              │  │ Circuit Breaker│ │                         │
│              │  │ Recovery Flow  │ │                         │
│              │  └────────────────┘ │                         │
│              └──────────┬──────────┘                         │
│                         │                                     │
│              ┌──────────▼──────────┐                         │
│              │  Transparency Layer │                         │
│              │  ┌────────────────┐ │                         │
│              │  │ Status Panel   │ │                         │
│              │  │ Logger         │ │                         │
│              │  │ Step Tracker   │ │                         │
│              │  │ Cost Monitor   │ │                         │
│              │  │ Intervention   │ │                         │
│              │  └────────────────┘ │                         │
│              └─────────────────────┘                         │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  External: Telegram Bot │ LINE Bot │ Web Dashboard │ CLI     │
└─────────────────────────────────────────────────────────────┘

```

---

## 2. 錯誤分類系統

### 2.1 錯誤類型定義

所有錯誤必須歸類到以下五個等級之一，每個等級對應不同的處理策略：

```python
# error_classifier.py

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import time


class ErrorSeverity(Enum):
    """
    錯誤嚴重程度分類
  
    Level 1 - TRANSIENT:   暫時性錯誤，重試即可解決
    Level 2 - RECOVERABLE: 可恢復錯誤，需要降級或切換策略
    Level 3 - DEPENDENCY:  依賴服務錯誤，需要等待或替代方案
    Level 4 - LOGICAL:     邏輯錯誤，需要修正任務描述或參數
    Level 5 - FATAL:       致命錯誤，必須人工介入
    """
    TRANSIENT = 1
    RECOVERABLE = 2
    DEPENDENCY = 3
    LOGICAL = 4
    FATAL = 5


class ErrorCategory(Enum):
    """錯誤具體分類"""
    # Level 1 - 暫時性
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK_BLIP = "network_blip"
    TEMPORARY_SERVER_ERROR = "temp_server_error"
  
    # Level 2 - 可恢復
    INVALID_RESPONSE = "invalid_response"
    PARSE_ERROR = "parse_error"
    TOOL_OUTPUT_MALFORMED = "tool_output_malformed"
    CONTEXT_OVERFLOW = "context_overflow"
  
    # Level 3 - 依賴服務
    API_DOWN = "api_down"
    TOOL_UNAVAILABLE = "tool_unavailable"
    AUTH_EXPIRED = "auth_expired"
    QUOTA_EXCEEDED = "quota_exceeded"
  
    # Level 4 - 邏輯錯誤
    TASK_AMBIGUOUS = "task_ambiguous"
    INVALID_PARAMS = "invalid_params"
    UNSUPPORTED_OPERATION = "unsupported_operation"
    CONFLICTING_INSTRUCTIONS = "conflicting_instructions"
  
    # Level 5 - 致命
    SYSTEM_CRASH = "system_crash"
    DATA_CORRUPTION = "data_corruption"
    SECURITY_VIOLATION = "security_violation"
    UNKNOWN_FATAL = "unknown_fatal"


# 錯誤碼 → 分類的映射表
ERROR_CODE_MAP = {
    # HTTP 錯誤碼
    400: ErrorCategory.INVALID_PARAMS,
    401: ErrorCategory.AUTH_EXPIRED,
    403: ErrorCategory.SECURITY_VIOLATION,
    404: ErrorCategory.TOOL_UNAVAILABLE,
    408: ErrorCategory.TIMEOUT,
    429: ErrorCategory.RATE_LIMIT,
    500: ErrorCategory.TEMPORARY_SERVER_ERROR,
    502: ErrorCategory.API_DOWN,
    503: ErrorCategory.API_DOWN,
    504: ErrorCategory.TIMEOUT,
  
    # 自定義錯誤碼
    "CTX_OVERFLOW": ErrorCategory.CONTEXT_OVERFLOW,
    "PARSE_FAIL": ErrorCategory.PARSE_ERROR,
    "TOOL_MALFORMED": ErrorCategory.TOOL_OUTPUT_MALFORMED,
    "TASK_AMBIGUOUS": ErrorCategory.TASK_AMBIGUOUS,
}


@dataclass
class AgentError:
    """統一錯誤物件"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    step_id: str                          # 發生錯誤的步驟 ID
    tool_name: Optional[str] = None       # 涉及的工具名稱
    raw_exception: Optional[Exception] = None
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)
    context: dict = field(default_factory=dict)  # 額外上下文資訊
  
    def to_user_message(self) -> str:
        """轉換為使用者可讀的錯誤訊息"""
        messages = {
            ErrorCategory.RATE_LIMIT: 
                "⏳ API 呼叫過於頻繁，正在自動等待後重試...",
            ErrorCategory.TIMEOUT: 
                "⏱️ 回應超時，正在重新嘗試...",
            ErrorCategory.NETWORK_BLIP: 
                "🌐 網路連線不穩，正在重新連線...",
            ErrorCategory.API_DOWN: 
                "🔧 目標服務暫時不可用，正在嘗試替代方案...",
            ErrorCategory.AUTH_EXPIRED: 
                "🔑 API 金鑰可能已過期，請檢查您的設定。",
            ErrorCategory.QUOTA_EXCEEDED: 
                "💰 API 額度已用盡。建議：\n"
                "  1. 檢查 OpenAI 帳戶餘額\n"
                "  2. 切換到較便宜的模型\n"
                "  3. 等待額度重置",
            ErrorCategory.CONTEXT_OVERFLOW: 
                "📄 上下文過長，正在自動摘要以繼續...",
            ErrorCategory.TASK_AMBIGUOUS: 
                "🤔 任務描述不夠明確，需要您的補充說明。",
            ErrorCategory.INVALID_PARAMS: 
                "⚠️ 參數有誤，正在嘗試自動修正...",
            ErrorCategory.SECURITY_VIOLATION: 
                "🛡️ 觸發安全規則，已停止執行。請檢查任務內容。",
        }
        return messages.get(
            self.category, 
            f"❌ 發生錯誤：{self.message}"
        )


class ErrorClassifier:
    """
    錯誤分類器
  
    接收原始異常，自動分類並產生 AgentError 物件
    """
  
    @staticmethod
    def classify(exception: Exception, step_id: str, 
                 tool_name: str = None) -> AgentError:
        """將原始異常分類為結構化的 AgentError"""
      
        # --- API 速率限制 ---
        if "rate_limit" in str(exception).lower() or \
           "429" in str(exception):
            return AgentError(
                category=ErrorCategory.RATE_LIMIT,
                severity=ErrorSeverity.TRANSIENT,
                message=str(exception),
                step_id=step_id,
                tool_name=tool_name,
                raw_exception=exception,
            )
      
        # --- 超時 ---
        if isinstance(exception, TimeoutError) or \
           "timeout" in str(exception).lower():
            return AgentError(
                category=ErrorCategory.TIMEOUT,
                severity=ErrorSeverity.TRANSIENT,
                message=str(exception),
                step_id=step_id,
                tool_name=tool_name,
                raw_exception=exception,
            )
      
        # --- 上下文溢出 ---
        if "context_length" in str(exception).lower() or \
           "maximum context" in str(exception).lower():
            return AgentError(
                category=ErrorCategory.CONTEXT_OVERFLOW,
                severity=ErrorSeverity.RECOVERABLE,
                message=str(exception),
                step_id=step_id,
                tool_name=tool_name,
                raw_exception=exception,
            )
      
        # --- 認證失敗 ---
        if "401" in str(exception) or \
           "authentication" in str(exception).lower() or \
           "api_key" in str(exception).lower():
            return AgentError(
                category=ErrorCategory.AUTH_EXPIRED,
                severity=ErrorSeverity.DEPENDENCY,
                message=str(exception),
                step_id=step_id,
                tool_name=tool_name,
                raw_exception=exception,
            )
      
        # --- 額度用盡 ---
        if "quota" in str(exception).lower() or \
           "billing" in str(exception).lower():
            return AgentError(
                category=ErrorCategory.QUOTA_EXCEEDED,
                severity=ErrorSeverity.DEPENDENCY,
                message=str(exception),
                step_id=step_id,
                tool_name=tool_name,
                raw_exception=exception,
            )
      
        # --- 網路錯誤 ---
        if isinstance(exception, ConnectionError) or \
           "connection" in str(exception).lower():
            return AgentError(
                category=ErrorCategory.NETWORK_BLIP,
                severity=ErrorSeverity.TRANSIENT,
                message=str(exception),
                step_id=step_id,
                tool_name=tool_name,
                raw_exception=exception,
            )
      
        # --- 未知錯誤（保守分類為 FATAL） ---
        return AgentError(
            category=ErrorCategory.UNKNOWN_FATAL,
            severity=ErrorSeverity.FATAL,
            message=str(exception),
            step_id=step_id,
            tool_name=tool_name,
            raw_exception=exception,
        )
```

### 2.2 錯誤分類速查表

```
┌──────────────────────┬────────────┬─────────────────────────┐
│ 錯誤訊息關鍵字         │ 等級       │ 預設處理策略             │
├──────────────────────┼────────────┼─────────────────────────┤
│ rate_limit / 429     │ TRANSIENT  │ 指數退避重試             │
│ timeout              │ TRANSIENT  │ 重試（最多 3 次）        │
│ connection error     │ TRANSIENT  │ 重試 + 換備用端點        │
│ context_length       │ RECOVERABLE│ 自動摘要上下文           │
│ parse error          │ RECOVERABLE│ 重新生成 + 修正 prompt   │
│ 401 / auth           │ DEPENDENCY  │ 通知使用者更新金鑰       │
│ quota / billing      │ DEPENDENCY  │ 切換模型 + 通知         │
│ 502 / 503            │ DEPENDENCY  │ 熔斷 + 降級             │
│ ambiguous            │ LOGICAL     │ 詢問使用者補充           │
│ security             │ FATAL       │ 立即停止 + 通知         │
│ unknown              │ FATAL       │ 記錄 + 通知 + 停止      │
└──────────────────────┴────────────┴─────────────────────────┘
```

---

## 3. 自動重試機制

### 3.1 指數退避重試器

```python
# retry_engine.py

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Any
from functools import wraps
from error_classifier import (
    AgentError, ErrorSeverity, ErrorClassifier
)


@dataclass
class RetryPolicy:
    """重試策略配置"""
    max_retries: int = 3                    # 最大重試次數
    base_delay: float = 1.0                 # 基礎延遲（秒）
    max_delay: float = 60.0                 # 最大延遲上限
    exponential_base: float = 2.0           # 指數底數
    jitter: bool = True                     # 是否加入隨機抖動
    retryable_severities: list = field(
        default_factory=lambda: [
            ErrorSeverity.TRANSIENT,
            ErrorSeverity.RECOVERABLE,
        ]
    )
    # 特定錯誤類型的自定義策略
    category_overrides: dict = field(default_factory=dict)


# 各錯誤類型的預設重試策略
DEFAULT_POLICIES = {
    ErrorSeverity.TRANSIENT: RetryPolicy(
        max_retries=5,
        base_delay=1.0,
        max_delay=30.0,
    ),
    ErrorSeverity.RECOVERABLE: RetryPolicy(
        max_retries=3,
        base_delay=2.0,
        max_delay=15.0,
    ),
    ErrorSeverity.DEPENDENCY: RetryPolicy(
        max_retries=2,
        base_delay=5.0,
        max_delay=60.0,
    ),
    # LOGICAL 和 FATAL 不重試
}


@dataclass
class RetryResult:
    """重試結果記錄"""
    success: bool
    result: Any = None
    error: Optional[AgentError] = None
    total_attempts: int = 0
    total_time: float = 0.0
    attempt_history: list = field(default_factory=list)


class RetryEngine:
    """
    重試引擎
  
    根據錯誤分類自動決定重試策略，支援指數退避與隨機抖動
    """
  
    def __init__(self, logger=None):
        self.logger = logger
        self._global_stats = {
            "total_retries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
        }
  
    def calculate_delay(self, attempt: int, 
                        policy: RetryPolicy) -> float:
        """計算退避延遲時間"""
        # 指數退避：base_delay * (exponential_base ^ attempt)
        delay = policy.base_delay * (
            policy.exponential_base ** attempt
        )
      
        # 加入隨機抖動（±25%），避免 thundering herd
        if policy.jitter:
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
      
        return min(delay, policy.max_delay)
  
    async def execute_with_retry(
        self,
        func: Callable,
        step_id: str,
        tool_name: str = None,
        policy_override: RetryPolicy = None,
        on_retry: Callable = None,      # 每次重試前的回呼
        on_fallback: Callable = None,   # 重試耗盡後的降級回呼
        *args, **kwargs
    ) -> RetryResult:
        """
        帶自動重試的執行器
      
        Parameters
        ----------
        func : Callable
            要執行的非同步函式
        step_id : str
            當前步驟 ID（用於日誌追蹤）
        tool_name : str
            工具名稱
        policy_override : RetryPolicy
            覆蓋預設重試策略
        on_retry : Callable
            每次重試前呼叫，簽名：async (attempt, error, delay)
        on_fallback : Callable
            重試耗盡後呼叫，簽名：async (error) -> fallback_result
        """
        start_time = time.time()
        attempt_history = []
        last_error = None
      
        for attempt in range(6):  # 最多嘗試 6 次（含首次）
            try:
                result = await func(*args, **kwargs)
              
                return RetryResult(
                    success=True,
                    result=result,
                    total_attempts=attempt + 1,
                    total_time=time.time() - start_time,
                    attempt_history=attempt_history,
                )
          
            except Exception as e:
                # 分類錯誤
                agent_error = ErrorClassifier.classify(
                    e, step_id, tool_name
                )
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
                    RetryPolicy(max_retries=0)  # 預設不重試
                )
              
                if (agent_error.severity not in 
                        policy.retryable_severities or
                    attempt >= policy.max_retries):
                  
                    # 重試耗盡，嘗試降級
                    if on_fallback:
                        try:
                            fallback_result = await on_fallback(
                                agent_error
                            )
                            if fallback_result is not None:
                                return RetryResult(
                                    success=True,
                                    result=fallback_result,
                                    total_attempts=attempt + 1,
                                    total_time=time.time() - start_time,
                                    attempt_history=attempt_history,
                                )
                        except Exception:
                            pass
                  
                    return RetryResult(
                        success=False,
                        error=agent_error,
                        total_attempts=attempt + 1,
                        total_time=time.time() - start_time,
                        attempt_history=attempt_history,
                    )
              
                # 計算延遲並等待
                delay = self.calculate_delay(attempt, policy)
              
                if self.logger:
                    self.logger.warning(
                        f"[{step_id}] 重試 {attempt + 1}/"
                        f"{policy.max_retries} | "
                        f"{agent_error.category.value} | "
                        f"等待 {delay:.1f}s"
                    )
              
                # 呼叫重試回呼
                if on_retry:
                    await on_retry(attempt, agent_error, delay)
              
                self._global_stats["total_retries"] += 1
                await asyncio.sleep(delay)
      
        # 所有重試都失敗
        self._global_stats["failed_recoveries"] += 1
        return RetryResult(
            success=False,
            error=last_error,
            total_attempts=6,
            total_time=time.time() - start_time,
            attempt_history=attempt_history,
        )
  
    def get_stats(self) -> dict:
        """取得全域重試統計"""
        return self._global_stats.copy()


# ============================================
# 裝飾器版本（方便直接套用到函式上）
# ============================================

def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    step_id: str = None,
):
    """
    重試裝飾器
  
    Usage:
        @with_retry(max_retries=3, step_id="search_step")
        async def search_web(query: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, ** = "unknown",
    tool_name: strkwargs):
            engine = RetryEngine()
            policy = RetryPolicy(
                max_retries=max_retries,
                base_delay=base_delay,
            )
            result = await engine.execute_with_retry(
                func=func,
                step_id=step_id,
                tool_name=tool_name,
                policy_override=policy,
                *args, **kwargs,
            )
            if result.success:
                return result.result
            raise result.error.raw_exception or Exception(
                result.error.message
            )
        return wrapper
    return decorator
```

### 3.2 重試流程圖

```
開始執行步驟
    │
    ▼
┌───────────────┐     成功      ┌──────────┐
│  執行函式      │─────────────▶│ 返回結果  │
└───────┬───────┘              └──────────┘
        │ 失敗
        ▼
┌───────────────┐
│  錯誤分類器    │
└───────┬───────┘
        │
        ▼
┌───────────────────────┐
│  等級 1/2？            │──── 否 ───▶ 進入降級/熔斷流程
│  重試次數 < 上限？      │
└───────┬───────────────┘
        │ 是
        ▼
┌───────────────────────┐
│  計算退避時間           │
│  delay = base × 2^n   │
│  ± 25% 隨機抖動        │
└───────┬───────────────┘
        │
        ▼
┌───────────────────────┐
│  通知透明化層           │
│  "正在重試第 N 次..."   │
└───────┬───────────────┘
        │
        ▼
    等待 delay 秒
        │
        ▼
    回到「執行函式」
```

---

## 4. 降級策略（Fallback）

```python
# fallback_manager.py

from typing import Callable, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from error_classifier import AgentError, ErrorCategory


class FallbackStrategy(Enum):
    """降級策略類型"""
    ALTERNATIVE_MODEL = "alternative_model"   # 切換備用模型
    ALTERNATIVE_TOOL = "alternative_tool"     # 切換備用工具
    CACHED_RESULT = "cached_result"           # 使用快取結果
    SIMPLIFIED_TASK = "simplified_task"       # 簡化任務後重試
    PARTIAL_RESULT = "partial_result"         # 返回部分結果
    HUMAN_INTERVENTION = "human_intervention" # 請求人工介入


@dataclass
class FallbackRule:
    """降級規則定義"""
    error_categories: list[ErrorCategory]
    strategy: FallbackStrategy
    handler: Callable
    priority: int = 0            # 優先級（數字越小越優先）
    description: str = ""
    enabled: bool = True


class FallbackManager:
    """
    降級管理器
  
    根據錯誤類型自動選擇最合適的降級策略
    """
  
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.rules: list[FallbackRule] = []
        self.cache: dict[str, Any] = {}    # 簡易快取
        self._register_default_rules()
  
    def _register_default_rules(self):
        """註冊預設降級規則"""
      
        # 規則 1：API 額度用盡 → 切換到較便宜的模型
        self.add_rule(FallbackRule(
            error_categories=[ErrorCategory.QUOTA_EXCEEDED],
            strategy=FallbackStrategy.ALTERNATIVE_MODEL,
            handler=self._switch_to_cheap_model,
            priority=1,
            description="切換到 GPT-4o-mini 繼續執行",
        ))
      
        # 規則 2：服務不可用 → 切換備用工具
        self.add_rule(FallbackRule(
            error_categories=[
                ErrorCategory.API_DOWN,
                ErrorCategory.TOOL_UNAVAILABLE,
            ],
            strategy=FallbackStrategy.ALTERNATIVE_TOOL,
            handler=self._switch_to_alternative_tool,
            priority=2,
            description="切換到備用 API 端點或替代工具",
        ))
      
        # 規則 3：上下文溢出 → 自動摘要
        self.add_rule(FallbackRule(
            error_categories=[ErrorCategory.CONTEXT_OVERFLOW],
            strategy=FallbackStrategy.SIMPLIFIED_TASK,
            handler=self._summarize_context,
            priority=1,
            description="自動摘要上下文以縮減 token 用量",
        ))
      
        # 規則 4：解析失敗 → 簡化 prompt 後重試
        self.add_rule(FallbackRule(
            error_categories=[
                ErrorCategory.INVALID_RESPONSE,
                ErrorCategory.PARSE_ERROR,
                ErrorCategory.TOOL_OUTPUT_MALFORMED,
            ],
            strategy=FallbackStrategy.SIMPLIFIED_TASK,
            handler=self._simplify_prompt,
            priority=2,
            description="簡化指令後重新嘗試",
        ))
      
        # 規則 5：任務模糊 → 請求使用者補充
        self.add_rule(FallbackRule(
            error_categories=[
                ErrorCategory.TASK_AMBIGUOUS,
                ErrorCategory.CONFLICTING_INSTRUCTIONS,
            ],
            strategy=FallbackStrategy.HUMAN_INTERVENTION,
            handler=self._ask_user_clarification,
                   ))
  
    def add_rule(self, rule: FallbackRule):
        """新增降級規則"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
  
    async def handle_error(
        self, error: AgentError, context: dict = None
    ) -> Optional[Any]:
        """
        處理錯誤，自動選擇並執行降級策略
      
        Returns
        -------
        降級結果，若無可用策略則返回 None
        """
        context = context or {}
      
        for rule in self.rules:
            if not rule.enabled:
                continue
            if error.category in rule.error_categories:
                try:
                    result = await rule.handler(error, context)
                    if result is not None:
                        return result
                except Exception as e:
                    # 降級策略本身失敗，嘗試下一條規則
                    continue
      
        return None
  
    # ========================================
    #  內建降級處理器
    # ========================================
  
    async def _switch_to_cheap_model(
        self, error: AgentError, context: dict
    ) -> dict:
        """切換到較便宜的模型"""
        model_chain = self.config.get("model_chain", [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ])
      
        current_model = context.get("current_model", model_chain[0])
      
        try:
            current_idx = model_chain.index(current_model)
            if current_idx + 1 < len(model_chain):
                new_model = model_chain[current_idx + 1]
                return {
                    "action": "switch_model",
                    "from": current_model,
                    "to": new_model,
                    "message": (
                        f"🔄 模型降級：{current_model} → {new_model}\n"
                        f"原因：{error.category.value}"
                    ),
                }
        except_RESULT,
            handler=self._return_partial_result,
            priority priority=1,
            description="向使用者請求補充說明",
        ))
      
        # 規則 6：任何錯誤 → 嘗試返回部分結果
        self.add_rule(FallbackRule(
            error_categories=list(ErrorCategory),
            strategy=FallbackStrategy.PARTIAL=99,   # 最低優先級，兜底策略
            description="返回已成功完成的部分結果",
 ValueError:
            pass
        return None
  
    async def _switch_to_alternative_tool(
        self, error: AgentError, context: dict
    ) -> dict:
        """切換到備用工具"""
        tool_alternatives = self.config.get("tool_alternatives", {
            "google_search": ["bing_search", "duckduckgo_search"],
            "github_api": ["github_api_mirror"],
            "web_scraper": ["requests_fallback", "curl_fallback"],
        })
      
        failed_tool = error.tool_name
        if failed_tool in tool_alternatives:
            alternatives = tool_alternatives[failed_tool]
            return {
                "action": "switch_tool",
                "from": failed_tool,
                "to": alternatives[0],
                "remaining_alternatives": alternatives[1:],
                "message": (
                    f"🔧 工具降級：{failed_tool} → {alternatives[0]}\n"
                    f"原因：{error.category.value}"
                ),
            }
        return None
  
    async def _summarize_context(
        self, error: AgentError, context: dict
    ) -> dict:
        """自動摘要上下文"""
        return {
            "action": "summarize_context",
            "keep_last_n_messages": 5,
            "summary_instruction": (
                "請將以下對話摘要為 500 字以內的重點，"
                "保留所有關鍵決策和未完成任務。"
            ),
            "message": (
                "📄 上下文過長，正在自動摘要以繼續執行..."
            ),
        }
  
    async def _simplify_prompt(
        self, error: AgentError, context: dict
    ) -> dict:
        """簡化 prompt 後重試"""
        return {
            "action": "simplify_prompt",
            "instructions": (
                "將原始指令簡化為最核心的請求，"
                "移除所有可選條件和格式要求。"
            ),
            "message": (
                "✂️ 指令簡化中，移除非必要條件後重新嘗試..."
            ),
        }
  
    async def _ask_user_clarification(
        self, error: AgentError, context: dict
    ) -> dict:
        """請求使用者補充說明"""
        return {
            "action": "human_intervention",
            "prompt_to_user": (
                f"我遇到了以下問題：{error.message}\n\n"
                f"能否提供更多資訊來幫助我繼續？\n"
                f"例如：具體的目標、偏好的格式、或相關的背景資訊。"
            ),
            "message": "🤔 需要您的補充說明才能繼續。",
        }
  
    async def _return_partial_result(
        self, error: AgentError, context: dict
    ) -> dict:
        """返回部分結果"""
        completed_steps = context.get("completed_steps", [])
        return {
            "action": "partial_result",
            "completed_steps": completed_steps,
            "failed_at": error.step_id,
            "message": (
                f"⚠️ 任務在步驟 [{error.step_id}] 遇到問題。\n"
                f"以下是已完成的部分結果：\n"
                f"✅ 完成 {len(completed_steps)} 個步驟\n"
                f"❌ 失敗原因：{error.category.value}"
            ),
        }
```

### 4.1 降級策略速查

```
錯誤類型                 → 降級策略                    → 備註
─────────────────────────────────────────────────────────────
QUOTA_EXCEEDED          → 切換便宜模型               → gpt-4o → gpt-4o-mini
API_DOWN                → 切換備用端點               → 自動輪替
CONTEXT_OVERFLOW        → 自動摘要舊對話             → 保留最近 5 則
PARSE_ERROR             → 簡化 prompt 重試           → 移除非必要條件
TASK_AMBIGUOUS          → 詢問使用者                 → 帶具體問題
AUTH_EXPIRED            → 通知使用者更新金鑰         → 不自動重試
SECURITY_VIOLATION      → 立即停止                   → 記錄並通知
（任何錯誤的兜底）        → 返回部分結果               → 已完成的步驟照常交付
```

---

## 5. 熔斷器模式（Circuit Breaker）

```python
# circuit_breaker.py

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Optional


class CircuitState(Enum):
    """熔斷器三種狀態"""
    CLOSED = "closed"         # 正常：請求正常通過
    OPEN = "open"             # 熔斷：請求直接被拒絕
    HALF_OPEN = "half_open"   # 試探：允許少量請求測試恢復


@dataclass
class CircuitBreakerConfig:
    """熔斷器配置"""
    failure_threshold: int = 5       # 失敗次數閾值
    recovery_timeout: float = 30.0   # 熔斷恢復超時（秒）
    half_open_max_calls: int = 3     # 半開狀態最大試探次數
    success_threshold: int = 2       # 半開→關閉所需成功次數
    monitoring_window: float = 60.0  # 監控窗口（秒）


class CircuitBreaker:
    """
    熔斷器
  
    當某個服務或工具連續失敗時，自動「熔斷」——
    短時間內不再嘗試呼叫，避免無謂的資源浪費。
  
    狀態轉換：
    CLOSED ──(連續失敗達閾值)──▶ OPEN
    OPEN ──(超時後)──▶ HALF_OPEN
    HALF_OPEN ──(試探成功達閾值)──▶ CLOSED
    HALF_OPEN ──(試探失敗)──▶ OPEN
    """
  
    def __init__(
        self, 
        name: str,
        config: CircuitBreakerConfig = None,
        on_state_change: Callable = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.on_state_change = on_state_change
      
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._half_open_calls = 0
      
        # 統計資料
        self._stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "rejected_calls": 0,      # 被熔斷拒絕的呼叫
            "state_changes": [],
        }
  
    @property
    def state(self) -> CircuitState:
        """取得當前狀態（自動檢查是否該從 OPEN → HALF_OPEN）"""
        if (self._state == CircuitState.OPEN and
            time.time() - self._last_failure_time > 
            self.config.recovery_timeout):
            self._transition_to(CircuitState.HALF_OPEN)
        return self._state
  
    def _transition_to(self, new_state: CircuitState):
        """狀態轉換"""
        old_state = self._state
        self._state = new_state
      
        self._stats["state_changes"].append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": time.time(),
        })
      
        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0
      
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
      
        if self.on_state_change:
            self.on_state_change(self.name, old_state, new_state)
  
    async def call(self, func: Callable, *args, **kwargs):
        """
        透過熔斷器呼叫函式
      
        如果熔斷器開啟，直接拒絕呼叫並拋出異常
        """
        current_state = self.state
        self._stats["total_calls"] += 1
      
        # OPEN 狀態：直接拒絕
        if current_state == CircuitState.OPEN:
            self._stats["rejected_calls"] += 1
            raise CircuitBreakerOpenError(
                f"熔斷器 [{self.name}] 已開啟，"
                f"預計 {self.config.recovery_timeout}s 後嘗試恢復。"
            )
      
        # HALF_OPEN 狀態：限制試探次數
        if current_state == CircuitState.HALF_OPEN:
            if (self._half_open_calls >= 
                    self.config.half_open_max_calls):
                self._stats["rejected_calls"] += 1
                raise CircuitBreakerOpenError(
                    f"熔斷器 [{self.name}] 試探次數已達上限。"
                )
            self._half_open_calls += 1
      
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
  
    def _on_success(self):
        """成功回呼"""
        self._stats["successful_calls"] += 1
      
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if (self._success_count >= 
                    self.config.success_threshold):
                self._transition_to(CircuitState.CLOSED)
      
        if self._state == CircuitState.CLOSED:
            self._failure_count = 0  # 重置失敗計數
  
    def _on_failure(self):
        """失敗回呼"""
        self._stats["failed_calls"] += 1
        self._failure_count += 1
        self._last_failure_time = time.time()
      
        if self._state == CircuitState.HALF_OPEN:
            # 試探失敗 → 重新熔斷
            self._transition_to(CircuitState.OPEN)
      
        elif (self._state == CircuitState.CLOSED and
              self._failure_count >= 
              self.config.failure_threshold):
            # 累積失敗達閾值 → 熔斷
            self._transition_to(CircuitState.OPEN)
  
    def get_stats(self) -> dict:
        """取得統計資料"""
        return {
            **self._stats,
            "current_state": self.state.value,
            "failure_count": self._failure_count,
        }
  
    def reset(self):
        """手動重置熔斷器"""
        self._transition_to(CircuitState.CLOSED)


class CircuitBreakerOpenError(Exception):
    """熔斷器開啟時拋出的異常"""
    pass


# ============================================
#  熔斷器管理器（管理多個熔斷器）
# ============================================

class CircuitBreakerRegistry:
    """
    熔斷器註冊表
  
    為每個外部服務或工具維護獨立的熔斷器
    """
  
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
  
    def get_or_create(
        self, 
        name: str,
        config: CircuitBreakerConfig = None,
    ) -> CircuitBreaker:
        """取得或建立熔斷器"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                config=config,
                on_state_change=self._on_state_change,
            )
        return self._breakers[name]
  
    def _on_state_change(
        self, name: str, 
        old_state: CircuitState, 
        new_state: CircuitState
    ):
        """全域狀態變更回呼"""
        # 可以在這裡接通知系統
        print(
            f"⚡ 熔斷器 [{name}]: "
            f"{old_state.value} → {new_state.value}"
        )
  
    def get_all_stats(self) -> dict:
        """取得所有熔斷器的統計資料"""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }
```

### 5.1 熔斷器狀態機

```
         失敗達閾值                    超時
    ┌──────────────────┐      ┌─────────────────┐
    │                  ▼      │                 ▼
┌───┴───┐          ┌───────┐  │           ┌───────────┐
│CLOSED │          │ OPEN  │──┘           │ HALF_OPEN │
│(正常)  │◀─────────│(熔斷)  │◀─────────────│(試探中)    │
└───┬───┘          └───────┘              └─────┬─────┘
    │                                           │
    │         試探成功達閾值                      │ 試探失敗
    └───────────────────────────────────────────┘──────────▶ OPEN
```

---

## 6. 恢復工作流（Recovery Workflow）

```python
# recovery_workflow.py

import asyncio
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
from error_classifier import AgentError, ErrorSeverity
from retry_engine import RetryEngine, RetryResult
from fallback_manager import FallbackManager
from circuit_breaker import (
    CircuitBreakerRegistry, CircuitBreakerOpenError
)


class RecoveryOutcome(Enum):
    """恢復結果"""
    SUCCESS = "success"               # 成功恢復
    PARTIAL = "partial"               # 部分恢復
    DEFERRED = "deferred"             # 延後處理
    ESCALATED = "escalated"           # 已上報人工
    ABORTED = "aborted"               # 已中止


@dataclass
class RecoveryReport:
    """恢復報告"""
    outcome: RecoveryOutcome
    original_error: AgentError
    steps_taken: list[str]            # 採取的恢復步驟
    final_result: any = None
    message_to_user: str = ""
    metadata: dict = field(default_factory=dict)


class RecoveryWorkflow:
    """
    恢復工作流引擎
  
    統一協調：分類器 → 重試 → 熔斷 → 降級 → 通知
    """
  
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.retry_engine = RetryEngine()
        self.fallback_manager = FallbackManager(config)
        self.circuit_breakers = CircuitBreakerRegistry()
        self._recovery_history: list[RecoveryReport] = []
  
    async def handle(
        self,
        error: AgentError,
        original_func: Callable,
        context: dict = None,
    ) -> RecoveryReport:
        """
        統一錯誤恢復入口
      
        處理流程：
        1. 檢查熔斷器狀態
        2. 嘗試自動重試
        3. 重試失敗 → 嘗試降級策略
        4. 降級失敗 → 上報人工介入
        """
        context = context or {}
        steps_taken = []
      
        # ========================================
        # Step 1：熔斷器檢查
        # ========================================
        breaker_name = context.get(
            "breaker_name", error.tool_name or "default"
        )
        breaker = self.circuit_breakers.get_or_create(
            breaker_name
        )
      
        if breaker.state.value == "open":
            steps_taken.append("熔斷器開啟，跳過直接呼叫")
            # 直接進入降級流程
        else:
            # ========================================
            # Step 2：自動重試
            # ========================================
            steps_taken.append(
                f"開始自動重試（錯誤等級："
                f"{error.severity.value}）"
            )
          
            retry_result = await self.retry_engine \
                .execute_with_retry(
                    func=lambda: breaker.call(
                        original_func
                    ),
                    step_id=error.step_id,
                    tool_name=error.tool_name,
                    on_retry=lambda attempt, err, delay: 
                        steps_taken.append(
                            f"重試 #{attempt + 1}："
                            f"等待 {delay:.1f}s"
                        ),
                )
          
            if retry_result.success:
                steps_taken.append(
                    f"重試成功（共 {retry_result.total_attempts}"
                    f" 次嘗試）"
                )
                report = RecoveryReport(
                    outcome=RecoveryOutcome.SUCCESS,
                    original_error=error,
                    steps_taken=steps_taken,
                    final_result=retry_result.result,
                    message_to_user="✅ 問題已自動修復，繼續執行。",
                )
                self._recovery_history.append(report)
                return report
      
        # ========================================
        # Step 3：降級策略
        # ========================================
        steps_taken.append("重試耗盡，進入降級流程")
      
        fallback_result = await self.fallback_manager \
            .handle_error(error, context)
      
        if fallback_result:
            action = fallback_result.get("action")
            steps_taken.append(
                f"降級策略：{action} - "
                f"{fallback_result.get('message', '')}"
            )
          
            outcome = (
                RecoveryOutcome.PARTIAL
                if action == "partial_result"
                else RecoveryOutcome.SUCCESS
            )
          
            report = RecoveryReport(
                outcome=outcome,
                original_error=error,
                steps_taken=steps_taken,
                final_result=fallback_result,
                message_to_user=fallback_result.get(
                    "message", "已採用替代方案繼續。"
                ),
            )
            self._recovery_history.append(report)
            return report
      
        # ========================================
        # Step 4：上報人工介入
        # ========================================
        steps_taken.append("所有自動恢復手段失敗，上報人工")
      
        report = RecoveryReport(
            outcome=RecoveryOutcome.ESCALATED,
            original_error=error,
            steps_taken=steps_taken,
            message_to_user=(
                f"🚨 無法自動恢復，需要您的協助。\n\n"
                f"錯誤類型：{error.category.value}\n"
                f"錯誤訊息：{error.message}\n"
                f"發生步驟：{error.step_id}\n\n"
                f"已嘗試的恢復方式：\n"
                + "\n".join(
                    f"  • {s}" for s in steps_taken
                )
                + "\n\n請選擇：\n"
                f"  [1] 重試整個任務\n"
                f"  [2] 跳過此步驟繼續\n"
                f"  [3] 修改任務描述\n"
                f"  [4] 中止任務"
            ),
        )
        self._recovery_history.append(report)
        return report
  
    def get_recovery_history(self) -> list[RecoveryReport]:
        """取得恢復歷史記錄"""
        return self._recovery_history.copy()
```

---

## 7. 執行過程透明化

### 7.1 步驟追蹤器

```python
# step_tracker.py

import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable, Any


class StepStatus(Enum):
    """步驟狀態"""
    PENDING = "pending"         # 等待執行
    RUNNING = "running"         # 執行中
    tool_name: Optional[str] = None
    parent_id: Optional[str] = None       # 父步驟 ID
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    result_summary: Optional[str] = None  # 結果摘要
    token_usage: int = 0                  # 此步驟的 token 用量
    cost_estimate: float = 0.0            # 預估費用（美元）
    metadata: dict = field(default_factory=dict)
  
    @property
    def icon(self) -> str:
        icons = {
            StepStatus.PENDING: "⏳",
            StepStatus.RUNNING: "🔄",
            StepStatus.COMPLETED: "✅",
            StepStatus.FAILED: "❌",
            StepStatus.SKIPPED: "⏭️",
            StepStatus.RETRYING: "🔁",
            StepStatus.WAITING_HUMAN: "🙋",
        }
        return icons.get(self    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失敗
    SKIPPED = "skipped"         # 已跳過
    RETRYING = "retrying"       # 重試中
    WAITING_HUMAN = "waiting"   # 等待人工介入


@dataclass
class StepInfo:
    """步驟詳細資訊"""
    id: str
    name: str
    description: str
    status: StepStatus = StepStatus.PENDING
.status, "❓")
  
    @property
    def elapsed_display(self) -> str:
        if self.duration:
            if self.duration < 1:
                return f"{self.duration*1000:.0f}ms"
            return f"{self.duration:.1f}s"
        if self.start_time:
            elapsed = time.time() - self.start_time
            return f"{elapsed:.1f}s (進行中)"
        return "-"


class StepTracker:
    """
    步驟追蹤器
  
    追蹤整個任務執行過程中的每一步，
    提供結構化的進度資訊供透明化面板使用
    """
  
    def __init__(self, task_id: str = None, 
                 on_update: Callable = None):
        self.task_id = task_id or str(uuid.uuid4())[:8]
        self.on_update = on_update  # 狀態變更回呼
        self.steps: dict[str, StepInfo] = {}
        self._step_order: list[str] = []
        self._total_tokens = 0
        self._total_cost = 0.0
        self._start_time = time.time()
  
    def add_step(
        self,
        name: str,
        description: str = "",
        tool_name: str = None,
        parent_id: str = None,
    ) -> str:
        """新增一個步驟"""
        step_id = f"{self.task_id}_step_{len(self._step_order) + 1}"
      
        step = StepInfo(
            id=step_id,
            name=name,
            description=description,
            tool_name=tool_name,
            parent_id=parent_id,
        )
      
        self.steps[step_id] = step
        self._step_order.append(step_id)
        self._notify_update(step_id, "added")
        return step_id
  
    def start_step(self, step_id: str):
        """標記步驟開始"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.RUNNING
            step.start_time = time.time()
            self._notify_update(step_id, "started")
  
    def complete_step(
        self, step_id: str, 
        result_summary: str = "",
        token_usage: int = 0,
        cost_estimate: float = 0.0,
    ):
        """標記步驟完成"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.COMPLETED
            step.end_time = time.time()
            step.duration = step.end_time - step.start_time
            step.result_summary = result_summary
            step.token_usage = token_usage
            step.cost_estimate = cost_estimate
            self._total_tokens += token_usage
            self._total_cost += cost_estimate
            self._notify_update(step_id, "completed")
  
    def fail_step(self, step_id: str, error_message: str):
        """標記步驟失敗"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.FAILED
            step.end_time = time.time()
            step.duration = step.end_time - step.start_time
            step.error_message = error_message
            self._notify_update(step_id, "failed")
  
    def retry_step(self, step_id: str):
        """標記步驟重試中"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.RETRYING
            step.retry_count += 1
            self._notify_update(step_id, "retrying")
  
    def wait_human(self, step_id: str):
        """標記步驟等待人工介入"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.WAITING_HUMAN
            self._notify_update(step_id, "waiting_human")
  
    def skip_step(self, step_id: str, reason: str = ""):
        """標記步驟跳過"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.SKIPPED
            step.result_summary = reason
            self._notify_update(step_id, "skipped")
  
    def _notify_update(self, step_id: str, event: str):
        """通知狀態變更"""
        if self.on_update:
            self.on_update({
                "task_id": self.task_id,
                "step_id": step_id,
                "event": event,
                "step": self.steps[step_id],
                "progress": self.get_progress(),
            })
  
    def get_progress(self) -> dict:
        """取得整體進度"""
        total = len(self.steps)
        if total == 0:
            return {"percentage": 0, "completed": 0, "total": 0}
      
        completed = sum(
            1 for s in self.steps.values()
            if s.status == StepStatus.COMPLETED
        )
        failed = sum(
            1 for s in self.steps.values()
            if s.status == StepStatus.FAILED
        )
      
        return {
            "percentage": round(completed / total * 100, 1),
            "completed": completed,
            "failed": failed,
            "total": total,
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(self._total_cost, 4),
            "elapsed_time": round(
                time.time() - self._start_time, 1
            ),
        }
  
    def render_tree(self) -> str:
        """渲染步驟樹狀圖（供 CLI / 日誌使用）"""
        lines = [
            f"📋 任務 [{self.task_id}]",
            f"{'─' * 50}",
        ]
      
        for step_id in self._step_order:
            step = self.steps[step_id]
            indent = "  " if step.parent_id else ""
          
            line = (
                f"{indent}{step.icon} {step.name} "
                f"[{step.status.value}]"
            )
          
            if step.elapsed_display != "-":
                line += f" ({step.elapsed_display})"
          
            if step.retry_count > 0:
                line += f" (重試 {step.retry_count} 次)"
          
            if step.result_summary:
                line += f"\n{indent}   └─ {step.result_summary}"
          
            if step.error_message:
                line += (
                    f"\n{indent}   └─ ⚠️ {step.error_message}"
                )
          
            lines.append(line)
      
        # 統計摘要
        progress = self.get_progress()
        lines.extend([
            f"{'─' * 50}",
            f"進度：{progress['percentage']}% | "
            f"✅ {progress['completed']}/{progress['total']} | "
            f"⏱️ {progress['elapsed_time']}s | "
            f"🪙 {progress['total_tokens']} tokens | "
            f"💰 ${progress['total_cost_usd']}",
        ])
      
        return "\n".join(lines)
```

---

## 8. 即時狀態面板

### 8.1 Web Dashboard（WebSocket 即時推送）

```python
# dashboard_server.py

import asyncio
import json
import time
from typing import Set
from dataclasses import dataclass, asdict
from step_tracker import StepTracker, StepStatus


@dataclass
class DashboardState:
    """儀表板全域狀態"""
    task_id: str
    task_description: str
    status: str = "running"          # running / completed / failed
    progress_percentage: float = 0
    current_step: str = ""
    steps: list = None
    total_tokens: int = 0
    total_cost_usd: float = 0
    elapsed_seconds: float = 0
    active_errors: list = None
    model_in_use: str = "gpt-4o"
  
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.active_errors is None:
            self.active_errors = []


class DashboardBroadcaster:
    """
    儀表板廣播器
  
    透過 WebSocket / SSE 向所有連線的客戶端推送即時狀態
    """
  
    def __init__(self):
        self._clients: Set = set()
        self._state: DashboardState = None
  
    def update_from_tracker(self, tracker: StepTracker):
        """從 StepTracker 更新儀表板狀態"""
        progress = tracker.get_progress()
      
        # 找出當前正在執行的步驟
        current_step = ""
        for step in tracker.steps.values():
            if step.status == StepStatus.RUNNING:
                current_step = step.name
                break
      
        steps_data = []
        for step_id in tracker._step_order:
            step = tracker.steps[step_id]
            steps_data.append({
                "id": step.id,
                "name": step.name,
                "description": step.description,
                "status": step.status.value,
                "icon": step.icon,
                "tool_name": step.tool_name,
                "elapsed": step.elapsed_display,
                "retry_count": step.retry_count,
                "result_summary": step.result_summary,
                "error_message": step.error_message,
                "token_usage": step.token_usage,
                "cost_estimate": step.cost_estimate,
            })
      
        self._state = DashboardState(
            task_id=tracker.task_id,
            task_description="",
            progress_percentage=progress["percentage"],
            current_step=current_step,
            steps=steps_data,
            total_tokens=progress["total_tokens"],
            total_cost_usd=progress["total_cost_usd"],
            elapsed_seconds=progress["elapsed_time"],
        )
      
        # 廣播給所有客戶端
        asyncio.create_task(self._broadcast())
  
    async def _broadcast(self):
        """廣播狀態到所有連線客戶端"""
        if not self._state:
            return
      
        message = json.dumps(asdict(self._state), default=str)
      
        disconnected = set()
        for client in self._clients:
            try:
                await client.send(message)
            except Exception:
                disconnected.add(client)
      
        self._clients -= disconnected
  
    def render_terminal(self, tracker: StepTracker) -> str:
        """
        終端機版即時面板（ANSI 輸出）
      
        適用於 CLI 環境，每次狀態變更時重新繪製
        """
        progress = tracker.get_progress()
      
        # 進度條
        bar_width = 30
        filled = int(
            bar_width * progress["percentage"] / 100
        )
        bar = "█" * filled + "░" * (bar_width - filled)
      
        lines = [
            "\033[2J\033[H",  # 清屏
            f"╔{'═' * 58}╗",
            f"║{'AutoAgent-TW 執行面板':^56}║",
            f"╠{'═' * 58}╣",
            f"║  任務 ID: {tracker.task_id:<45}║",
            f"║  進度: [{bar}] {progress['percentage']:>5.1f}%  ║",
            f"║  步驟: {progress['completed']}/{progress['total']}"
            f" 完成 | {progress['failed']} 失敗"
            f"{' ' * 20}║",
            f"║  時間: {progress['elapsed_time']:.1f}s"
            f" | Tokens: {progress['total_tokens']}"
            f" | 💰 ${progress['total_cost_usd']:.4f}"
            f"{' ' * 8}║",
            f"╠{'═' * 58}╣",
        ]
      
        # 步驟列表
        for step_id in tracker._step_order:
            step = tracker.steps[step_id]
            status_line = (
                f"║  {step.icon} {step.name:<35}"
                f"{step.elapsed_display:>10}  ║"
            )
            lines.append(status_line)
          
            if step.status == StepStatus.RETRYING:
                lines.append(
                    f"║     🔁 重試中（第 {step.retry_count} 次）"
                    f"{' ' * 28}║"
                )
            elif step.status == StepStatus.FAILED:
                err_msg = (step.error_message or "")[:40]
                lines.append(
                    f"║     ❌ {err_msg}"
                    f"{' ' * (48 - len(err_msg))}║"
                )
      
        lines.append(f"╚{'═' * 58}╝")
      
        return "\n".join(lines)
```

### 8.2 終端機面板預覽

```
╔════════════════════════════════════════════════════════╗
║              AutoAgent-TW 執行面板                      ║
╠════════════════════════════════════════════════════════╣
║  任務 ID: a3f8b2c1                                     ║
║  進度: [████████████████░░░░░░░░░░░░░░]  53.3%        ║
║  步驟: 4/7 完成 | 0 失敗                               ║
║  時間: 23.4s | Tokens: 3,842 | 💰 $0.0192             ║
╠════════════════════════════════════════════════════════╣
║  ✅ 搜尋 HN 熱門文章                     2.1s          ║
║  ✅ 篩選 LLM 相關文章                    0.3s          ║
║  ✅ 摘要文章 #1                          3.2s          ║
║  ✅ 摘要文章 #2                          2.8s          ║
║  🔄 摘要文章 #3                       5.2s (進行中)    ║
║  ⏳ 摘要文章 #4                           -            ║
║  ⏳ 整理為報告                           -             ║
╚════════════════════════════════════════════════════════╝
```

---

## 9. 執行日誌系統

```python
# execution_logger.py

import json
import time
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """結構化日誌條目"""
    timestamp: str
    level: str
    task_id: str
    step_id: str
    event: str                    # 事件類型
    message: str
    tool_name: Optional[str] = None
    token_usage: int = 0
    duration_ms: float = 0
    error_category: Optional[str] = None
    retry_count: int = 0
    raw_data: Optional[dict] = None  # 原始資料（debug 用）


class ExecutionLogger:
    """
    執行日誌系統
  
    同時輸出到：
    1. 檔案（JSON Lines 格式，方便後續分析）
    2. 終端機（人類可讀格式）
    3. 記憶體（供即時查詢）
    """
  
    def __init__(
        self,
        task_id: str,
        log_dir: str = "./logs",
        console_verbose: bool = True,
        max_memory_entries: int = 1000,
    ):
        self.task_id = task_id
        self.console_verbose = console_verbose
        self._memory_log: list[LogEntry] = []
        self._max_memory = max_memory_entries
      
        # 建立日誌目錄
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_file = os.path.join(
            log_dir, f"task_{task_id}_{timestamp}.jsonl"
        )
  
    def log(
        self,
        level: LogLevel,
        step_id: str,
        event: str,
        message: str,
        tool_name: str = None,
        token_usage: int = 0,
        duration_ms: float = 0,
        error_category: str = None,
        retry_count: int = 0,
        raw_data: dict = None,
    ):
        """寫入一筆日誌"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            task_id=self.task_id,
            step_id=step_id,
            event=event,
            message=message,
            tool_name=tool_name,
            token_usage=token_usage,
            duration_ms=duration_ms,
            error_category=error_category,
            retry_count=retry_count,
            raw_data=raw_data,
        )
      
        # 寫入檔案
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")
      
        # 存入記憶體
        self._memory_log.append(entry)
        if len(self._memory_log) > self._max_memory:
            self._memory_log = self._memory_log[-self._max_memory:]
      
        # 終端輸出
        if self.console_verbose:
            self._console_print(entry)
  
    def _console_print(self, entry: LogEntry):
        """終端機格式化輸出"""
        level_colors = {
            "DEBUG": "\033[90m",      # 灰色
            "INFO": "\033[36m",       # 青色
            "WARNING": "\033[33m",    # 黃色
            "ERROR": "\033[31m",      # 紅色
            "CRITICAL": "\033[41m",   # 紅色背景
        }
        reset = "\033[0m"
        color = level_colors.get(entry.level, "")
      
        time_str = entry.timestamp[11:19]  # HH:MM:SS
      
        print(
            f"{color}[{time_str}] [{entry.level:>8}] "
            f"[{entry.step_id}] {entry.message}{reset}"
        )
      
        if entry.error_category:
            print(
                f"         └─ 錯誤類型: {entry.error_category}"
                f" | 重試次數: {entry.retry_count}"
            )
        if entry.token_usage > 0:
            print(
                f"         └─ Token 用量: {entry.token_usage}"
            )
  
    # ========================================
    #  便捷方法
    # ========================================
  
    def info(self, step_id: str, event: str, message: str, **kw):
        self.log(LogLevel.INFO, step_id, event, message, **kw)
  
    def warning(self, step_id: str, event: str, message: str, **kw):
        self.log(LogLevel.WARNING, step_id, event, message, **kw)
  
    def error(self, step_id: str, event: str, message: str, **kw):
        self.log(LogLevel.ERROR, step_id, event, message, **kw)
  
    def debug(self, step_id: str, event: str, message: str, **kw):
        self.log(LogLevel.DEBUG, step_id, event, message, **kw)
  
    # ========================================
    #  查詢與分析
    # ========================================
  
    def get_errors(self) -> list[LogEntry]:
        """取得所有錯誤日誌"""
        return [
            e for e in self._memory_log
            if e.level in ("ERROR", "CRITICAL")
        ]
  
    def get_retry_events(self) -> list[LogEntry]:
        """取得所有重試事件"""
        return [
            e for e in self._memory_log
            if e.retry_count > 0
        ]
  
    def get_token_usage_by_step(self) -> dict:
        """按步驟統計 token 用量"""
        usage = {}
        for entry in self._memory_log:
            if entry.token_usage > 0:
                sid = entry.step_id
                usage[sid] = usage.get(sid, 0) + entry.token_usage
        return usage
  
    def get_summary(self) -> dict:
        """取得日誌摘要"""
        return {
            "task_id": self.task_id,
            "total_entries": len(self._memory_log),
            "errors": len(self.get_errors()),
            "retries": len(self.get_retry_events()),
            "total_tokens": sum(
                e.token_usage for e in self._memory_log
            ),
            "token_by_step": self.get_token_usage_by_step(),
            "log_file": self._log_file,
        }
  
    def export_markdown(self) -> str:
        """匯出為 Markdown 格式報告"""
        lines = [
            f"# 執行報告 - Task {self.task_id}",
            f"",
            f"## 日誌摘要",
            f"",
            f"| 項目 | 數值 |",
            f"|---|---|",
            f"| 總日誌條目 | {len(self._memory_log)} |",
            f"| 錯誤數量 | {len(self.get_errors())} |",
            f"| 重試事件 | {len(self.get_retry_events())} |",
            f"| 總 Token | {sum(e.token_usage for e in self._memory_log)} |",
            f"",
            f"## 詳細日誌",
            f"",
        ]
      
        for entry in self._memory_log:
            icon = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "CRITICAL": "🚨",
                "DEBUG": "🔍",
            }.get(entry.level, "•")
          
            lines.append(
                f"- {icon} **[{entry.timestamp[11:19]}]** "
                f"`{entry.step_id}` {entry.message}"
            )
      
        return "\n".join(lines)
```

### 9.1 JSON Lines 日誌範例

```jsonl
{"timestamp":"2025-06-15T10:30:01.123","level":"INFO","task_id":"a3f8","step_id":"step_1","event":"step_start","message":"開始搜尋 HN 熱門文章","tool_name":"web_search","token_usage":0,"duration_ms":0}
{"timestamp":"2025-06-15T10:30:03.456","level":"INFO","task_id":"a3f8","step_id":"step_1","event":"step_complete","message":"搜尋完成，找到 15 篇文章","tool_name":"web_search","token_usage":1204,"duration_ms":2333}
{"timestamp":"2025-06-15T10:30:04.789","level":"WARNING","task_id":"a3f8","step_id":"step_3","event":"retry","message":"API 回應超時，正在重試","tool_name":"llm_summarize","token_usage":0,"duration_ms":0,"error_category":"timeout","retry_count":1}
{"timestamp":"2025-06-15T10:30:08.012","level":"INFO","task_id":"a3f8","step_id":"step_3","event":"step_complete","message":"摘要完成（重試 1 次後成功）","tool_name":"llm_summarize","token_usage":856,"duration_ms":3223,"retry_count":1}
```

---

## 10. 使用者介入機制

```python
# user_intervention.py

import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any


class InterventionType(Enum):
    """介入請求類型"""
    CLARIFICATION = "clarification"     # 需要補充說明
    CONFIRMATION = "confirmation"       # 需要確認操作
    CHOICE = "choice"                   # 需要選擇
    ERROR_RECOVERY = "error_recovery"   # 錯誤恢復選擇
    APPROVAL = "approval"              # 敏感操作審批


@dataclass
class InterventionRequest:
    """介入請求"""
    request_id: str
    type: InterventionType
    message: str
    options: list[str] = None           # 選擇題的選項
    context: dict = None                # 額外上下文
    timeout: float = 300.0              # 超時時間（秒），預設 5 分鐘
    default_action: str = None          # 超時後的預設動作


@dataclass
class InterventionResponse:
    """介入回應"""
    request_id: str
    selected_option: int = None         # 選擇題的選項索引
    free_text: str = ""                 # 自由文字回應
    approved: bool = False              # 審批結果


class InterventionManager:
    """
    使用者介入管理器
  
    當 Agent 需要使用者輸入時，
    透過此管理器發送請求並等待回應
    """
  
    def __init__(self, notify_func: Callable = None):
        """
        Parameters
        ----------
        notify_func : Callable
            通知使用者的函式，簽名：
            async (request: InterventionRequest) -> None
            例如：發送 Telegram 訊息、LINE 訊息等
        """
        self.notify_func = notify_func
        self._pending: dict[str, asyncio.Event] = {}
        self._responses: dict[str, InterventionResponse] = {}
  
    async def request(
        self, request: InterventionRequest
    ) -> InterventionResponse:
        """
        發送介入請求，等待使用者回應
      
        支援超時機制：超過 timeout 秒未回應則執行預設動作
        """
        event = asyncio.Event()
        self._pending[request.request_id] = event
      
        # 通知使用者
        if self.notify_func:
            await self.notify_func(request)
      
        try:
            # 等待回應或超時
            await asyncio.wait_for(
                event.wait(), 
                timeout=request.timeout,
            )
          
            response = self._responses.get(request.request_id)
            return response
      
        except asyncio.TimeoutError:
            # 超時 → 執行預設動作
            return InterventionResponse(
                request_id=request.request_id,
                free_text=request.default_action or "timeout",
            )
      
        finally:
            self._pending.pop(request.request_id, None)
            self._responses.pop(request.request_id, None)
  
    def submit_response(self, response: InterventionResponse):
        """提交使用者回應（由外部介面呼叫）"""
        request_id = response.request_id
        if request_id in self._pending:
            self._responses[request_id] = response
            self._pending[request_id].set()
  
    def format_for_telegram(
        self, request: InterventionRequest
    ) -> str:
        """格式化為 Telegram 訊息"""
        lines = [request.message, ""]
      
        if request.type == InterventionType.CHOICE:
            for i, option in enumerate(request.options or []):
                lines.append(f"  [{i+1}] {option}")
            lines.append("")
            lines.append("請回覆數字選擇：")
      
        elif request.type == InterventionType.ERROR_RECOVERY:
            lines.append("請選擇處理方式：")
            lines.append("  /retry - 重試整個任務")
            lines.append("  /skip - 跳過此步驟")
            lines.append("  /edit - 修改任務描述")
            lines.append("  /abort - 中止任務")
      
        elif request.type == InterventionType.CONFIRMATION:
            lines.append("請確認：")
            lines.append("  /yes - 確認執行")
            lines.append("  /no - 取消")
      
        lines.append(f"\n⏰ 請在 {int(request.timeout/60)} 分鐘內回覆")
      
        return "\n".join(lines)
```

### 10.1 使用者介入流程圖

```
Agent 執行中
    │
    ▼
遇到需要使用者輸入的情況
    │
    ▼
┌──────────────────────┐
│ 建立 InterventionRequest │
│ - 類型：錯誤恢復選擇      │
│ - 訊息：具體描述問題      │
│ - 選項：重試/跳過/修改/中止│
│ - 超時：5 分鐘           │
│ - 預設：跳過此步驟        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 通知使用者              │
│ （Telegram / LINE / CLI）│
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     │           │
  有回應      5 分鐘超時
     │           │
     ▼           ▼
 使用者選擇   執行預設動作
     │       （跳過此步驟）
     ▼
 根據選擇繼續執行
```

---

## 11. 成本與 Token 監控

```python
# cost_monitor.py

from dataclasses import dataclass, field
from typing import Optional


# 模型定價表（美元 / 1M tokens）
MODEL_PRICING = {
    # OpenAI
    "gpt-4o":           {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":      {"input": 0.15,  "output": 0.60},
    "gpt-3.5-turbo":    {"input": 0.50,  "output": 1.50},
    "o1":               {"input": 15.00, "output": 60.00},
    "o1-mini":          {"input": 3.00,  "output": 12.00},
  
    # Anthropic
    "claude-sonnet-4-20250514": {"input": 3.00,  "output": 15.00},
    "claude-haiku":             {"input": 0.25,  "output": 1.25},
  
    # Google
    "gemini-2.5-pro":   {"input": 1.25,  "output": 10.00},
    "gemini-2.5-flash": {"input": 0.15,  "output": 0.60},
}


@dataclass
class CostEntry:
    """單次呼叫的成本記錄"""
    step_id: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


@dataclass
class BudgetConfig:
    """預算配置"""
    daily_limit_usd: float = 5.0       # 每日上限
    per_task_limit_usd: float = 1.0    # 單任務上限
    warning_threshold: float = 0.8     # 警告閾值（80%）
    alert_callback: Optional[object] = None


class CostMonitor:
    """
    成本監控器
  
    即時追蹤 token 用量與費用，
    在接近預算上限時發出警告
    """
  
    def __init__(self, budget: BudgetConfig = None):
        self.budget = budget or BudgetConfig()
        self.entries: list[CostEntry] = []
        self._task_cost = 0.0
        self._daily_cost = 0.0
  
    def record(
        self,
        step_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostEntry:
        """記錄一次 API 呼叫的成本"""
        pricing = MODEL_PRICING.get(model, {
            "input": 1.0, "output": 3.0  # 預設估值
        })
      
        input_cost = input_tokens / 1_000_000 * pricing["input"]
        output_cost = (
            output_tokens / 1_000_000 * pricing["output"]
        )
        total = input_cost + output_cost
      
        entry = CostEntry(
            step_id=step_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total,
        )
      
        self.entries.append(entry)
        self._task_cost += total
        self._daily_cost += total
      
        # 檢查預算警告
        self._check_budget()
      
        return entry
  
    def _check_budget(self):
        """檢查預算是否接近上限"""
        task_ratio = (
            self._task_cost / self.budget.per_task_limit_usd
        )
        daily_ratio = (
            self._daily_cost / self.budget.daily_limit_usd
        )
      
        if task_ratio >= 1.0:
            self._alert(
                "🚨", 
                f"任務預算已達上限！"
                f"(${self._task_cost:.4f} / "
                f"${self.budget.per_task_limit_usd})"
            )
        elif task_ratio >= self.budget.warning_threshold:
            self._alert(
                "⚠️",
                f"任務預算即將用盡 "
                f"({task_ratio:.0%})："
                f"${self._task_cost:.4f} / "
                f"${self.budget.per_task_limit_usd}"
            )
      
        if daily_ratio >= 1.0:
            self._alert(
                "🚨",
                f"每日預算已達上限！"
                f"(${self._daily_cost:.4f} / "
                f"${self.budget.daily_limit_usd})"
            )
  
    def _alert(self, icon: str, message: str):
        """發送預算警告"""
        print(f"\n{icon} {message}\n")
        if self.budget.alert_callback:
            self.budget.alert_callback(message)
  
    def get_report(self) -> dict:
        """取得成本報告"""
        by_step = {}
        by_model = {}
      
        for e in self.entries:
            # 按步驟統計
            if e.step_id not in by_step:
                by_step[e.step_id] = {
                    "tokens": 0, "cost": 0.0
                }
            by_step[e.step_id]["tokens"] += (
                e.input_tokens + e.output_tokens
            )
            by_step[e.step_id]["cost"] += e.total_cost
          
            # 按模型統計
            if e.model not in by_model:
                by_model[e.model] = {
                    "calls": 0, "tokens": 0, "cost": 0.0
                }
            by_model[e.model]["calls"] += 1
            by_model[e.model]["tokens"] += (
                e.input_tokens + e.output_tokens
            )
            by_model[e.model]["cost"] += e.total_cost
      
        return {
            "task_total_cost": round(self._task_cost, 6),
            "daily_total_cost": round(self._daily_cost, 6),
            "budget_remaining": round(
                self.budget.per_task_limit_usd - self._task_cost, 
                6
            ),
            "budget_usage_percent": round(
                self._task_cost / self.budget.per_task_limit_usd * 100, 
                1
            ),
            "by_step": by_step,
            "by_model": by_model,
            "total_api_calls": len(self.entries),
            "total_tokens": sum(
                e.input_tokens + e.output_tokens 
                for e in self.entries
            ),
        }
  
    def render_cost_bar(self) -> str:
        """渲染預算使用進度條"""
        ratio = min(
            self._task_cost / self.budget.per_task_limit_usd, 
            1.0
        )
        bar_width = 25
        filled = int(bar_width * ratio)
      
        if ratio < 0.5:
            color = "\033[32m"   # 綠色
        elif ratio < 0.8:
            color = "\033[33m"   # 黃色
        else:
            color = "\033[31m"   # 紅色
        reset = "\033[0m"
      
        bar = "█" * filled + "░" * (bar_width - filled)
      
        return (
            f"{color}[{bar}] {ratio:.0%}{reset} "
            f"| ${self._task_cost:.4f} / "
            f"${self.budget.per_task_limit_usd}"
        )
```

---

## 12. 完整範例：端到端流程

以下展示所有模組如何串在一起運作：

```python
# example_full_workflow.py

import asyncio
from error_classifier import ErrorClassifier, ErrorSeverity
from retry_engine import RetryEngine, RetryPolicy
from fallback_manager import FallbackManager
from circuit_breaker import CircuitBreakerRegistry
from recovery_workflow import RecoveryWorkflow
from step_tracker import StepTracker
from execution_logger import ExecutionLogger
from cost_monitor import CostMonitor, BudgetConfig
from user_intervention import (
    InterventionManager, InterventionRequest, 
    InterventionType, InterventionResponse,
)


async def main():
    """完整工作流範例：自動搜尋並摘要文章"""
  
    # ========================================
    #  初始化所有模組
    # ========================================
    task_id = "demo_001"
  
    logger = ExecutionLogger(task_id=task_id)
    tracker = StepTracker(
        task_id=task_id,
        on_update=lambda event: logger.info(
            event["step_id"], event["event"],
            f"步驟狀態變更：{event['event']}"
        ),
    )
    cost_monitor = CostMonitor(
        budget=BudgetConfig(
            daily_limit_usd=5.0,
            per_task_limit_usd=0.50,
        )
    )
    recovery = RecoveryWorkflow(config={
        "model_chain": [
            "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"
        ],
        "tool_alternatives": {
            "google_search": [
                "bing_search", "duckduckgo_search"
            ],
        },
    })
  
    # ========================================
    #  定義任務步驟
    # ========================================
    s1 = tracker.add_step(
        "搜尋 HN 熱門文章",
        "使用搜尋工具取得最新文章",
        tool_name="web_search",
    )
    s2 = tracker.add_step(
        "篩選 LLM 相關文章",
        "從搜尋結果中過濾出 LLM 主題",
    )
    s3 = tracker.add_step(
        "摘要文章",
        "為每篇文章產生中文摘要",
        tool_name="llm_summarize",
    )
    s4 = tracker.add_step(
        "整理為報告",
        "將所有摘要整合為最終報告",
    )
  
    # ========================================
    #  執行任務
    # ========================================
    print("🚀 任務開始\n")
    print(tracker.render_tree())
    print()
  
    # --- Step 1：搜尋 ---
    tracker.start_step(s1)
    logger.info(s1, "step_start", "開始搜尋 HN 熱門文章")
  
    try:
        # 模擬搜尋 API 呼叫
        await simulate_search()
        tracker.complete_step(
            s1, 
            result_summary="找到 15 篇文章",
            token_usage=1204,
            cost_estimate=0.003,
        )
        cost_monitor.record(s1, "gpt-4o", 800, 404)
        logger.info(s1, "step_complete", "搜尋完成，找到 15 篇")
    except Exception as e:
        # 錯誤處理
        agent_error = ErrorClassifier.classify(e, s1, "web_search")
        logger.error(
            s1, "step_error", str(e),
            error_category=agent_error.category.value,
        )
      
        # 嘗試恢復
        report = await recovery.handle(
            agent_error,
            original_func=simulate_search,
            context={"breaker_name": "web_search"},
        )
      
        if report.final_result:
            tracker.complete_step(
                s1, 
                result_summary="（降級後完成）找到 10 篇文章"
            )
            logger.info(
                s1, "recovery_success", 
                report.message_to_user
            )
        else:
            tracker.fail_step(s1, report.message_to_user)
  
    # --- Step 2：篩選 ---
    tracker.start_step(s2)
    logger.info(s2, "step_start", "篩選 LLM 相關文章")
    await asyncio.sleep(0.3)
    tracker.complete_step(
        s2,
        result_summary="篩選出 5 篇 LLM 相關文章",
        token_usage=512,
        cost_estimate=0.001,
    )
    cost_monitor.record(s2, "gpt-4o", 300, 212)
  
    # --- Step 3：摘要（模擬重試）---
    tracker.start_step(s3)
    logger.info(s3, "step_start", "開始摘要文章")
  
    for article_idx in range(3):
        sub_step = tracker.add_step(
            f"摘要文章 #{article_idx + 1}",
            parent_id=s3,
        )
        tracker.start_step(sub_step)
      
        try:
            if article_idx == 1:
                # 模擬第二篇文章摘要時超時
                raise TimeoutError("API 回應超時")
          
            await asyncio.sleep(0.5)
            tracker.complete_step(
                sub_step,
                result_summary=f"文章 #{article_idx+1} 摘要完成",
                token_usage=856,
                cost_estimate=0.009,
            )
            cost_monitor.record(
                sub_step, "gpt-4o", 500, 356
            )
      
        except Exception as e:
            tracker.retry_step(sub_step)
            agent_error = ErrorClassifier.classify(
                e, sub_step, "llm_summarize"
            )
            logger.warning(
                sub_step, "retry",
                f"超時，正在重試...",
                error_category=agent_error.category.value,
                retry_count=1,
            )
          
            # 重試成功
            await asyncio.sleep(1.0)
            tracker.complete_step(
                sub_step,
                result_summary=(
                    f"文章 #{article_idx+1} 摘要完成"
                    f"（重試 1 次）"
                ),
                token_usage=920,
                cost_estimate=0.009,
            )
            cost_monitor.record(
                sub_step, "gpt-4o", 550, 370
            )
            logger.info(
                sub_step, "retry_success",
                "重試成功"
            )
  
    tracker.complete_step(s3, result_summary="3 篇文章摘要完成")
  
    # --- Step 4：整理報告 ---
    tracker.start_step(s4)
    logger.info(s4, "step_start", "整理最終報告")
    await asyncio.sleep(0.5)
    tracker.complete_step(
        s4,
        result_summary="報告已生成（1,200 字）",
        token_usage=1500,
        cost_estimate=0.015,
    )
    cost_monitor.record(s4, "gpt-4o", 800, 700)
  
    # ========================================
    #  輸出最終結果
    # ========================================
    print("\n" + "=" * 60)
    print(tracker.render_tree())
    print()
    print("📊 成本報告：")
    report = cost_monitor.get_report()
    print(f"   總花費：${report['task_total_cost']:.4f}")
    print(f"   總 Tokens：{report['total_tokens']}")
    print(f"   API 呼叫：{report['total_api_calls']} 次")
    print(f"   預算使用：{report['budget_usage_percent']}%")
    print(f"   {cost_monitor.render_cost_bar()}")
    print()
    print("📝 日誌摘要：")
    summary = logger.get_summary()
    print(f"   錯誤：{summary['errors']} 次")
    print(f"   重試：{summary['retries']} 次")
    print(f"   日誌檔：{summary['log_file']}")


async def simulate_search():
    """模擬搜尋（成功情況）"""
    await asyncio.sleep(0.5)
    return ["article1", "article2", "article3"]


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 13. 設定檔參考

建立 `agent_config.yaml`：

```yaml
# agent_config.yaml
# AutoAgent-TW 錯誤處理與透明化設定

# ============================================
#  重試策略
# ============================================
retry:
  # Level 1 - 暫時性錯誤
  transient:
    max_retries: 5
    base_delay: 1.0          # 秒
    max_delay: 30.0
    exponential_base: 2.0
    jitter: true             # ±25% 隨機抖動
  
  # Level 2 - 可恢復錯誤
  recoverable:
    max_retries: 3
    base_delay: 2.0
    max_delay: 15.0
    exponential_base: 2.0
    jitter: true
  
  # Level 3 - 依賴服務錯誤
  dependency:
    max_retries: 2
    base_delay: 5.0
    max_delay: 60.0
    exponential_base: 2.0
    jitter: true

# ============================================
#  熔斷器
# ============================================
circuit_breaker:
  default:
    failure_threshold: 5     # 連續失敗 5 次後熔斷
    recovery_timeout: 30.0   # 熔斷 30 秒後嘗試恢復
    half_open_max_calls: 3   # 恢復時最多試探 3 次
    success_threshold: 2     # 試探成功 2 次後完全恢復
  
  # 特定服務的覆蓋設定
  overrides:
    openai_api:
      failure_threshold: 3
      recovery_timeout: 60.0
    web_search:
      failure_threshold: 5
      recovery_timeout: 15.0

# ============================================
#  降級策略
# ============================================
fallback:
  model_chain:
    - gpt-4o
    - gpt-4o-mini
    - gpt-3.5-turbo
  
  tool_alternatives:
    google_search:
      - bing_search
      - duckduckgo_search
    web_scraper:
      - requests_fallback
      - curl_fallback
  
  # 自動摘要設定
  context_management:
    max_context_tokens: 8000
    summary_trigger_ratio: 0.8    # 達到 80% 時觸發摘要
    keep_last_n_messages: 5
    summary_max_tokens: 500

# ============================================
#  預算控制
# ============================================
budget:
  daily_limit_usd: 5.0
  per_task_limit_usd: 1.0
  warning_threshold: 0.8    # 80% 時發出警告
  
  # 按任務類型的預算上限
  task_overrides:
    simple_query: 0.10
    research_report: 0.50
    code_generation: 0.30

# ============================================
#  透明化設定
# ============================================
transparency:
  # 日誌
  logging:
    level: INFO              # DEBUG / INFO / WARNING / ERROR
    log_dir: ./logs
    console_verbose: true
    max_file_size_mb: 10
    retention_days: 30
  
  # 終端面板
  terminal:
    refresh_interval: 1.0    # 秒
    show_cost_bar: true
    show_token_usage: true
    color_output: true
  
  # 使用者通知
  notifications:
    on_step_complete: true
    on_error: true
    on_retry: true
    on_recovery: true
    on_budget_warning: true
    on_task_complete: true
    on_human_intervention_needed: true

# ============================================
#  使用者介入
# ============================================
intervention:
  default_timeout: 300.0     # 5 分鐘
  auto_skip_on_timeout: false
  require_approval_for:
    - file_deletion
    - api_key_rotation
    - payment_operations
```

---

## 14. 疑難排解

### 常見問題

**Q：重試一直失敗，但錯誤訊息看起來不嚴重？**

```
檢查項目：
1. 確認錯誤分類是否正確 → 查看 error_classifier.py 的分類邏輯
2. 檢查熔斷器是否已開啟 → circuit_breaker.get_all_stats()
3. 確認 API 金鑰是否有效
4. 查看日誌檔中的詳細錯誤堆疊
```

**Q：終端面板顯示亂碼？**

```
解決方案：
1. 確認終端支援 UTF-8：export LANG=en_US.UTF-8
2. 確認終端寬度 >= 60 字元
3. 若不支援 ANSI，設定 transparency.terminal.color_output: false
```

**Q：成本監控不準確？**

```
原因：MODEL_PRICING 定價表可能過時
解決：定期更新 cost_monitor.py 中的 MODEL_PRICING 字典
建議：在每次模型更新後檢查 OpenAI / Anthropic 官方定價頁面
```

**Q：日誌檔越來越大？**

```
解決方案：
1. 設定 retention_days 自動清理舊日誌
2. 設定 max_file_size_mb 限制單檔大小
3. 定期執行：find ./logs -name "*.jsonl" -mtime +30 -delete
```

---

## 附錄：模組依賴關係

```
error_classifier.py      ← 所有模組的基礎
    │
    ├── retry_engine.py  ← 依賴 error_classifier
    │
    ├── fallback_manager.py ← 依賴 error_classifier
    │
    ├── circuit_breaker.py  ← 獨立模組
    │
    └── recovery_workflow.py ← 依賴以上全部
            │
            ├── step_tracker.py   ← 獨立模組
            ├── execution_logger.py ← 獨立模組
            ├── cost_monitor.py   ← 獨立模組
            └── user_intervention.py ← 獨立模組
```

---

> **文件結束**
>
> 本文件為 AutoAgent-TW 錯誤處理與執行過程透明化的完整實作指南。
> 所有程式碼均為可直接使用的 Python 實作，可根據專案需求進行調整。
>
> 如有問題，請提交 Issue 至 GitHub 倉庫。

```

---

這份文件涵蓋了 **7 個核心模組**，每個模組都可以獨立使用，也可以組合成完整的錯誤處理與透明化系統：

| 模組 | 職責 | 可獨立使用 |
|---|---|---|
| `error_classifier.py` | 錯誤自動分類 | ✅ |
| `retry_engine.py` | 指數退避重試 | ✅ |
| `fallback_manager.py` | 降級策略管理 | 需 classifier |
| `circuit_breaker.py` | 熔斷器 | ✅ |
| `recovery_workflow.py` | 統一恢復協調 | 需以上全部 |
| `step_tracker.py` | 步驟追蹤 | ✅ |
| `execution_logger.py` | 結構化日誌 | ✅ |
| `cost_monitor.py` | 成本監控 | ✅ |
| `user_intervention.py` | 使用者介入 | ✅ |
```
