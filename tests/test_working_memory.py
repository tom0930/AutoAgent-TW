"""
Tests for Working Memory Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta

from src.core.memory import WorkingMemory, WorkingMemoryConfig, FlushEvent


class TestWorkingMemoryConfig:
    """Tests for WorkingMemoryConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = WorkingMemoryConfig(workspace_root=Path("/tmp/test"))
        
        assert config.max_tokens == 128000
        assert config.trigger_threshold == 0.75
        assert config.flush_target == 0.4
        assert config.auto_flush_enabled is True
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = WorkingMemoryConfig(
            workspace_root=Path("/custom/path"),
            max_tokens=64000,
            trigger_threshold=0.8,
            flush_target=0.3,
            auto_flush_enabled=False,
        )
        
        assert config.max_tokens == 64000
        assert config.trigger_threshold == 0.8
        assert config.flush_target == 0.3
        assert config.auto_flush_enabled is False


class TestWorkingMemory:
    """Tests for WorkingMemory class"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace directory"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def memory(self, temp_workspace):
        """Create a WorkingMemory instance with temp workspace"""
        config = WorkingMemoryConfig(workspace_root=temp_workspace)
        return WorkingMemory(config)
    
    def test_memory_dir_created(self, temp_workspace):
        """Test that memory directory is created"""
        config = WorkingMemoryConfig(workspace_root=temp_workspace)
        _ = WorkingMemory(config)
        
        memory_dir = temp_workspace / "memory"
        assert memory_dir.exists()
        assert memory_dir.is_dir()
    
    def test_get_daily_file(self, memory):
        """Test daily file path generation"""
        date = datetime(2026, 4, 23)
        daily_file = memory.get_daily_file(date)
        
        assert daily_file.name == "2026-04-23.md"
        assert daily_file.parent.name == "memory"
    
    def test_should_flush_below_threshold(self, memory):
        """Test should_flush returns False below threshold"""
        # 75% of 128000 = 96000
        assert memory.should_flush(50000) is False
        assert memory.should_flush(95999) is False
    
    def test_should_flush_above_threshold(self, memory):
        """Test should_flush returns True at/above threshold"""
        assert memory.should_flush(96000) is True
        assert memory.should_flush(128000) is True
    
    def test_should_flush_disabled(self, temp_workspace):
        """Test should_flush respects auto_flush_enabled=False"""
        config = WorkingMemoryConfig(
            workspace_root=temp_workspace,
            auto_flush_enabled=False,
        )
        memory = WorkingMemory(config)
        
        assert memory.should_flush(128000) is False
    
    def test_write_and_load_daily(self, memory):
        """Test writing and loading daily memory"""
        content = "# Test Content\n\nThis is a test."
        memory.write_daily(content, mode="replace")
        
        loaded = memory.load_daily()
        assert loaded == content
    
    def test_write_and_load_memory(self, memory):
        """Test writing and loading long-term memory"""
        content = "# Long-term Memory\n\nImportant facts here."
        memory.write_memory(content, mode="replace")
        
        loaded = memory.load_memory()
        assert loaded == content
    
    def test_append_to_daily(self, memory):
        """Test appending to daily memory"""
        memory.write_daily("First content", mode="replace")
        memory.write_daily("Second content", mode="append")
        
        loaded = memory.load_daily()
        assert "First content" in loaded
        assert "Second content" in loaded
    
    def test_load_recent(self, memory):
        """Test loading recent daily files"""
        # Write today
        memory.write_daily("Today's content", mode="replace")
        
        # Write yesterday
        yesterday = datetime.now() - timedelta(days=1)
        memory.write_daily("Yesterday's content", date=yesterday, mode="replace")
        
        recent = memory.load_recent(days=2)
        
        assert "Today's content" in recent
        assert "Yesterday's content" in recent
    
    def test_load_context(self, memory):
        """Test loading full context"""
        memory.write_memory("Long-term facts", mode="replace")
        memory.write_daily("Daily notes", mode="replace")
        
        context = memory.load_context()
        
        assert "Long-term Memory" in context
        assert "Long-term facts" in context
        assert "Recent Context" in context
        assert "Daily notes" in context
    
    def test_estimate_tokens(self, memory):
        """Test token estimation"""
        # English text
        english = "Hello world this is a test"
        english_tokens = memory._estimate_tokens(english)
        assert english_tokens > 0
        assert english_tokens < len(english)  # Should be compressed
        
        # Chinese text
        chinese = "這是一個測試"
        chinese_tokens = memory._estimate_tokens(chinese)
        assert chinese_tokens > 0
        
        # Mixed text
        mixed = "Hello 這是一個 test 測試"
        mixed_tokens = memory._estimate_tokens(mixed)
        assert mixed_tokens > 0
    
    def test_flush_creates_event(self, memory):
        """Test that flush creates a FlushEvent"""
        content = "Test content " * 1000  # Moderate content
        # Don't pass fake token count - let flush estimate it
        
        compressed, new_tokens, event = memory.flush(content, 0)  # 0 = auto-estimate
        
        assert isinstance(event, FlushEvent)
        # tokens_before should be estimated from content
        assert event.tokens_before > 0
        assert event.tokens_after == new_tokens
        # Compression ratio should be <= 1.0
        assert event.compression_ratio <= 1.0
        assert len(memory.get_flush_history()) == 1
    
    def test_flush_writes_to_daily(self, memory):
        """Test that flush writes content to daily file"""
        content = "Test content to flush"
        current_tokens = 100000  # Above threshold
        
        memory.flush(content, current_tokens)
        
        daily_content = memory.load_daily()
        assert len(daily_content) > 0
    
    def test_custom_summarization(self, memory):
        """Test flush with custom summarization function"""
        def custom_summary(content: str, target_tokens: int) -> str:
            return f"CUSTOM: {content[:100]}"
        
        content = "Test content " * 1000
        current_tokens = 100000
        
        compressed, _, _ = memory.flush(
            content, 
            current_tokens, 
            summary_func=custom_summary
        )
        
        assert compressed.startswith("CUSTOM:")
    
    def test_get_stats(self, memory):
        """Test statistics retrieval"""
        memory.write_memory("Long-term", mode="replace")
        memory.write_daily("Daily", mode="replace")
        
        stats = memory.get_stats()
        
        assert stats["memory_file_exists"] is True
        assert stats["memory_tokens"] > 0
        assert stats["recent_tokens"] > 0
        assert stats["flush_count"] == 0
        assert "config" in stats
    
    def test_list_daily_files(self, memory):
        """Test listing daily files"""
        # Create a few daily files
        for i in range(3):
            date = datetime.now() - timedelta(days=i)
            memory.write_daily(f"Day {i}", date=date, mode="replace")
        
        files = memory.list_daily_files()
        
        assert len(files) == 3
        # Should be sorted in reverse (newest first)
        assert files[0].stem >= files[1].stem


class TestFlushEvent:
    """Tests for FlushEvent dataclass"""
    
    def test_flush_event_creation(self):
        """Test FlushEvent creation"""
        event = FlushEvent(
            timestamp=datetime.now(),
            tokens_before=100000,
            tokens_after=40000,
            compression_ratio=0.4,
            target_file="/path/to/2026-04-23.md",
        )
        
        assert event.tokens_before == 100000
        assert event.tokens_after == 40000
        assert event.compression_ratio == 0.4
    
    def test_flush_event_to_dict(self):
        """Test FlushEvent serialization"""
        event = FlushEvent(
            timestamp=datetime(2026, 4, 23, 16, 50, 0),
            tokens_before=100000,
            tokens_after=40000,
            compression_ratio=0.4,
            target_file="/path/to/2026-04-23.md",
        )
        
        d = event.to_dict()
        
        assert d["tokens_before"] == 100000
        assert d["tokens_after"] == 40000
        assert d["compression_ratio"] == 0.4
        assert "2026-04-23" in d["timestamp"]
