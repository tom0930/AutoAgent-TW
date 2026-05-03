from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseRenderer(ABC):
    """
    Contract for all Renderers (CLI, Web, IDE) - Phase 171 v2.1.
    Decouples core logic from presentation.
    """
    
    @abstractmethod
    def update_agent_status(self, agent_id: str, status: str, data: Dict[str, Any] = None):
        """Called when an individual agent changes state."""
        pass

    @abstractmethod
    def display_suggestion(self, suggestion: Dict[str, Any]):
        """Renders a proactive AI suggestion with evidence."""
        pass

    @abstractmethod
    def display_squad_metrics(self, squad_id: str, metrics: Dict[str, Any]):
        """Renders high-level squad performance/load."""
        pass

    @abstractmethod
    def notify_crisis(self, message: str, diagnostic_data: Dict[str, Any]):
        """Renders emergency intervention UI."""
        pass
