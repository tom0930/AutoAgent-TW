"""
Tests for Knowledge Graph module.

Tests the temporal ER graph with validity windows.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.core.memory.kg import (
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


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory."""
    import shutil
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    # Cleanup with error handling for Windows file locks
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass  # Windows file locks


@pytest.fixture
def kg(temp_storage):
    """Create a KnowledgeGraph with temporary storage."""
    config = KGConfig(storage_path=temp_storage)
    graph = KnowledgeGraph(config)
    graph.initialize()
    yield graph


class TestValidityWindow:
    """Tests for ValidityWindow class."""

    def test_open_ended_validity(self):
        """Test open-ended validity (no bounds)."""
        window = ValidityWindow()
        
        assert window.is_valid_at(datetime.now())
        assert window.is_current()

    def test_past_validity(self):
        """Test past validity."""
        window = ValidityWindow(
            valid_from=datetime.now() - timedelta(days=2),
            valid_to=datetime.now() - timedelta(days=1),
        )
        
        assert window.is_past()
        assert not window.is_current()

    def test_future_validity(self):
        """Test future validity."""
        window = ValidityWindow(
            valid_from=datetime.now() + timedelta(days=1),
            valid_to=datetime.now() + timedelta(days=2),
        )
        
        assert window.is_future()
        assert not window.is_current()

    def test_current_validity(self):
        """Test current validity."""
        window = ValidityWindow(
            valid_from=datetime.now() - timedelta(days=1),
            valid_to=datetime.now() + timedelta(days=1),
        )
        
        assert window.is_current()
        assert not window.is_past()
        assert not window.is_future()

    def test_valid_at_specific_time(self):
        """Test validity at specific time."""
        target_time = datetime(2026, 1, 15, 12, 0, 0)
        window = ValidityWindow(
            valid_from=datetime(2026, 1, 1),
            valid_to=datetime(2026, 2, 1),
        )
        
        assert window.is_valid_at(target_time)
        assert not window.is_valid_at(datetime(2026, 3, 1))

    def test_overlapping_windows(self):
        """Test overlapping validity windows."""
        window1 = ValidityWindow(
            valid_from=datetime(2026, 1, 1),
            valid_to=datetime(2026, 1, 15),
        )
        window2 = ValidityWindow(
            valid_from=datetime(2026, 1, 10),
            valid_to=datetime(2026, 1, 20),
        )
        
        assert window1.overlaps(window2)
        assert window2.overlaps(window1)

    def test_non_overlapping_windows(self):
        """Test non-overlapping validity windows."""
        window1 = ValidityWindow(
            valid_from=datetime(2026, 1, 1),
            valid_to=datetime(2026, 1, 10),
        )
        window2 = ValidityWindow(
            valid_from=datetime(2026, 1, 15),
            valid_to=datetime(2026, 1, 20),
        )
        
        assert not window1.overlaps(window2)

    def test_serialization(self):
        """Test validity window serialization."""
        window = ValidityWindow(
            valid_from=datetime(2026, 1, 1),
            valid_to=datetime(2026, 2, 1),
        )
        
        data = window.to_dict()
        restored = ValidityWindow.from_dict(data)
        
        assert restored.valid_from == window.valid_from
        assert restored.valid_to == window.valid_to


class TestEntity:
    """Tests for Entity class."""

    def test_create_entity(self):
        """Test entity creation."""
        entity = Entity.create(EntityType.PROJECT, "AutoAgent-TW", "AI Framework")
        
        assert entity.id.startswith("entity_")
        assert entity.entity_type == EntityType.PROJECT
        assert entity.name == "AutoAgent-TW"
        assert entity.description == "AI Framework"

    def test_entity_properties(self):
        """Test entity property operations."""
        entity = Entity.create(EntityType.PERSON, "Alice")
        
        entity.set_property("email", "alice@example.com")
        entity.set_property("role", "developer")
        
        assert entity.get_property("email") == "alice@example.com"
        assert entity.get_property("role") == "developer"
        assert entity.get_property("nonexistent", "default") == "default"

    def test_entity_serialization(self):
        """Test entity serialization."""
        entity = Entity.create(EntityType.PROJECT, "Test", properties={"key": "value"})
        entity.set_property("extra", "data")
        
        data = entity.to_dict()
        restored = Entity.from_dict(data)
        
        assert restored.id == entity.id
        assert restored.name == entity.name
        assert restored.properties == entity.properties


class TestRelation:
    """Tests for Relation class."""

    def test_create_relation(self):
        """Test relation creation."""
        relation = Relation.create(
            "entity_1", "entity_2",
            RelationType.DEPENDS_ON,
        )
        
        assert relation.id.startswith("rel_")
        assert relation.source_id == "entity_1"
        assert relation.target_id == "entity_2"
        assert relation.relation_type == RelationType.DEPENDS_ON

    def test_relation_with_validity(self):
        """Test relation with validity window."""
        validity = ValidityWindow(
            valid_from=datetime.now() - timedelta(days=1),
            valid_to=datetime.now() + timedelta(days=1),
        )
        relation = Relation.create(
            "entity_1", "entity_2",
            RelationType.PART_OF,
            validity=validity,
        )
        
        assert relation.is_current()
        assert relation.is_valid_at(datetime.now())

    def test_relation_confidence(self):
        """Test relation confidence score."""
        relation = Relation.create(
            "entity_1", "entity_2",
            RelationType.RELATED_TO,
            confidence=0.85,
        )
        
        assert relation.confidence == 0.85

    def test_relation_serialization(self):
        """Test relation serialization."""
        validity = ValidityWindow(valid_from=datetime(2026, 1, 1))
        relation = Relation.create(
            "entity_1", "entity_2",
            RelationType.IMPLEMENTS,
            validity=validity,
            confidence=0.9,
        )
        
        data = relation.to_dict()
        restored = Relation.from_dict(data)
        
        assert restored.id == relation.id
        assert restored.relation_type == relation.relation_type
        assert restored.confidence == relation.confidence


class TestRelationType:
    """Tests for RelationType enum."""

    def test_inverse_part_of(self):
        """Test inverse of PART_OF."""
        assert RelationType.PART_OF.inverse == RelationType.CONTAINS
        assert RelationType.CONTAINS.inverse == RelationType.PART_OF

    def test_inverse_parent_child(self):
        """Test inverse of PARENT_OF."""
        assert RelationType.PARENT_OF.inverse == RelationType.CHILD_OF
        assert RelationType.CHILD_OF.inverse == RelationType.PARENT_OF

    def test_inverse_temporal(self):
        """Test inverse of temporal relations."""
        assert RelationType.PRECEDES.inverse == RelationType.FOLLOWS
        assert RelationType.FOLLOWS.inverse == RelationType.PRECEDES


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph class."""

    def test_add_entity(self, kg):
        """Test adding an entity."""
        entity = kg.add_entity(
            EntityType.PROJECT,
            "AutoAgent-TW",
            "AI Harness Framework",
        )
        
        assert entity.id in kg.entities
        assert entity.name == "AutoAgent-TW"

    def test_get_entity_by_name(self, kg):
        """Test getting entity by name."""
        created = kg.add_entity(EntityType.PROJECT, "AutoAgent-TW")
        
        retrieved = kg.get_entity_by_name("AutoAgent-TW")
        
        assert retrieved == created

    def test_update_entity(self, kg):
        """Test updating an entity."""
        entity = kg.add_entity(EntityType.PROJECT, "Test")
        
        updated = kg.update_entity(
            entity.id,
            name="Updated Name",
            properties={"key": "value"},
        )
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.get_property("key") == "value"

    def test_delete_entity(self, kg):
        """Test deleting an entity."""
        entity = kg.add_entity(EntityType.PROJECT, "Test")
        
        result = kg.delete_entity(entity.id)
        
        assert result is True
        assert entity.id not in kg.entities

    def test_add_relation(self, kg):
        """Test adding a relation."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        
        relation = kg.add_relation(e1.id, e2.id, RelationType.DEPENDS_ON)
        
        assert relation is not None
        assert relation.source_id == e1.id
        assert relation.target_id == e2.id

    def test_add_relation_invalid_entities(self, kg):
        """Test adding relation with invalid entities."""
        relation = kg.add_relation("invalid_1", "invalid_2", RelationType.RELATED_TO)
        
        assert relation is None

    def test_auto_inverse_relation(self, kg):
        """Test automatic inverse relation creation."""
        kg.config.auto_infer = True
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.CONCEPT, "Concept1")
        
        kg.add_relation(e1.id, e2.id, RelationType.PART_OF)
        
        # Should have both original and inverse
        relations_from_e1 = kg.get_relations_from(e1.id)
        relations_from_e2 = kg.get_relations_from(e2.id)
        
        assert len(relations_from_e1) == 1
        assert relations_from_e1[0].relation_type == RelationType.PART_OF
        assert len(relations_from_e2) == 1
        assert relations_from_e2[0].relation_type == RelationType.CONTAINS

    def test_get_related_entities(self, kg):
        """Test getting related entities."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        kg.add_relation(e1.id, e2.id, RelationType.DEPENDS_ON)
        
        related = kg.get_related_entities(e1.id)
        
        assert len(related) == 1
        assert related[0].id == e2.id

    def test_delete_relation(self, kg):
        """Test deleting a relation."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        relation = kg.add_relation(e1.id, e2.id, RelationType.RELATED_TO, infer_inverse=False)
        
        result = kg.delete_relation(relation.id)
        
        assert result is True
        assert relation.id not in kg.relations

    def test_query_entities_by_type(self, kg):
        """Test querying entities by type."""
        kg.add_entity(EntityType.PROJECT, "Project1")
        kg.add_entity(EntityType.PROJECT, "Project2")
        kg.add_entity(EntityType.PERSON, "Person1")
        
        query = EntityQuery(entity_type=EntityType.PROJECT)
        results = kg.query_entities(query)
        
        assert len(results) == 2

    def test_query_entities_by_name(self, kg):
        """Test querying entities by name."""
        kg.add_entity(EntityType.PROJECT, "AutoAgent-TW")
        kg.add_entity(EntityType.PROJECT, "OtherProject")
        
        query = EntityQuery(name_contains="AutoAgent")
        results = kg.query_entities(query)
        
        assert len(results) == 1
        assert results[0].name == "AutoAgent-TW"

    def test_query_relations_by_type(self, kg):
        """Test querying relations by type."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        e3 = kg.add_entity(EntityType.PROJECT, "Project3")
        
        kg.add_relation(e1.id, e2.id, RelationType.DEPENDS_ON, infer_inverse=False)
        kg.add_relation(e2.id, e3.id, RelationType.RELATED_TO, infer_inverse=False)
        
        query = RelationQuery(relation_type=RelationType.DEPENDS_ON)
        results = kg.query_relations(query)
        
        assert len(results) == 1

    def test_query_relations_by_validity(self, kg):
        """Test querying relations by validity time."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        
        # Past relation
        past_validity = ValidityWindow(
            valid_from=datetime.now() - timedelta(days=2),
            valid_to=datetime.now() - timedelta(days=1),
        )
        kg.add_relation(e1.id, e2.id, RelationType.RELATED_TO, past_validity, infer_inverse=False)
        
        # Current relation
        current_validity = ValidityWindow(
            valid_from=datetime.now() - timedelta(hours=1),
            valid_to=datetime.now() + timedelta(hours=1),
        )
        kg.add_relation(e1.id, e2.id, RelationType.DEPENDS_ON, current_validity, infer_inverse=False)
        
        query = RelationQuery(valid_at=datetime.now())
        results = kg.query_relations(query)
        
        assert len(results) == 1
        assert results[0].relation_type == RelationType.DEPENDS_ON

    def test_find_path(self, kg):
        """Test finding path between entities."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        e3 = kg.add_entity(EntityType.PROJECT, "Project3")
        
        kg.add_relation(e1.id, e2.id, RelationType.RELATED_TO, infer_inverse=False)
        kg.add_relation(e2.id, e3.id, RelationType.RELATED_TO, infer_inverse=False)
        
        path = kg.find_path(e1.id, e3.id)
        
        assert path is not None
        assert path == [e1.id, e2.id, e3.id]

    def test_find_path_no_connection(self, kg):
        """Test finding path when no connection exists."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        
        path = kg.find_path(e1.id, e2.id)
        
        assert path is None

    def test_get_entity_state_at(self, kg):
        """Test getting entity state at specific time."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        
        validity = ValidityWindow(
            valid_from=datetime(2026, 1, 1),
            valid_to=datetime(2026, 2, 1),
        )
        kg.add_relation(e1.id, e2.id, RelationType.DEPENDS_ON, validity, infer_inverse=False)
        
        state = kg.get_entity_state_at(e1.id, datetime(2026, 1, 15))
        
        assert "entity" in state
        assert "relations" in state
        assert len(state["relations"]) == 1

    def test_get_history(self, kg):
        """Test getting entity history."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PROJECT, "Project2")
        e3 = kg.add_entity(EntityType.PROJECT, "Project3")
        
        kg.add_relation(e1.id, e2.id, RelationType.RELATED_TO, infer_inverse=False)
        kg.add_relation(e3.id, e1.id, RelationType.DEPENDS_ON, infer_inverse=False)
        
        history = kg.get_history(e1.id)
        
        assert len(history) == 2

    def test_get_stats(self, kg):
        """Test getting knowledge graph statistics."""
        e1 = kg.add_entity(EntityType.PROJECT, "Project1")
        e2 = kg.add_entity(EntityType.PERSON, "Person1")
        kg.add_relation(e1.id, e2.id, RelationType.OWNED_BY, infer_inverse=False)
        
        stats = kg.get_stats()
        
        assert stats["entities"] == 2
        assert stats["relations"] == 1
        assert stats["entity_types"]["project"] == 1
        assert stats["entity_types"]["person"] == 1

    def test_persistence(self, temp_storage):
        """Test that knowledge graph persists to disk."""
        config = KGConfig(storage_path=temp_storage)
        
        # Create and populate
        kg1 = KnowledgeGraph(config)
        kg1.initialize()
        entity = kg1.add_entity(EntityType.PROJECT, "TestProject")
        kg1.close()
        
        # Reopen
        kg2 = KnowledgeGraph(config)
        kg2.initialize()
        
        assert len(kg2.entities) == 1
        assert kg2.get_entity_by_name("TestProject") is not None


class TestEntityType:
    """Tests for EntityType enum."""

    def test_entity_types(self):
        """Test all entity types exist."""
        assert EntityType.PROJECT.value == "project"
        assert EntityType.PERSON.value == "person"
        assert EntityType.CONCEPT.value == "concept"
        assert EntityType.HARDWARE.value == "hardware"
        assert EntityType.PROTOCOL.value == "protocol"
        assert EntityType.FILE.value == "file"
        assert EntityType.EVENT.value == "event"
        assert EntityType.ORGANIZATION.value == "organization"
        assert EntityType.LOCATION.value == "location"
