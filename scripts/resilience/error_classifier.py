"""
Error Classification System (Phase 1)
提供精準的錯誤分類，將各式異常映射為標準的嚴重性與種類。
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import time

class ErrorSeverity(Enum):
    """
    錯誤嚴重程度分類
  
    Level 1 - TRANSIENT:   暫時性錯誤，指數量級退避重試即可解決
    Level 2 - RECOVERABLE: 可恢復錯誤，需要降級或切換策略（模型降級、摘要）
    Level 3 - DEPENDENCY:  依賴服務錯誤，需要等待或啟動熔斷器
    Level 4 - LOGICAL:     邏輯錯誤，需要修正任務描述或參數 (交由高階 Repair Loop)
    Level 5 - FATAL:       致命錯誤，必須人工介入 (LINE Notify)
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
    BUDGET_EXHAUSTED = "budget_exhausted" # 加碼：防暴走
    UNKNOWN_FATAL = "unknown_fatal"

@dataclass
class AgentError:
    """統一結構化錯誤物件"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    step_id: str                          # 發生錯誤的步驟 ID
    tool_name: Optional[str] = None       # 涉及的工具名稱
    raw_exception: Optional[Exception] = None
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
  
    def to_user_message(self) -> str:
        messages = {
            ErrorCategory.RATE_LIMIT: "⏳ API 呼叫過於頻繁，正在自動等待後重試...",
            ErrorCategory.TIMEOUT: "⏱️ 回應超時，正在重新嘗試...",
            ErrorCategory.NETWORK_BLIP: "🌐 網路連線不穩，正在重新連線...",
            ErrorCategory.API_DOWN: "🔧 目標服務暫時不可用，正在嘗試替代方案...",
            ErrorCategory.AUTH_EXPIRED: "🔑 API 金鑰可能已過期，請檢查設定。",
            ErrorCategory.QUOTA_EXCEEDED: "💰 API 額度已用盡，準備啟動模型降級...",
            ErrorCategory.CONTEXT_OVERFLOW: "📄 上下文過長，正在自動摘要以壓縮 token...",
            ErrorCategory.TASK_AMBIGUOUS: "🤔 任務描述不夠明確，交由 Repair Loop 處理...",
            ErrorCategory.INVALID_PARAMS: "⚠️ 參數有誤，交由 Repair Loop 自動修正...",
            ErrorCategory.SECURITY_VIOLATION: "🛡️ 觸發安全規則，已停止執行。",
            ErrorCategory.BUDGET_EXHAUSTED: "💸 已達到預算上限，Agent 暫停工作請求批准。"
        }
        return messages.get(self.category, f"❌ 發生錯誤 ({self.severity.name}): {self.message}")

class ErrorClassifier:
    """
    錯誤分類器
    將各種原生的 Exception 映射為 AgentError
    """
    @staticmethod
    def classify(exception: Exception, step_id: str = "unknown", tool_name: Optional[str] = None) -> AgentError:
        err_str = str(exception).lower()
        
        # --- 暫時性 / API 限制 ---
        if "rate limit" in err_str or "429" in err_str or "too many requests" in err_str:
            return AgentError(ErrorCategory.RATE_LIMIT, ErrorSeverity.TRANSIENT, str(exception), step_id, tool_name, exception)
        
        if isinstance(exception, TimeoutError) or "timeout" in err_str or "408" in err_str or "504" in err_str:
            return AgentError(ErrorCategory.TIMEOUT, ErrorSeverity.TRANSIENT, str(exception), step_id, tool_name, exception)
            
        if isinstance(exception, ConnectionError) or "connection" in err_str or "reset by peer" in err_str:
            return AgentError(ErrorCategory.NETWORK_BLIP, ErrorSeverity.TRANSIENT, str(exception), step_id, tool_name, exception)
            
        # --- 可恢復 / Token 溢出 ---
        if "context_length" in err_str or "maximum context" in err_str or "token limit" in err_str or "max context length" in err_str:
            return AgentError(ErrorCategory.CONTEXT_OVERFLOW, ErrorSeverity.RECOVERABLE, str(exception), step_id, tool_name, exception)
            
        if "jsondecodeerror" in err_str or "parse error" in err_str or "invalid format" in err_str:
            return AgentError(ErrorCategory.PARSE_ERROR, ErrorSeverity.RECOVERABLE, str(exception), step_id, tool_name, exception)
            
        # --- 依賴與 Quota ---
        if "401" in err_str or "authentication" in err_str or "api_key" in err_str:
            return AgentError(ErrorCategory.AUTH_EXPIRED, ErrorSeverity.DEPENDENCY, str(exception), step_id, tool_name, exception)
            
        if "quota" in err_str or "billing" in err_str or "insufficient_quota" in err_str or "credit" in err_str:
            return AgentError(ErrorCategory.QUOTA_EXCEEDED, ErrorSeverity.DEPENDENCY, str(exception), step_id, tool_name, exception)
            
        if "502" in err_str or "503" in err_str or "bad gateway" in err_str:
            return AgentError(ErrorCategory.API_DOWN, ErrorSeverity.DEPENDENCY, str(exception), step_id, tool_name, exception)
            
        # --- 安全與預算 (FATAL) ---
        if "budget" in err_str and "exceeded" in err_str:
            return AgentError(ErrorCategory.BUDGET_EXHAUSTED, ErrorSeverity.FATAL, str(exception), step_id, tool_name, exception)
        
        # --- 未知錯誤 (保守歸類為 FATAL) ---
        return AgentError(ErrorCategory.UNKNOWN_FATAL, ErrorSeverity.FATAL, str(exception), step_id, tool_name, exception)
