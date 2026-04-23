"""
Knowledge Graph - Temporal Entity-Relationship Graph for Memory.

Implements a temporal ER graph with validity windows for tracking
relationships between entities over time.

Architecture:
    Entity (Node) — Objects, concepts, people, projects
    └── Property: Key-value attributes
    Relation (Edge) — Typed relationships with validity windows
    └── ValidityWindow: Time range [valid_from, valid_to]

Features:
- Temporal queries (what was true at time T?)
- Entity resolution (merge duplicates)
- Relation inference (transitive, symmetric)
- Validity tracking (past, current, future)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = [
    "KnowledgeGraph",
    "Entity",
    "Relation",
    "EntityType",
    "RelationType",
    "ValidityWindow",
    "KGConfig",
    "EntityQuery",
    "RelationQuery",
]


class EntityType(Enum):
    """Entity type classification."""

    PROJECT = "project"  # Software projects
    PERSON = "person"  # People
    CONCEPT = "concept"  # Abstract concepts
    HARDWARE = "hardware"  # Physical hardware
    PROTOCOL = "protocol"  # Communication protocols
    FILE = "file"  # Files and documents
    EVENT = "event"  # Events and milestones
    ORGANIZATION = "organization"  # Companies, teams
    LOCATION = "location"  # Physical locations


class RelationType(Enum):
    """Relation type classification."""

    # Hierarchical
    PART_OF = "part_of"  # A is part of B
    CONTAINS = "contains"  # A contains B (inverse of PART_OF)
    PARENT_OF = "parent_of"  # A is parent of B
    CHILD_OF = "child_of"  # A is child of B

    # Associative
    RELATED_TO = "related_to"  # Generic relation
    DEPENDS_ON = "depends_on"  # A depends on B
    REFERENCES = "references"  # A references B
    IMPLEMENTS = "implements"  # A implements B

    # Temporal
    PRECEDES = "precedes"  # A precedes B in time
    FOLLOWS = "follows"  # A follows B in time
    TRANSFORMS_TO = "transforms_to"  # A transforms to B

    # Attribution
    OWNED_BY = "owned_by"  # A is owned by B
    CREATED_BY = "created_by"  # A is created by B
    LOCATED_AT = "located_at"  # A is located at B

    @property
    def inverse(self) -> "RelationType":
        """Get the inverse relation type."""
        inverses = {
            RelationType.PART_OF: RelationType.CONTAINS,
            RelationType.CONTAINS: RelationType.PART_OF,
            RelationType.PARENT_OF: RelationType.CHILD_OF,
            RelationType.CHILD_OF: RelationType.PARENT_OF,
            RelationType.PRECEDES: RelationType.FOLLOWS,
            RelationType.FOLLOWS: RelationType.PRECEDES,
            RelationType.TRANSFORMS_TO: RelationType.FOLLOWS,  # Approximate
        }
        return inverses.get(self, self)


@dataclass
class ValidityWindow:
    """
    Time range for relation validity.

    Represents when a relation was/is/will be true.
    None means unbounded (open-ended).
    """

    valid_from: Optional[datetime] = None  # When relation becomes valid
    valid_to: Optional[datetime] = None  # When relation becomes invalid

    def is_valid_at(self, at_time: datetime) -> bool:
        """Check if relation is valid at a specific time."""
        if self.valid_from and at_time < self.valid_from:
            return False
        if self.valid_to and at_time > self.valid_to:
            return False
        return True

    def is_current(self) -> bool:
        """Check if relation is currently valid."""
        return self.is_valid_at(datetime.now())

    def is_past(self) -> bool:
        """Check if relation is in the past."""
        if self.valid_to:
            return datetime.now() > self.valid_to
        return False

    def is_future(self) -> bool:
        """Check if relation is in the future."""
        if self.valid_from:
            return datetime.now() < self.valid_from
        return False

    def overlaps(self, other: "ValidityWindow") -> bool:
        """Check if two validity windows overlap."""
        # Both open-ended
        if not self.valid_from and not self.valid_to:
            return True
        if not other.valid_from and not other.valid_to:
            return True

        # Check overlap
        start1 = self.valid_from or datetime.min
        end1 = self.valid_to or datetime.max
        start2 = other.valid_from or datetime.min
        end2 = other.valid_to or datetime.max

        return start1 <= end2 and start2 <= end1

    def to_dict(self) -> dict[str, Optional[str]]:
        """Serialize to dictionary."""
        return {
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidityWindow":
        """Deserialize from dictionary."""
        return cls(
            valid_from=datetime.fromisoformat(data["valid_from"]) if data.get("valid_from") else None,
            valid_to=datetime.fromisoformat(data["valid_to"]) if data.get("valid_to") else None,
        )


@dataclass
class Entity:
    """
    Entity node in the knowledge graph.

    Represents an object, concept, person, project, etc.
    """

    id: str  # Unique identifier
    entity_type: EntityType
    name: str
    description: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        entity_type: EntityType,
        name: str,
        description: str = "",
        properties: Optional[dict[str, Any]] = None,
    ) -> "Entity":
        """Create a new entity with auto-generated ID."""
        now = datetime.now()
        import hashlib
        name_hash = hashlib.sha256(f"{entity_type.value}:{name}:{now.isoformat()}".encode()).hexdigest()[:12]
        return cls(
            id=f"entity_{name_hash}",
            entity_type=entity_type,
            name=name,
            description=description,
            properties=properties or {},
            created_at=now,
            updated_at=now,
        )

    def set_property(self, key: str, value: Any) -> None:
        """Set a property on the entity."""
        self.properties[key] = value
        self.updated_at = datetime.now()

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property from the entity."""
        return self.properties.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entity":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            description=data.get("description", ""),
            properties=data.get("properties", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class Relation:
    """
    Relation edge in the knowledge graph.

    Represents a typed relationship between two entities
    with optional validity window.
    """

    id: str  # Unique identifier
    source_id: str  # Source entity ID
    target_id: str  # Target entity ID
    relation_type: RelationType
    validity: ValidityWindow = field(default_factory=ValidityWindow)
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0  # Confidence score (0.0 - 1.0)

    @classmethod
    def create(
        cls,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        validity: Optional[ValidityWindow] = None,
        properties: Optional[dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> "Relation":
        """Create a new relation with auto-generated ID."""
        now = datetime.now()
        import hashlib
        rel_hash = hashlib.sha256(
            f"{source_id}:{relation_type.value}:{target_id}:{now.isoformat()}".encode()
        ).hexdigest()[:12]
        return cls(
            id=f"rel_{rel_hash}",
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            validity=validity or ValidityWindow(),
            properties=properties or {},
            created_at=now,
            confidence=confidence,
        )

    def is_valid_at(self, at_time: datetime) -> bool:
        """Check if relation is valid at a specific time."""
        return self.validity.is_valid_at(at_time)

    def is_current(self) -> bool:
        """Check if relation is currently valid."""
        return self.validity.is_current()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "validity": self.validity.to_dict(),
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relation":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=RelationType(data["relation_type"]),
            validity=ValidityWindow.from_dict(data.get("validity", {})),
            properties=data.get("properties", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            confidence=data.get("confidence", 1.0),
        )


@dataclass
class EntityQuery:
    """Query for searching entities."""

    entity_type: Optional[EntityType] = None
    name_contains: Optional[str] = None
    property_filters: dict[str, Any] = field(default_factory=dict)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = 100


@dataclass
class RelationQuery:
    """Query for searching relations."""

    relation_type: Optional[RelationType] = None
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    valid_at: Optional[datetime] = None
    min_confidence: float = 0.0
    limit: int = 100


@dataclass
class KGConfig:
    """Configuration for Knowledge Graph."""

    storage_path: Path = field(default_factory=lambda: Path(".kg"))
    auto_infer: bool = True  # Auto-infer inverse relations


class KnowledgeGraph:
    """
    Knowledge Graph - Temporal ER Graph for Memory.

    Manages entities and relations with temporal validity tracking.
    """

    def __init__(self, config: KGConfig) -> None:
        self.config = config
        self.entities: dict[str, Entity] = {}
        self.relations: dict[str, Relation] = {}
        self._index_path = config.storage_path / "kg_index.json"
        self._initialized = False

        # Indexes for fast lookup
        self._entity_by_type: dict[EntityType, set[str]] = {}
        self._relation_by_source: dict[str, set[str]] = {}
        self._relation_by_target: dict[str, set[str]] = {}

    def initialize(self) -> None:
        """Initialize knowledge graph, loading from disk if exists."""
        if self._initialized:
            return

        if self._index_path.exists():
            self._load_from_disk()

        self._initialized = True

    def _load_from_disk(self) -> None:
        """Load knowledge graph from disk."""
        with open(self._index_path, encoding="utf-8") as f:
            data = json.load(f)

        self.entities = {k: Entity.from_dict(v) for k, v in data.get("entities", {}).items()}
        self.relations = {k: Relation.from_dict(v) for k, v in data.get("relations", {}).items()}

        # Rebuild indexes
        self._rebuild_indexes()

    def _save_to_disk(self) -> None:
        """Save knowledge graph to disk."""
        self.config.storage_path.mkdir(parents=True, exist_ok=True)
        data = {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relations": {k: v.to_dict() for k, v in self.relations.items()},
            "updated_at": datetime.now().isoformat(),
        }
        with open(self._index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes."""
        # Entity by type
        self._entity_by_type.clear()
        for entity_id, entity in self.entities.items():
            if entity.entity_type not in self._entity_by_type:
                self._entity_by_type[entity.entity_type] = set()
            self._entity_by_type[entity.entity_type].add(entity_id)

        # Relation by source/target
        self._relation_by_source.clear()
        self._relation_by_target.clear()
        for relation_id, relation in self.relations.items():
            if relation.source_id not in self._relation_by_source:
                self._relation_by_source[relation.source_id] = set()
            self._relation_by_source[relation.source_id].add(relation_id)

            if relation.target_id not in self._relation_by_target:
                self._relation_by_target[relation.target_id] = set()
            self._relation_by_target[relation.target_id].add(relation_id)

    # ==================== Entity Operations ====================

    def add_entity(
        self,
        entity_type: EntityType,
        name: str,
        description: str = "",
        properties: Optional[dict[str, Any]] = None,
    ) -> Entity:
        """Add a new entity to the graph."""
        entity = Entity.create(entity_type, name, description, properties)
        self.entities[entity.id] = entity

        # Update index
        if entity_type not in self._entity_by_type:
            self._entity_by_type[entity_type] = set()
        self._entity_by_type[entity_type].add(entity.id)

        self._save_to_disk()
        return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)

    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Get an entity by name."""
        for entity in self.entities.values():
            if entity.name == name:
                return entity
        return None

    def update_entity(
        self,
        entity_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        properties: Optional[dict[str, Any]] = None,
    ) -> Optional[Entity]:
        """Update an entity."""
        entity = self.entities.get(entity_id)
        if not entity:
            return None

        if name is not None:
            entity.name = name
        if description is not None:
            entity.description = description
        if properties is not None:
            entity.properties.update(properties)

        entity.updated_at = datetime.now()
        self._save_to_disk()
        return entity

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and all its relations."""
        if entity_id not in self.entities:
            return False

        # Remove all relations involving this entity
        relations_to_delete = [
            rid for rid, r in self.relations.items()
            if r.source_id == entity_id or r.target_id == entity_id
        ]
        for rid in relations_to_delete:
            self._remove_relation_index(rid)
            del self.relations[rid]

        # Remove entity
        entity = self.entities[entity_id]
        self._entity_by_type[entity.entity_type].discard(entity_id)
        del self.entities[entity_id]

        self._save_to_disk()
        return True

    def query_entities(self, query: EntityQuery) -> list[Entity]:
        """Query entities based on criteria."""
        results: list[Entity] = []

        for entity in self.entities.values():
            # Type filter
            if query.entity_type and entity.entity_type != query.entity_type:
                continue

            # Name filter
            if query.name_contains and query.name_contains.lower() not in entity.name.lower():
                continue

            # Property filters
            match = True
            for key, value in query.property_filters.items():
                if entity.get_property(key) != value:
                    match = False
                    break
            if not match:
                continue

            # Date filters
            if query.created_after and entity.created_at < query.created_after:
                continue
            if query.created_before and entity.created_at > query.created_before:
                continue

            results.append(entity)

        return results[:query.limit]

    # ==================== Relation Operations ====================

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        validity: Optional[ValidityWindow] = None,
        properties: Optional[dict[str, Any]] = None,
        confidence: float = 1.0,
        infer_inverse: bool = True,
    ) -> Optional[Relation]:
        """Add a relation between two entities."""
        # Verify entities exist
        if source_id not in self.entities or target_id not in self.entities:
            return None

        relation = Relation.create(
            source_id, target_id, relation_type, validity, properties, confidence
        )
        self.relations[relation.id] = relation

        # Update indexes
        if source_id not in self._relation_by_source:
            self._relation_by_source[source_id] = set()
        self._relation_by_source[source_id].add(relation.id)

        if target_id not in self._relation_by_target:
            self._relation_by_target[target_id] = set()
        self._relation_by_target[target_id].add(relation.id)

        # Infer inverse relation if configured
        if infer_inverse and self.config.auto_infer:
            inverse_type = relation_type.inverse
            if inverse_type != relation_type:  # Avoid self-inverse
                self.add_relation(
                    target_id, source_id, inverse_type,
                    validity, properties, confidence,
                    infer_inverse=False,  # Prevent infinite recursion
                )

        self._save_to_disk()
        return relation

    def _remove_relation_index(self, relation_id: str) -> None:
        """Remove relation from indexes."""
        relation = self.relations.get(relation_id)
        if relation:
            self._relation_by_source.get(relation.source_id, set()).discard(relation_id)
            self._relation_by_target.get(relation.target_id, set()).discard(relation_id)

    def get_relation(self, relation_id: str) -> Optional[Relation]:
        """Get a relation by ID."""
        return self.relations.get(relation_id)

    def get_relations_from(self, entity_id: str, valid_at: Optional[datetime] = None) -> list[Relation]:
        """Get all relations from an entity."""
        relation_ids = self._relation_by_source.get(entity_id, set())
        relations = [self.relations[rid] for rid in relation_ids if rid in self.relations]

        if valid_at:
            relations = [r for r in relations if r.is_valid_at(valid_at)]

        return relations

    def get_relations_to(self, entity_id: str, valid_at: Optional[datetime] = None) -> list[Relation]:
        """Get all relations to an entity."""
        relation_ids = self._relation_by_target.get(entity_id, set())
        relations = [self.relations[rid] for rid in relation_ids if rid in self.relations]

        if valid_at:
            relations = [r for r in relations if r.is_valid_at(valid_at)]

        return relations

    def get_related_entities(
        self,
        entity_id: str,
        relation_type: Optional[RelationType] = None,
        valid_at: Optional[datetime] = None,
    ) -> list[Entity]:
        """Get all entities related to an entity."""
        relations = self.get_relations_from(entity_id, valid_at)

        if relation_type:
            relations = [r for r in relations if r.relation_type == relation_type]

        related_ids = {r.target_id for r in relations}
        return [self.entities[eid] for eid in related_ids if eid in self.entities]

    def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        if relation_id not in self.relations:
            return False

        self._remove_relation_index(relation_id)
        del self.relations[relation_id]
        self._save_to_disk()
        return True

    def query_relations(self, query: RelationQuery) -> list[Relation]:
        """Query relations based on criteria."""
        results: list[Relation] = []

        for relation in self.relations.values():
            # Type filter
            if query.relation_type and relation.relation_type != query.relation_type:
                continue

            # Source/target filters
            if query.source_id and relation.source_id != query.source_id:
                continue
            if query.target_id and relation.target_id != query.target_id:
                continue

            # Validity filter
            if query.valid_at and not relation.is_valid_at(query.valid_at):
                continue

            # Confidence filter
            if relation.confidence < query.min_confidence:
                continue

            results.append(relation)

        return results[:query.limit]

    # ==================== Temporal Queries ====================

    def get_entity_state_at(
        self,
        entity_id: str,
        at_time: datetime,
    ) -> dict[str, Any]:
        """
        Get the state of an entity at a specific time.

        Returns entity properties and valid relations at that time.
        """
        entity = self.entities.get(entity_id)
        if not entity:
            return {}

        relations = self.get_relations_from(entity_id, at_time)

        return {
            "entity": entity.to_dict(),
            "relations": [r.to_dict() for r in relations],
            "related_entities": [
                self.entities[r.target_id].to_dict()
                for r in relations
                if r.target_id in self.entities
            ],
        }

    def get_history(self, entity_id: str) -> list[Relation]:
        """
        Get the history of relations for an entity.

        Returns all relations sorted by creation time.
        """
        relations = self.get_relations_from(entity_id) + self.get_relations_to(entity_id)
        relations.sort(key=lambda r: r.created_at)
        return relations

    # ==================== Graph Operations ====================

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3,
    ) -> Optional[list[str]]:
        """
        Find a path between two entities using BFS.

        Returns list of entity IDs representing the path, or None.
        """
        if source_id == target_id:
            return [source_id]

        visited: set[str] = {source_id}
        queue: list[tuple[str, list[str]]] = [(source_id, [source_id])]

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            related = self.get_related_entities(current)
            for entity in related:
                if entity.id in visited:
                    continue

                new_path = path + [entity.id]
                if entity.id == target_id:
                    return new_path

                visited.add(entity.id)
                queue.append((entity.id, new_path))

        return None

    # ==================== Stats ====================

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge graph statistics."""
        current_relations = sum(1 for r in self.relations.values() if r.is_current())
        past_relations = sum(1 for r in self.relations.values() if r.validity.is_past())

        return {
            "entities": len(self.entities),
            "relations": len(self.relations),
            "current_relations": current_relations,
            "past_relations": past_relations,
            "entity_types": {
                et.value: len(self._entity_by_type.get(et, set()))
                for et in EntityType
            },
        }

    def close(self) -> None:
        """Close knowledge graph and save to disk."""
        self._save_to_disk()
        self._initialized = False
