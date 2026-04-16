from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class ToolRisk:
    name: str
    risk_level: int # 1 (Read) to 5 (Fatal)
    description: str

class PermissionEngine:
    """
    IRA 5-Level Tool Permission Guard (Phase 120 - Task 2.1).
    Maps tools to risk levels and evaluates interrupt criteria.
    """
    def __init__(self):
        # Initial registry (Mocks as per Wave 4 requirements)
        self.registry: Dict[str, ToolRisk] = {
            "delete_database": ToolRisk("delete_database", 5, "Destructive DB operations"),
            "delete_config": ToolRisk("delete_config", 5, "Global config deletion"),
            "send_external_email": ToolRisk("send_external_email", 4, "External communication"),
            "high_cost_api": ToolRisk("high_cost_api", 4, "High credit consumption"),
            "read_sensitive_data": ToolRisk("read_sensitive_data", 3, "Internal customer records"),
            "web_search": ToolRisk("web_search", 2, "General information retrieval"),
            "get_time": ToolRisk("get_time", 1, "System read-only status"),
            "local_rag_read": ToolRisk("local_rag_read", 1, "Local vector database read")
        }

    def get_risk_level(self, tool_name: str) -> int:
        risk_obj = self.registry.get(tool_name)
        return risk_obj.risk_level if risk_obj else 3 # Default to Medium if unknown

    def should_interrupt(self, tool_name: str, is_trusted_user: bool = False) -> Tuple[bool, str]:
        """
        Decision logic:
        (Risk >= 4) OR (Risk == 3 AND !User.Trusted) -> trigger_interrupt()
        """
        risk = self.get_risk_level(tool_name)
        
        if risk >= 4:
            return True, f"Interrupt: Tool '{tool_name}' has fatal/high risk level ({risk})."
        
        if risk == 3 and not is_trusted_user:
            return True, f"Interrupt: Tool '{tool_name}' (Risk 3) requires trusted user privileges."
            
        return False, "Auto-execution permitted."

if __name__ == "__main__":
    engine = PermissionEngine()
    print("Testing Permission Guard Logic...")
    
    # Test cases
    cases = [
        ("delete_database", True),  # Risk 5 -> Interrupt
        ("get_time", True),        # Risk 1 -> Pass
        ("read_sensitive_data", False), # Risk 3, Untrusted -> Interrupt
        ("read_sensitive_data", True)  # Risk 3, Trusted -> Pass
    ]
    
    for tool, trusted in cases:
        interrupt, reason = engine.should_interrupt(tool, trusted)
        print(f"Tool: {tool:20} | Trusted: {str(trusted):5} | Interrupt: {str(interrupt):5} | Reason: {reason}")
