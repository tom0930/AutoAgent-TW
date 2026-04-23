"""
AI Harness Session Manager 測試
"""
import pytest
import time
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.session_manager import SessionManager, SessionKind, SessionStatus


class TestSessionManager:
    """Session Manager 測試"""
    
    @pytest.fixture
    def temp_storage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "sessions"
    
    @pytest.fixture
    def manager(self, temp_storage):
        return SessionManager(temp_storage)
    
    def test_create_session(self, manager):
        """測試建立 Session"""
        session = manager.create(SessionKind.MAIN, label="Test Session")
        
        assert session is not None
        assert session.kind == SessionKind.MAIN
        assert session.label == "Test Session"
        assert session.message_count == 0
    
    def test_get_session(self, manager):
        """測試取得 Session"""
        session = manager.create(SessionKind.MAIN)
        retrieved = manager.get(session.key)
        
        assert retrieved is not None
        assert retrieved.key == session.key
    
    def test_send_message(self, manager):
        """測試發送訊息"""
        session = manager.create(SessionKind.MAIN)
        
        msg = manager.send(session.key, "Hello", role="user")
        assert msg is not None
        assert msg.role == "user"
        assert msg.content == "Hello"
        
        retrieved = manager.get(session.key)
        assert retrieved.message_count == 1
    
    def test_list_sessions(self, manager):
        """測試列出 Sessions"""
        manager.create(SessionKind.MAIN)
        manager.create(SessionKind.ISOLATED)
        
        sessions = manager.list()
        assert len(sessions) >= 2
    
    def test_destroy_session(self, manager):
        """測試銷毀 Session"""
        session = manager.create(SessionKind.MAIN)
        key = session.key
        
        result = manager.destroy(key)
        assert result is True
        
        retrieved = manager.get(key)
        assert retrieved is None
    
    def test_get_stats(self, manager):
        """測試統計資訊"""
        manager.create(SessionKind.MAIN)
        manager.create(SessionKind.ISOLATED)
        
        stats = manager.get_stats()
        assert 'total' in stats
        assert stats['total'] >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
