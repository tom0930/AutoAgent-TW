"""AI Harness Package - 統一 AI Agent 框架 版本：v1.0.0"""
__version__ = "1.0.0"

from .cli import HarnessCLI
from .canvas import CanvasSystem, CanvasNode, CanvasEdge, CanvasSnapshot, NodeStatus, NodeType
from .messages import MessageRouter, Message, MessageResult, MessageChannel, MessagePriority, ChannelAdapter
from .spawner import AgentSpawner, AgentConfig, AgentResult, AgentStatus, AgentRuntime

__all__ = [
    # CLI
    "HarnessCLI",
    # Canvas
    "CanvasSystem", "CanvasNode", "CanvasEdge", "CanvasSnapshot", "NodeStatus", "NodeType",
    # Messages
    "MessageRouter", "Message", "MessageResult", "MessageChannel", "MessagePriority", "ChannelAdapter",
    # Spawner
    "AgentSpawner", "AgentConfig", "AgentResult", "AgentStatus", "AgentRuntime",
]
