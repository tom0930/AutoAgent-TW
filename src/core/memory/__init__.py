"""
Memory Module - Hybrid Palace Architecture

Layer 1: Working Memory (OpenClaw-style)
- Markdown-based short-term memory
- Auto Flush mechanism

Layer 2: Palace Index (MemPalace-style)
- Wings/Rooms/Drawers structure
- Verbatim storage
- ChromaDB backend

Layer 2.5: Knowledge Graph
- Temporal ER diagram
- Validity windows
- Entity resolution

Layer 3: Reranking Pipeline
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

from .palace import (
    PalaceIndex,
    PalaceConfig,
    Wing,
    Room,
    Drawer,
    WingType,
    SearchResult,
)

from .kg import (
    KnowledgeGraph,
    KGConfig,
    Entity,
    Relation,
    EntityType,
    RelationType,
    ValidityWindow,
    EntityQuery,
    RelationQuery,
)

from .rerank import (
    Reranker,
    RerankConfig,
    RerankResult,
    BM25,
    TemporalScorer,
    KGBooster,
    rerank_search_results,
)

from .compress import (
    TokenCompressor,
    CompressionConfig,
    CompressionResult,
    TokenEstimator,
    StructureParser,
    compress_content,
    estimate_tokens,
)

__all__ = [
    # Working Memory
    "WorkingMemory",
    "WorkingMemoryConfig",
    "FlushEvent",
    "TRIGGER_THRESHOLD",
    "FLUSH_TARGET",
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
