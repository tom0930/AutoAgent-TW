"""
Palace Index - MemPalace-style hierarchical memory structure.

Implements Wings > Rooms > Drawers metaphor for organizing
long-term verbatim storage with ChromaDB backend.

Architecture:
    Wing (Project/Domain)
    └── Room (Topic/Area)
        └── Drawer (Entry/Document)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = [
    "PalaceIndex",
    "Wing",
    "Room",
    "Drawer",
    "PalaceConfig",
    "WingType",
    "SearchResult",
]


class WingType(Enum):
    """Wing classification types."""

    PROJECT = "project"  # Software projects (AutoAgent-TW, VMatIrrKitPacking)
    DOMAIN = "domain"  # Knowledge domains (hardware, protocols)
    AGENT = "agent"  # Agent-specific memory (agent diaries)
    SYSTEM = "system"  # System-level memory (config, logs)


@dataclass
class Drawer:
    """
    Individual memory entry - the atomic unit of storage.

    Stores verbatim content with metadata. No summarization.
    """

    id: str  # Unique identifier (hash-based)
    room_id: str  # Parent room ID
    content: str  # Verbatim content (never summarized)
    created_at: datetime
    updated_at: datetime
    embedding: Optional[list[float]] = None  # Local embedding vector
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        room_id: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Drawer":
        """Create a new drawer with auto-generated ID."""
        now = datetime.now()
        content_hash = hashlib.sha256(
            f"{room_id}:{content}:{now.isoformat()}".encode()
        ).hexdigest()[:16]
        return cls(
            id=f"drawer_{content_hash}",
            room_id=room_id,
            content=content,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

    def update(self, new_content: str) -> None:
        """Update drawer content (verbatim, no summarization)."""
        self.content = new_content
        self.updated_at = datetime.now()
        self.embedding = None  # Invalidate embedding

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "embedding": self.embedding,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Drawer":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            room_id=data["room_id"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Room:
    """
    Topic/area container within a wing.

    Groups related drawers by topic.
    """

    id: str  # Unique identifier
    wing_id: str  # Parent wing ID
    name: str  # Room name (topic)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    drawers: dict[str, Drawer] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        wing_id: str,
        name: str,
        description: str = "",
    ) -> "Room":
        """Create a new room with auto-generated ID."""
        now = datetime.now()
        name_hash = hashlib.sha256(f"{wing_id}:{name}:{now.isoformat()}".encode()).hexdigest()[:12]
        return cls(
            id=f"room_{name_hash}",
            wing_id=wing_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
        )

    def add_drawer(self, drawer: Drawer) -> None:
        """Add a drawer to this room."""
        self.drawers[drawer.id] = drawer
        self.updated_at = datetime.now()

    def get_drawer(self, drawer_id: str) -> Optional[Drawer]:
        """Get a drawer by ID."""
        return self.drawers.get(drawer_id)

    def remove_drawer(self, drawer_id: str) -> bool:
        """Remove a drawer from this room."""
        if drawer_id in self.drawers:
            del self.drawers[drawer_id]
            self.updated_at = datetime.now()
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "wing_id": self.wing_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "drawers": {k: v.to_dict() for k, v in self.drawers.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Room":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            wing_id=data["wing_id"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            drawers={k: Drawer.from_dict(v) for k, v in data.get("drawers", {}).items()},
        )


@dataclass
class Wing:
    """
    Top-level project/domain container.

    Represents a major project or knowledge domain.
    """

    id: str  # Unique identifier
    name: str  # Wing name (project/domain)
    wing_type: WingType
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    rooms: dict[str, Room] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        wing_type: WingType,
        description: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Wing":
        """Create a new wing with auto-generated ID."""
        now = datetime.now()
        name_hash = hashlib.sha256(f"{name}:{wing_type.value}:{now.isoformat()}".encode()).hexdigest()[:10]
        return cls(
            id=f"wing_{name_hash}",
            name=name,
            wing_type=wing_type,
            description=description,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

    def add_room(self, room: Room) -> None:
        """Add a room to this wing."""
        self.rooms[room.id] = room
        self.updated_at = datetime.now()

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        return self.rooms.get(room_id)

    def get_room_by_name(self, name: str) -> Optional[Room]:
        """Get a room by name."""
        for room in self.rooms.values():
            if room.name == name:
                return room
        return None

    def remove_room(self, room_id: str) -> bool:
        """Remove a room from this wing."""
        if room_id in self.rooms:
            del self.rooms[room_id]
            self.updated_at = datetime.now()
            return True
        return False

    def list_rooms(self) -> list[Room]:
        """List all rooms in this wing."""
        return list(self.rooms.values())

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "wing_type": self.wing_type.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "rooms": {k: v.to_dict() for k, v in self.rooms.items()},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Wing":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            wing_type=WingType(data["wing_type"]),
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            rooms={k: Room.from_dict(v) for k, v in data.get("rooms", {}).items()},
            metadata=data.get("metadata", {}),
        )


@dataclass
class SearchResult:
    """Search result from palace index."""

    drawer: Drawer
    room: Room
    wing: Wing
    score: float  # Relevance score (0.0 - 1.0)
    distance: float  # Vector distance (lower = more similar)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "drawer_id": self.drawer.id,
            "room_id": self.room.id,
            "wing_id": self.wing.id,
            "content": self.drawer.content,
            "score": self.score,
            "distance": self.distance,
            "wing_name": self.wing.name,
            "room_name": self.room.name,
        }


@dataclass
class PalaceConfig:
    """Configuration for Palace Index."""

    storage_path: Path = field(default_factory=lambda: Path(".palace"))
    embedding_model: str = "local"  # "local" for local embeddings
    max_drawers_per_room: int = 1000
    auto_index: bool = True  # Auto-index on add


class PalaceIndex:
    """
    Main palace index - manages wings, rooms, and drawers.

    Provides hierarchical storage with ChromaDB backend for
    vector similarity search.
    """

    def __init__(self, config: PalaceConfig) -> None:
        self.config = config
        self.wings: dict[str, Wing] = {}
        self._index_path = config.storage_path / "palace_index.json"
        self._initialized = False

        # ChromaDB client (lazy load)
        self._chroma_client: Any = None
        self._collection: Any = None

    def initialize(self) -> None:
        """Initialize palace index, loading from disk if exists."""
        if self._initialized:
            return

        # Load from disk if exists
        if self._index_path.exists():
            self._load_from_disk()

        # Initialize ChromaDB backend
        self._init_chroma()

        self._initialized = True

    def _init_chroma(self) -> None:
        """Initialize ChromaDB backend for vector storage."""
        try:
            import chromadb  # type: ignore

            self._chroma_client = chromadb.PersistentClient(
                path=str(self.config.storage_path / "chromadb")
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name="palace_embeddings",
                metadata={"hnsw:space": "cosine"},
            )
        except ImportError:
            # ChromaDB not installed - fallback to file-only mode
            self._chroma_client = None
            self._collection = None

    def _load_from_disk(self) -> None:
        """Load palace index from disk."""
        with open(self._index_path, encoding="utf-8") as f:
            data = json.load(f)
        self.wings = {k: Wing.from_dict(v) for k, v in data.get("wings", {}).items()}

    def _save_to_disk(self) -> None:
        """Save palace index to disk."""
        self.config.storage_path.mkdir(parents=True, exist_ok=True)
        data = {
            "wings": {k: v.to_dict() for k, v in self.wings.items()},
            "updated_at": datetime.now().isoformat(),
        }
        with open(self._index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ==================== Wing Operations ====================

    def create_wing(
        self,
        name: str,
        wing_type: WingType,
        description: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> Wing:
        """Create a new wing."""
        wing = Wing.create(name, wing_type, description, metadata)
        self.wings[wing.id] = wing
        self._save_to_disk()
        return wing

    def get_wing(self, wing_id: str) -> Optional[Wing]:
        """Get a wing by ID."""
        return self.wings.get(wing_id)

    def get_wing_by_name(self, name: str) -> Optional[Wing]:
        """Get a wing by name."""
        for wing in self.wings.values():
            if wing.name == name:
                return wing
        return None

    def list_wings(self, wing_type: Optional[WingType] = None) -> list[Wing]:
        """List all wings, optionally filtered by type."""
        wings = list(self.wings.values())
        if wing_type:
            wings = [w for w in wings if w.wing_type == wing_type]
        return wings

    def delete_wing(self, wing_id: str) -> bool:
        """Delete a wing and all its rooms/drawers."""
        if wing_id not in self.wings:
            return False

        wing = self.wings[wing_id]

        # Remove from ChromaDB
        if self._collection:
            drawer_ids = []
            for room in wing.rooms.values():
                drawer_ids.extend(room.drawers.keys())
            if drawer_ids:
                self._collection.delete(ids=drawer_ids)

        del self.wings[wing_id]
        self._save_to_disk()
        return True

    # ==================== Room Operations ====================

    def create_room(
        self,
        wing_id: str,
        name: str,
        description: str = "",
    ) -> Optional[Room]:
        """Create a new room in a wing."""
        wing = self.get_wing(wing_id)
        if not wing:
            return None

        room = Room.create(wing_id, name, description)
        wing.add_room(room)
        self._save_to_disk()
        return room

    def get_room(self, wing_id: str, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        wing = self.get_wing(wing_id)
        if not wing:
            return None
        return wing.get_room(room_id)

    def list_rooms(self, wing_id: str) -> list[Room]:
        """List all rooms in a wing."""
        wing = self.get_wing(wing_id)
        if not wing:
            return []
        return wing.list_rooms()

    def delete_room(self, wing_id: str, room_id: str) -> bool:
        """Delete a room and all its drawers."""
        wing = self.get_wing(wing_id)
        if not wing:
            return False

        room = wing.get_room(room_id)
        if not room:
            return False

        # Remove from ChromaDB
        if self._collection:
            drawer_ids = list(room.drawers.keys())
            if drawer_ids:
                self._collection.delete(ids=drawer_ids)

        return wing.remove_room(room_id)

    # ==================== Drawer Operations ====================

    def add_drawer(
        self,
        wing_id: str,
        room_id: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Drawer]:
        """Add a drawer (verbatim entry) to a room."""
        room = self.get_room(wing_id, room_id)
        if not room:
            return None

        drawer = Drawer.create(room_id, content, metadata)

        # Generate embedding
        if self._collection and self.config.auto_index:
            self._index_drawer(drawer)

        room.add_drawer(drawer)
        self._save_to_disk()
        return drawer

    def _index_drawer(self, drawer: Drawer) -> None:
        """Index a drawer in ChromaDB."""
        if not self._collection:
            return

        # Use simple local embedding (or external embedding service)
        embedding = self._get_embedding(drawer.content)
        if embedding:
            drawer.embedding = embedding
            self._collection.add(
                ids=[drawer.id],
                embeddings=[embedding],
                documents=[drawer.content],
                metadatas=[{
                    "room_id": drawer.room_id,
                    "created_at": drawer.created_at.isoformat(),
                }],
            )

    def _get_embedding(self, text: str) -> Optional[list[float]]:
        """Get embedding for text (local or external)."""
        # Placeholder for local embedding
        # In production, use sentence-transformers or similar
        if self.config.embedding_model == "local":
            # Simple hash-based pseudo-embedding for demo
            # TODO: Replace with actual local model (sentence-transformers)
            text_hash = hashlib.sha256(text.encode()).digest()
            # Create a 384-dim pseudo-embedding (normalize to unit vector)
            embedding = [float(b) / 255.0 for b in text_hash[:384]]
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]
            return embedding
        return None

    def get_drawer(self, wing_id: str, room_id: str, drawer_id: str) -> Optional[Drawer]:
        """Get a drawer by ID."""
        room = self.get_room(wing_id, room_id)
        if not room:
            return None
        return room.get_drawer(drawer_id)

    def update_drawer(
        self,
        wing_id: str,
        room_id: str,
        drawer_id: str,
        new_content: str,
    ) -> Optional[Drawer]:
        """Update drawer content (verbatim, no summarization)."""
        room = self.get_room(wing_id, room_id)
        if not room:
            return None

        drawer = room.get_drawer(drawer_id)
        if not drawer:
            return None

        drawer.update(new_content)

        # Re-index
        if self._collection:
            self._collection.delete(ids=[drawer_id])
            self._index_drawer(drawer)

        self._save_to_disk()
        return drawer

    def delete_drawer(self, wing_id: str, room_id: str, drawer_id: str) -> bool:
        """Delete a drawer."""
        room = self.get_room(wing_id, room_id)
        if not room:
            return False

        drawer = room.get_drawer(drawer_id)
        if not drawer:
            return False

        # Remove from ChromaDB
        if self._collection:
            self._collection.delete(ids=[drawer_id])

        return room.remove_drawer(drawer_id)

    # ==================== Search Operations ====================

    def search(
        self,
        query: str,
        wing_id: Optional[str] = None,
        room_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search for content using vector similarity.

        Args:
            query: Search query text
            wing_id: Optional wing filter
            room_id: Optional room filter
            limit: Max results to return

        Returns:
            List of SearchResult objects sorted by relevance
        """
        if not self._collection:
            return []

        # Get query embedding
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []

        # Build filter
        where_filter: Optional[dict[str, Any]] = None
        if room_id:
            where_filter = {"room_id": room_id}

        # Search ChromaDB
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter,
            include=["documents", "distances", "metadatas"],
        )

        # Build search results
        search_results: list[SearchResult] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for i, drawer_id in enumerate(ids):
            # Find the drawer
            for wing in self.wings.values():
                if wing_id and wing.id != wing_id:
                    continue
                for room in wing.rooms.values():
                    drawer = room.drawers.get(drawer_id)
                    if drawer:
                        distance = distances[i]
                        score = 1.0 - min(distance, 1.0)  # Convert distance to score
                        search_results.append(SearchResult(
                            drawer=drawer,
                            room=room,
                            wing=wing,
                            score=score,
                            distance=distance,
                        ))
                        break

        return search_results

    def search_by_date(
        self,
        start_date: datetime,
        end_date: datetime,
        wing_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[SearchResult]:
        """
        Search for content by date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            wing_id: Optional wing filter
            limit: Max results to return

        Returns:
            List of SearchResult objects sorted by date
        """
        results: list[SearchResult] = []

        for wing in self.wings.values():
            if wing_id and wing.id != wing_id:
                continue
            for room in wing.rooms.values():
                for drawer in room.drawers.values():
                    if start_date <= drawer.created_at <= end_date:
                        results.append(SearchResult(
                            drawer=drawer,
                            room=room,
                            wing=wing,
                            score=1.0,  # No relevance score for date search
                            distance=0.0,
                        ))

        # Sort by date (newest first)
        results.sort(key=lambda r: r.drawer.created_at, reverse=True)
        return results[:limit]

    # ==================== Stats ====================

    def get_stats(self) -> dict[str, Any]:
        """Get palace statistics."""
        total_rooms = sum(len(w.rooms) for w in self.wings.values())
        total_drawers = sum(
            len(r.drawers) for w in self.wings.values() for r in w.rooms.values()
        )

        return {
            "wings": len(self.wings),
            "rooms": total_rooms,
            "drawers": total_drawers,
            "wing_types": {
                wt.value: sum(1 for w in self.wings.values() if w.wing_type == wt)
                for wt in WingType
            },
        }

    def close(self) -> None:
        """Close palace index and save to disk."""
        self._save_to_disk()
        self._initialized = False
