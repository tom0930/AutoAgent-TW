"""
AI Harness Canvas System 測試
"""
import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.harness.canvas import CanvasSystem, NodeType, NodeStatus


class TestCanvasSystem:
    """Canvas System 測試"""
    
    @pytest.fixture
    def temp_storage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def canvas(self, temp_storage):
        return CanvasSystem("test", temp_storage)
    
    def test_add_node(self, canvas):
        """測試添加節點"""
        node_id = canvas.add_node("Test Node", NodeType.AGENT)
        assert node_id is not None
        
        node = canvas.get_node(node_id)
        assert node is not None
        assert node.label == "Test Node"
        assert node.node_type == NodeType.AGENT
    
    def test_update_node(self, canvas):
        """測試更新節點"""
        node_id = canvas.add_node("Test", NodeType.AGENT)
        
        result = canvas.update_node(node_id, status=NodeStatus.ACTIVE)
        assert result is True
        
        node = canvas.get_node(node_id)
        assert node.status == NodeStatus.ACTIVE
    
    def test_connect(self, canvas):
        """測試連接"""
        node1 = canvas.add_node("Node 1", NodeType.AGENT)
        node2 = canvas.add_node("Node 2", NodeType.SESSION)
        
        edge_id = canvas.connect(node1, node2, label="test")
        assert edge_id is not None
    
    def test_snapshot(self, canvas):
        """測試快照"""
        canvas.add_node("Node 1", NodeType.AGENT)
        canvas.add_node("Node 2", NodeType.SESSION)
        
        snap_id = canvas.snapshot("Test Snapshot")
        assert snap_id is not None
        
        snapshots = canvas.list_snapshots()
        assert len(snapshots) >= 1
    
    def test_export_mermaid(self, canvas):
        """測試 Mermaid 匯出"""
        canvas.add_node("Node 1", NodeType.AGENT)
        canvas.add_node("Node 2", NodeType.SESSION)
        
        mermaid = canvas.export_mermaid()
        assert "graph TD" in mermaid
        assert "Node" in mermaid


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
