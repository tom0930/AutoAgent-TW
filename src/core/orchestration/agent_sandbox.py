import logging
from typing import Dict, Any, Tuple
from src.core.orchestration.agent_identity import CapabilityCard, TrustLevel
from src.core.permission_engine import PermissionEngine

logger = logging.getLogger("Orchestration.Sandbox")

class AgentSandbox:
    """
    Security Sandbox for Multi-Agent Tool Execution (Phase 171 v2.1).
    Enforces role-based access control and risk-based interception.
    """
    def __init__(self, card: CapabilityCard, permission_engine: PermissionEngine):
        self.card = card
        self.engine = permission_engine

    def validate_tool_use(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates if the agent is allowed to use a specific tool with given arguments.
        
        Returns:
            (allowed: bool, reason: str)
        """
        # 1. Identity Check: Is this tool in the allowed list for this role?
        if tool_name not in self.card.allowed_tools:
            return False, f"Identity Violation: Role '{self.card.role}' is not authorized to use tool '{tool_name}'."

        # 2. Blacklist Check: Explicitly forbidden?
        if tool_name in self.card.forbidden_tools:
            return False, f"Policy Violation: Tool '{tool_name}' is explicitly forbidden for this agent."

        # 3. Risk-based Trust Check: Does the risk level exceed the agent's trust level?
        risk_level = self.engine.get_risk_level(tool_name)
        # Handle both Enum and int (Pydantic use_enum_values case)
        trust_val = self.card.trust_level if isinstance(self.card.trust_level, int) else self.card.trust_level.value
        if risk_level > trust_val:
            return False, f"Trust Violation: Tool '{tool_name}' (Risk {risk_level}) exceeds Agent Trust Level ({trust_val})."

        # 4. Contextual Argument Scan (L1 Sanitization Integration)
        # Note: Phase 170 Sanitizer already runs at Gateway, but we can add agent-specific rules here.
        if tool_name == "run_command":
            cmd = str(arguments.get("CommandLine", ""))
            if any(forbidden in cmd for forbidden in ["rm -rf", "format", "mkfs"]):
                 return False, "Sandbox Violation: Destructive shell command detected."

        return True, "Authorized"

    def wrap_tool_node(self, tool_node_func):
        """
        Higher-order function to wrap a LangGraph ToolNode with sandbox protection.
        """
        def protected_node(state):
            # Logic to extract last tool call and validate
            # (Simplified for Wave 1 framework setup)
            return tool_node_func(state)
        return protected_node
