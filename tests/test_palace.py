"""
Tests for Palace Index module.

Tests the Wings/Rooms/Drawers hierarchical storage structure
with ChromaDB backend.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.core.memory.palace import (
    PalaceIndex,
    PalaceConfig,
    Wing,
    Room,
    Drawer,
    WingType,
    SearchResult,
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
        pass  # Windows ChromaDB file locks


@pytest.fixture
def palace(temp_storage):
    """Create a PalaceIndex with temporary storage."""
    config = PalaceConfig(storage_path=temp_storage)
    index = PalaceIndex(config)
    index.initialize()
    yield index


class TestDrawer:
    """Tests for Drawer class."""

    def test_create_drawer(self):
        """Test drawer creation with auto-generated ID."""
        drawer = Drawer.create("room_123", "Test content")
        
        assert drawer.id.startswith("drawer_")
        assert drawer.room_id == "room_123"
        assert drawer.content == "Test content"
        assert drawer.embedding is None
        assert drawer.metadata == {}

    def test_create_drawer_with_metadata(self):
        """Test drawer creation with metadata."""
        metadata = {"source": "test", "priority": 1}
        drawer = Drawer.create("room_123", "Content", metadata)
        
        assert drawer.metadata == metadata

    def test_update_drawer(self):
        """Test drawer content update."""
        drawer = Drawer.create("room_123", "Original")
        original_updated = drawer.updated_at
        
        drawer.update("New content")
        
        assert drawer.content == "New content"
        assert drawer.updated_at > original_updated
        assert drawer.embedding is None  # Invalidated

    def test_drawer_serialization(self):
        """Test drawer to_dict/from_dict round-trip."""
        drawer = Drawer.create("room_123", "Content", {"key": "value"})
        
        data = drawer.to_dict()
        restored = Drawer.from_dict(data)
        
        assert restored.id == drawer.id
        assert restored.content == drawer.content
        assert restored.metadata == drawer.metadata


class TestRoom:
    """Tests for Room class."""

    def test_create_room(self):
        """Test room creation."""
        room = Room.create("wing_123", "Test Room", "Description")
        
        assert room.id.startswith("room_")
        assert room.wing_id == "wing_123"
        assert room.name == "Test Room"
        assert room.description == "Description"

    def test_add_drawer(self):
        """Test adding drawers to room."""
        room = Room.create("wing_123", "Room")
        drawer = Drawer.create(room.id, "Content")
        
        room.add_drawer(drawer)
        
        assert len(room.drawers) == 1
        assert drawer.id in room.drawers

    def test_get_drawer(self):
        """Test getting drawer from room."""
        room = Room.create("wing_123", "Room")
        drawer = Drawer.create(room.id, "Content")
        room.add_drawer(drawer)
        
        retrieved = room.get_drawer(drawer.id)
        
        assert retrieved == drawer

    def test_remove_drawer(self):
        """Test removing drawer from room."""
        room = Room.create("wing_123", "Room")
        drawer = Drawer.create(room.id, "Content")
        room.add_drawer(drawer)
        
        result = room.remove_drawer(drawer.id)
        
        assert result is True
        assert drawer.id not in room.drawers

    def test_remove_nonexistent_drawer(self):
        """Test removing non-existent drawer."""
        room = Room.create("wing_123", "Room")
        
        result = room.remove_drawer("nonexistent")
        
        assert result is False


class TestWing:
    """Tests for Wing class."""

    def test_create_wing(self):
        """Test wing creation."""
        wing = Wing.create("AutoAgent-TW", WingType.PROJECT, "Project wing")
        
        assert wing.id.startswith("wing_")
        assert wing.name == "AutoAgent-TW"
        assert wing.wing_type == WingType.PROJECT
        assert wing.description == "Project wing"

    def test_add_room(self):
        """Test adding room to wing."""
        wing = Wing.create("Project", WingType.PROJECT)
        room = Room.create(wing.id, "Architecture")
        
        wing.add_room(room)
        
        assert len(wing.rooms) == 1
        assert room.id in wing.rooms

    def test_get_room_by_name(self):
        """Test getting room by name."""
        wing = Wing.create("Project", WingType.PROJECT)
        room = Room.create(wing.id, "Architecture")
        wing.add_room(room)
        
        retrieved = wing.get_room_by_name("Architecture")
        
        assert retrieved == room

    def test_remove_room(self):
        """Test removing room from wing."""
        wing = Wing.create("Project", WingType.PROJECT)
        room = Room.create(wing.id, "Architecture")
        wing.add_room(room)
        
        result = wing.remove_room(room.id)
        
        assert result is True
        assert room.id not in wing.rooms


class TestPalaceIndex:
    """Tests for PalaceIndex class."""

    def test_create_wing(self, palace):
        """Test creating a wing."""
        wing = palace.create_wing(
            "AutoAgent-TW",
            WingType.PROJECT,
            "AI Harness Framework",
        )
        
        assert wing.id in palace.wings
        assert wing.name == "AutoAgent-TW"
        assert wing.wing_type == WingType.PROJECT

    def test_get_wing_by_name(self, palace):
        """Test getting wing by name."""
        created = palace.create_wing("AutoAgent-TW", WingType.PROJECT)
        
        retrieved = palace.get_wing_by_name("AutoAgent-TW")
        
        assert retrieved == created

    def test_list_wings_by_type(self, palace):
        """Test listing wings filtered by type."""
        palace.create_wing("Project1", WingType.PROJECT)
        palace.create_wing("Domain1", WingType.DOMAIN)
        palace.create_wing("Project2", WingType.PROJECT)
        
        projects = palace.list_wings(wing_type=WingType.PROJECT)
        
        assert len(projects) == 2

    def test_delete_wing(self, palace):
        """Test deleting a wing."""
        wing = palace.create_wing("Test", WingType.PROJECT)
        
        result = palace.delete_wing(wing.id)
        
        assert result is True
        assert wing.id not in palace.wings

    def test_create_room(self, palace):
        """Test creating a room."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        
        room = palace.create_room(wing.id, "Architecture", "Architecture docs")
        
        assert room is not None
        assert room.name == "Architecture"
        assert room.wing_id == wing.id

    def test_create_room_invalid_wing(self, palace):
        """Test creating room with invalid wing."""
        room = palace.create_room("invalid_wing", "Room")
        
        assert room is None

    def test_add_drawer(self, palace):
        """Test adding a drawer."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        room = palace.create_room(wing.id, "Architecture")
        
        drawer = palace.add_drawer(
            wing.id, room.id,
            "This is verbatim content",
            {"source": "test"},
        )
        
        assert drawer is not None
        assert drawer.content == "This is verbatim content"
        assert drawer.metadata == {"source": "test"}

    def test_get_drawer(self, palace):
        """Test getting a drawer."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        room = palace.create_room(wing.id, "Architecture")
        created = palace.add_drawer(wing.id, room.id, "Content")
        
        retrieved = palace.get_drawer(wing.id, room.id, created.id)
        
        assert retrieved == created

    def test_update_drawer(self, palace):
        """Test updating drawer content."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        room = palace.create_room(wing.id, "Architecture")
        drawer = palace.add_drawer(wing.id, room.id, "Original")
        
        updated = palace.update_drawer(wing.id, room.id, drawer.id, "Updated")
        
        assert updated is not None
        assert updated.content == "Updated"

    def test_delete_drawer(self, palace):
        """Test deleting a drawer."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        room = palace.create_room(wing.id, "Architecture")
        drawer = palace.add_drawer(wing.id, room.id, "Content")
        
        result = palace.delete_drawer(wing.id, room.id, drawer.id)
        
        assert result is True
        assert palace.get_drawer(wing.id, room.id, drawer.id) is None

    def test_get_stats(self, palace):
        """Test getting palace statistics."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        room = palace.create_room(wing.id, "Architecture")
        palace.add_drawer(wing.id, room.id, "Content 1")
        palace.add_drawer(wing.id, room.id, "Content 2")
        
        stats = palace.get_stats()
        
        assert stats["wings"] == 1
        assert stats["rooms"] == 1
        assert stats["drawers"] == 2

    def test_search_by_date(self, palace):
        """Test searching by date range."""
        wing = palace.create_wing("Project", WingType.PROJECT)
        room = palace.create_room(wing.id, "Architecture")
        
        # Create drawers at different times
        drawer1 = palace.add_drawer(wing.id, room.id, "Old content")
        drawer2 = palace.add_drawer(wing.id, room.id, "New content")
        
        now = datetime.now()
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)
        
        results = palace.search_by_date(start, end)
        
        assert len(results) == 2

    def test_persistence(self, temp_storage):
        """Test that palace persists to disk."""
        config = PalaceConfig(storage_path=temp_storage)
        
        # Create and populate
        palace1 = PalaceIndex(config)
        palace1.initialize()
        wing = palace1.create_wing("Project", WingType.PROJECT)
        palace1.close()
        
        # Reopen
        palace2 = PalaceIndex(config)
        palace2.initialize()
        
        assert len(palace2.wings) == 1
        assert palace2.get_wing_by_name("Project") is not None


class TestWingType:
    """Tests for WingType enum."""

    def test_wing_types(self):
        """Test all wing types exist."""
        assert WingType.PROJECT.value == "project"
        assert WingType.DOMAIN.value == "domain"
        assert WingType.AGENT.value == "agent"
        assert WingType.SYSTEM.value == "system"
