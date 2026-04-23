"""
AI Harness Canvas System
功能：視覺化狀態管理、節點狀態、圖形渲染
版本：v1.0.0
"""
import time
import json
import threading
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import logging


class NodeStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class NodeType(Enum):
    AGENT = "agent"
    SESSION = "session"
    TOOL = "tool"
    SERVICE = "service"
    DEVICE = "device"
    CANVAS = "canvas"


@dataclass
class CanvasNode:
    """Canvas 節點"""
    node_id: str
    node_type: NodeType
    label: str
    status: NodeStatus = NodeStatus.IDLE
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0
    last_update: float = 0
    
    # 連接
    connections: List[str] = field(default_factory=list)
    
    def update(self, status: Optional[NodeStatus] = None, metadata: Optional[Dict[str, Any]] = None):
        """更新節點狀態"""
        if status is not None:
            self.status = status
        if metadata is not None:
            self.metadata.update(metadata)
        self.last_update = time.time()


@dataclass
class CanvasEdge:
    """Canvas 連接邊"""
    edge_id: str
    source_id: str
    target_id: str
    label: str = ""
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanvasSnapshot:
    """Canvas 快照"""
    canvas_id: str
    timestamp: float
    nodes: List[CanvasNode]
    edges: List[CanvasEdge]
    viewport: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "zoom": 1.0})


class CanvasSystem:
    """
    Canvas System - 視覺化狀態管理
    
    功能：
    - 節點管理（創建、更新、刪除）
    - 連接邊管理
    - 狀態追蹤
    - 快照保存
    - 即時更新訂閱
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, canvas_id: str = "main", storage_path: Optional[Path] = None):
        self.canvas_id = canvas_id
        self.storage_path = storage_path
        
        if storage_path:
            self.storage_path = Path(storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"harness.canvas.{canvas_id}")
        
        # 節點
        self.nodes: Dict[str, CanvasNode] = {}
        
        # 連接
        self.edges: Dict[str, CanvasEdge] = {}
        
        # 快照
        self.snapshots: List[CanvasSnapshot] = []
        self.max_snapshots = 50
        
        # 訂閱者
        self.subscribers: List[Callable] = []
        
        # 鎖
        self._lock = threading.RLock()
        
        # 載入快照
        self._load()
    
    # === 節點管理 ===
    
    def add_node(self,
                label: str,
                node_type: NodeType,
                node_id: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        新增節點
        
        Args:
            label: 節點標籤
            node_type: 節點類型
            node_id: 節點 ID（可選，自動產生）
            metadata: 額外元數據
        
        Returns:
            節點 ID
        """
        if not node_id:
            import uuid
            node_id = f"{node_type.value}_{uuid.uuid4().hex[:8]}"
        
        node = CanvasNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            created_at=time.time(),
            last_update=time.time(),
            metadata=metadata or {}
        )
        
        with self._lock:
            self.nodes[node_id] = node
        
        self._notify({'type': 'node_added', 'node': self._node_to_dict(node)})
        self._save()
        
        return node_id
    
    def update_node(self, 
                    node_id: str,
                    status: Optional[NodeStatus] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    position: Optional[Dict[str, float]] = None) -> bool:
        """更新節點"""
        with self._lock:
            node = self.nodes.get(node_id)
            if not node:
                return False
            
            if status is not None:
                node.status = status
            if metadata is not None:
                node.metadata.update(metadata)
            if position is not None:
                node.position = position
            
            node.last_update = time.time()
        
        self._notify({
            'type': 'node_updated',
            'node_id': node_id,
            'status': node.status.value if status else None
        })
        self._save()
        
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """移除節點"""
        with self._lock:
            if node_id not in self.nodes:
                return False
            
            # 移除相關連接
            edges_to_remove = [
                eid for eid, edge in self.edges.items()
                if edge.source_id == node_id or edge.target_id == node_id
            ]
            for eid in edges_to_remove:
                del self.edges[eid]
            
            del self.nodes[node_id]
        
        self._notify({'type': 'node_removed', 'node_id': node_id})
        self._save()
        
        return True
    
    def get_node(self, node_id: str) -> Optional[CanvasNode]:
        """取得節點"""
        return self.nodes.get(node_id)
    
    def list_nodes(self,
                   node_type: Optional[NodeType] = None,
                   status: Optional[NodeStatus] = None) -> List[Dict[str, Any]]:
        """列出節點"""
        with self._lock:
            result = []
            
            for node in self.nodes.values():
                if node_type and node.node_type != node_type:
                    continue
                if status and node.status != status:
                    continue
                
                result.append(self._node_to_dict(node))
            
            return result
    
    # === 連接管理 ===
    
    def connect(self,
               source_id: str,
               target_id: str,
               label: str = "",
               metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """建立連接"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        import uuid
        edge_id = f"edge_{uuid.uuid4().hex[:8]}"
        
        edge = CanvasEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            label=label,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.edges[edge_id] = edge
            
            # 更新節點的連接列表
            if edge_id not in self.nodes[source_id].connections:
                self.nodes[source_id].connections.append(edge_id)
        
        self._notify({
            'type': 'edge_added',
            'edge': asdict(edge)
        })
        self._save()
        
        return edge_id
    
    def disconnect(self, edge_id: str) -> bool:
        """斷開連接"""
        with self._lock:
            if edge_id not in self.edges:
                return False
            
            edge = self.edges[edge_id]
            
            # 從源節點移除連接
            if edge_id in self.nodes[edge.source_id].connections:
                self.nodes[edge.source_id].connections.remove(edge_id)
            
            del self.edges[edge_id]
        
        self._notify({'type': 'edge_removed', 'edge_id': edge_id})
        self._save()
        
        return True
    
    # === 快照 ===
    
    def snapshot(self, label: str = "") -> str:
        """
        建立快照
        
        Args:
            label: 快照標籤
        
        Returns:
            快照 ID
        """
        import uuid
        snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            snapshot = CanvasSnapshot(
                canvas_id=self.canvas_id,
                timestamp=time.time(),
                nodes=list(self.nodes.values()),
                edges=list(self.edges.values())
            )
            
            self.snapshots.append(snapshot)
            
            # 限制快照數量
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots = self.snapshots[-self.max_snapshots:]
        
        self._notify({
            'type': 'snapshot_created',
            'snapshot_id': snapshot_id,
            'label': label
        })
        self._save()
        
        return snapshot_id
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """列出快照"""
        return [
            {
                'snapshot_id': f"snap_{i}",
                'canvas_id': s.canvas_id,
                'timestamp': s.timestamp,
                'node_count': len(s.nodes),
                'edge_count': len(s.edges)
            }
            for i, s in enumerate(self.snapshots)
        ]
    
    # === 匯出 ===
    
    def export_json(self) -> str:
        """匯出為 JSON"""
        with self._lock:
            data = {
                'canvas_id': self.canvas_id,
                'timestamp': time.time(),
                'nodes': [self._node_to_dict(n) for n in self.nodes.values()],
                'edges': [asdict(e) for e in self.edges.values()]
            }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_mermaid(self) -> str:
        """匯出為 Mermaid 圖"""
        lines = [f"graph TD"]
        
        with self._lock:
            for node in self.nodes.values():
                status_color = {
                    NodeStatus.IDLE: "#e0e0e0",
                    NodeStatus.ACTIVE: "#90EE90",
                    NodeStatus.BUSY: "#FFD700",
                    NodeStatus.ERROR: "#FF6B6B",
                    NodeStatus.OFFLINE: "#808080"
                }.get(node.status, "#e0e0e0")
                
                lines.append(f'    {node.node_id}["{node.label}"]:::{node.status.value}')
            
            for edge in self.edges.values():
                if edge.label:
                    lines.append(f'    {edge.source_id} -->|"{edge.label}"| {edge.target_id}')
                else:
                    lines.append(f'    {edge.source_id} --> {edge.target_id}')
        
        # 添加樣式
        lines.append("")
        lines.append("    classDef idle fill:#e0e0e0,stroke:#999")
        lines.append("    classDef active fill:#90EE90,stroke:#228B22")
        lines.append("    classDef busy fill:#FFD700,stroke:#DAA520")
        lines.append("    classDef error fill:#FF6B6B,stroke:#DC143C")
        lines.append("    classDef offline fill:#808080,stroke:#555")
        
        return "\n".join(lines)
    
    # === 訂閱 ===
    
    def subscribe(self, callback: Callable):
        """訂閱更新"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """取消訂閱"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _notify(self, event: Dict[str, Any]):
        """通知訂閱者"""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Subscriber callback failed: {e}")
    
    # === 持久化 ===
    
    def _save(self):
        """保存到磁碟"""
        if not self.storage_path:
            return
        
        path = self.storage_path / f"canvas_{self.canvas_id}.json"
        
        with self._lock:
            data = {
                'canvas_id': self.canvas_id,
                'timestamp': time.time(),
                'nodes': {nid: self._node_to_dict(n) for nid, n in self.nodes.items()},
                'edges': {eid: asdict(e) for eid, e in self.edges.items()}
            }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load(self):
        """從磁碟載入"""
        if not self.storage_path:
            return
        
        path = self.storage_path / f"canvas_{self.canvas_id}.json"
        if not path.exists():
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self._lock:
                for nid, ndata in data.get('nodes', {}).items():
                    ndata['node_type'] = NodeType(ndata['node_type'])
                    ndata['status'] = NodeStatus(ndata['status'])
                    self.nodes[nid] = CanvasNode(**ndata)
                
                for eid, edata in data.get('edges', {}).items():
                    self.edges[eid] = CanvasEdge(**edata)
                    
        except Exception as e:
            self.logger.warning(f"Failed to load canvas: {e}")
    
    def _node_to_dict(self, node: CanvasNode) -> Dict[str, Any]:
        """轉換節點為字典"""
        return {
            'node_id': node.node_id,
            'node_type': node.node_type.value,
            'label': node.label,
            'status': node.status.value,
            'position': node.position,
            'metadata': node.metadata,
            'created_at': node.created_at,
            'last_update': node.last_update,
            'connections': node.connections
        }


def main():
    """測試"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        canvas = CanvasSystem("test", Path(tmpdir))
        
        # 添加節點
        agent = canvas.add_node("主代理", NodeType.AGENT)
        session = canvas.add_node("主對話", NodeType.SESSION)
        tool = canvas.add_node("檔案工具", NodeType.TOOL)
        
        print(f"Added nodes: {agent}, {session}, {tool}")
        
        # 建立連接
        canvas.connect(agent, session, "管理")
        canvas.connect(session, tool, "使用")
        
        # 更新狀態
        canvas.update_node(agent, status=NodeStatus.ACTIVE)
        
        # 列出節點
        print("\nNodes:")
        for n in canvas.list_nodes():
            print(f"  [{n['status']}] {n['label']} ({n['node_type']})")
        
        # 匯出 Mermaid
        print("\nMermaid:")
        print(canvas.export_mermaid())
        
        # 建立快照
        snap_id = canvas.snapshot("測試快照")
        print(f"\nSnapshot: {snap_id}")


if __name__ == '__main__':
    main()
