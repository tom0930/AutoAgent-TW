"""
AI Harness Core Package
所有 AI Harness 核心模組
版本：v1.0.0
"""

# ── Phase 1 ──────────────────────────────────────────────────────────────────
from .harness_gateway import HarnessGateway, ServiceStatus
from .session_manager import SessionManager, Session, SessionKind, SessionStatus

# ── Phase 2 ──────────────────────────────────────────────────────────────────
from .skill.engine import SkillEngine, Skill, SkillMetadata, SkillResult, TriggerMatch
from .plugin.loader import PluginLoader, PluginManifest, PluginSandbox
from .mcp.hub import MCPHub, MCPTool, MCPToolCall, MCPToolResult, MCPTransport
from .cron.scheduler import CronScheduler, CronJob, JobRun, JobKind, JobStatus
from .node.pairing import NodePairing, DevicePairing, DeviceType, PairingStatus

# ── Phase 3 ──────────────────────────────────────────────────────────────────
from .orchestration.coordinator import OrchestrationCoordinator
from .orchestration.spawn_manager import AgentProcess

# ── Hybrid Palace Memory ─────────────────────────────────────────────────────
from .memory import (
    WorkingMemory,
    WorkingMemoryConfig,
    FlushEvent,
    # Palace Index
    PalaceIndex,
    PalaceConfig,
    Wing,
    Room,
    Drawer,
    WingType,
    SearchResult,
    # Knowledge Graph
    KnowledgeGraph,
    KGConfig,
    Entity,
    Relation,
    EntityType,
    RelationType,
    ValidityWindow,
    EntityQuery,
    RelationQuery,
    # Reranking
    Reranker,
    RerankConfig,
    RerankResult,
    BM25,
    TemporalScorer,
    KGBooster,
    rerank_search_results,
    # Compression
    TokenCompressor,
    CompressionConfig,
    CompressionResult,
    TokenEstimator,
    StructureParser,
    compress_content,
    estimate_tokens,
)

__version__ = "1.0.0"

__all__ = [
    # Phase 1
    "HarnessGateway",
    "ServiceStatus",
    "SessionManager",
    "Session",
    "SessionKind",
    "SessionStatus",
    # Phase 2
    "SkillEngine",
    "Skill",
    "SkillMetadata",
    "SkillResult",
    "TriggerMatch",
    "PluginLoader",
    "PluginManifest",
    "PluginSandbox",
    "MCPHub",
    "MCPTool",
    "MCPToolCall",
    "MCPToolResult",
    "MCPTransport",
    "CronScheduler",
    "CronJob",
    "JobRun",
    "JobKind",
    "JobStatus",
    "NodePairing",
    "DevicePairing",
    "DeviceType",
    "PairingStatus",
    # Phase 3
    "OrchestrationCoordinator",
    "AgentProcess",
    # Hybrid Palace Memory
    "WorkingMemory",
    "WorkingMemoryConfig",
    "FlushEvent",
    # Palace Index
    "PalaceIndex",
    "PalaceConfig",
    "Wing",
    "Room",
    "Drawer",
    "WingType",
    "SearchResult",
    # Knowledge Graph
    "KnowledgeGraph",
    "KGConfig",
    "Entity",
    "Relation",
    "EntityType",
    "RelationType",
    "ValidityWindow",
    "EntityQuery",
    "RelationQuery",
    # Reranking
    "Reranker",
    "RerankConfig",
    "RerankResult",
    "BM25",
    "TemporalScorer",
    "KGBooster",
    "rerank_search_results",
    # Compression
    "TokenCompressor",
    "CompressionConfig",
    "CompressionResult",
    "TokenEstimator",
    "StructureParser",
    "compress_content",
    "estimate_tokens",
]
