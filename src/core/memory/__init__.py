"""
Memory Module - Hybrid Palace Architecture

Layer 1: Working Memory (OpenClaw-style)
- Markdown-based short-term memory
- Auto Flush mechanism

Layer 2: Palace Index (MemPalace-style) - Planned
- Wings/Rooms/Drawers structure
- Knowledge Graph

Layer 3: Reranking Pipeline - Planned
- Hybrid Search + Temporal + KG Boost
- Token Compression
"""

from .working import (
    WorkingMemory,
    WorkingMemoryConfig,
    FlushEvent,
    TRIGGER_THRESHOLD,
    FLUSH_TARGET,
)

__all__ = [
    "WorkingMemory",
    "WorkingMemoryConfig", 
    "FlushEvent",
    "TRIGGER_THRESHOLD",
    "FLUSH_TARGET",
]
