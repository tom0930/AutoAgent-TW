"""
AI Harness Session Manager
功能：建立/管理/銷毀 Session，Session 間訊息路由，跨 Session 記憶體共享
版本：v1.0.0
"""
import json
import uuid
import time
import threading
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
from collections import defaultdict


class SessionKind(Enum):
    MAIN = "main"              # 主對話 Session
    ISOLATED = "isolated"      # 隔離的獨立任務 Session
    SUBAGENT = "subagent"      # 子代理 Session
    CRON = "cron"              # Cron 排程觸發的 Session
    HEARTBEAT = "heartbeat"    # 心跳檢查 Session


class SessionStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    TERMINATED = "terminated"


@dataclass
class SessionMessage:
    """Session 訊息"""
    id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Session 資料結構"""
    key: str
    kind: SessionKind
    label: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: float = 0
    last_active: float = 0
    model: Optional[str] = None
    message_count: int = 0
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    messages: List[SessionMessage] = field(default_factory=list)
    
    def touch(self):
        """更新最後活躍時間"""
        self.last_active = time.time()
        self.status = SessionStatus.ACTIVE
    
    def add_message(self, role: str, content: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> SessionMessage:
        """新增訊息"""
        msg = SessionMessage(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            role=role,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self.message_count += 1
        self.touch()
        return msg
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """從字典建立"""
        # 轉換 enum
        if isinstance(data.get('kind'), str):
            data['kind'] = SessionKind(data['kind'])
        if isinstance(data.get('status'), str):
            data['status'] = SessionStatus(data['status'])
        
        # 轉換訊息
        if 'messages' in data:
            data['messages'] = [
                SessionMessage(**m) if isinstance(m, dict) else m 
                for m in data['messages']
            ]
        
        return cls(**data)


class SessionManager:
    """
    Session 管理器
    
    提供 Session 的建立、管理、銷毀功能。
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, Session] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        
        # 載入已存在的 Session
        self._load_sessions()
        
        # 啟動 Session 清理執行緒
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, 
            daemon=True,
            name="SessionManager-Cleanup"
        )
        self._cleanup_thread.start()
    
    def _session_file(self, key: str) -> Path:
        """取得 Session 檔案路徑"""
        # 使用 key 的 hash 作為檔名的一部分，避免路徑問題
        key_hash = hashlib.md5(key.encode()).hexdigest()[:8]
        return self.storage_path / f"session_{key_hash}.json"
    
    def create(self, 
               kind: SessionKind = SessionKind.MAIN,
               label: Optional[str] = None,
               model: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None) -> Session:
        """
        建立新 Session
        
        Args:
            kind: Session 類型
            label: Session 標籤（可選）
            model: 使用的模型（可選）
            metadata: 額外元數據（可選）
        
        Returns:
            新建立的 Session
        """
        with self._lock:
            key = f"session_{uuid.uuid4().hex[:12]}"
            
            session = Session(
                key=key,
                kind=kind,
                label=label,
                created_at=time.time(),
                last_active=time.time(),
                model=model,
                metadata=metadata or {}
            )
            
            self.sessions[key] = session
            self._save_session(session)
            
            self._emit('session_created', session)
            
            return session
    
    def get(self, key: str) -> Optional[Session]:
        """取得 Session"""
        with self._lock:
            session = self.sessions.get(key)
            if session:
                session.touch()
            return session
    
    def get_or_create(self, key: str, **kwargs) -> Session:
        """取得或建立 Session"""
        with self._lock:
            session = self.sessions.get(key)
            if not session:
                session = self.create(**kwargs)
                # 重新設定 key 為指定的 key
                session.key = key
                self.sessions[key] = session
            return session
    
    def list(self, 
             kinds: Optional[List[SessionKind]] = None,
             active_minutes: Optional[int] = None,
             limit: int = 50) -> List[Session]:
        """
        列出 Sessions
        
        Args:
            kinds: 過濾的 Session 類型
            active_minutes: 只列出最近 active_minutes 分鐘內活躍的
            limit: 返回數量限制
        
        Returns:
            Session 列表
        """
        with self._lock:
            sessions = list(self.sessions.values())
            
            if kinds:
                sessions = [s for s in sessions if s.kind in kinds]
            
            if active_minutes:
                cutoff = time.time() - (active_minutes * 60)
                sessions = [s for s in sessions if s.last_active >= cutoff]
            
            # 按最後活躍時間排序
            sessions.sort(key=lambda s: s.last_active, reverse=True)
            
            return sessions[:limit]
    
    def send(self, 
             key: str, 
             message: str, 
             role: str = "user",
             metadata: Optional[Dict[str, Any]] = None) -> Optional[SessionMessage]:
        """
        向 Session 發送訊息
        
        Args:
            key: Session key
            message: 訊息內容
            role: 角色 (user/assistant/system)
            metadata: 額外元數據
        
        Returns:
            建立的訊息，如果 Session 不存在則返回 None
        """
        with self._lock:
            session = self.get(key)
            if not session:
                return None
            
            msg = session.add_message(role, message, metadata)
            self._save_session(session)
            
            self._emit('message_sent', session, msg)
            
            return msg
    
    def destroy(self, key: str) -> bool:
        """
        銷毀 Session
        
        Args:
            key: Session key
        
        Returns:
            是否成功銷毀
        """
        with self._lock:
            if key not in self.sessions:
                return False
            
            session = self.sessions[key]
            del self.sessions[key]
            
            # 刪除檔案
            path = self._session_file(key)
            if path.exists():
                path.unlink()
            
            self._emit('session_destroyed', session)
            
            return True
    
    def destroy_all(self, kinds: Optional[List[SessionKind]] = None) -> int:
        """
        銷毀所有符合條件的 Session
        
        Args:
            kinds: 要銷毀的 Session 類型，None 表示全部
        
        Returns:
            銷毀的數量
        """
        with self._lock:
            to_destroy = []
            
            for key, session in self.sessions.items():
                if kinds is None or session.kind in kinds:
                    to_destroy.append(key)
            
            for key in to_destroy:
                path = self._session_file(key)
                if path.exists():
                    path.unlink()
                del self.sessions[key]
            
            return len(to_destroy)
    
    def subscribe(self, event: str, callback: Callable):
        """
        訂閱事件
        
        Args:
            event: 事件名稱
            callback: 回呼函數
        """
        self.subscribers[event].append(callback)
    
    def _emit(self, event: str, *args):
        """發送事件"""
        for callback in self.subscribers.get(event, []):
            try:
                callback(*args)
            except Exception as e:
                pass  # 記錄錯誤
    
    def _save_session(self, session: Session):
        """持久化 Session"""
        path = self._session_file(session.key)
        
        # 限制訊息歷史長度（只保存最後 1000 條）
        messages = session.messages[-1000:]
        
        data = session.to_dict()
        data['messages'] = [asdict(m) for m in messages]
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_sessions(self):
        """載入所有 Session"""
        for path in self.storage_path.glob("session_*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    self.sessions[session.key] = session
            except Exception as e:
                pass  # 忽略損壞的 Session 檔案
    
    def _cleanup_loop(self):
        """清理過期 Session"""
        while True:
            time.sleep(300)  # 每 5 分鐘清理一次
            
            with self._lock:
                now = time.time()
                expired = []
                
                for key, session in self.sessions.items():
                    # 超過 7 天不活躍的 Session
                    if now - session.last_active > 7 * 24 * 3600:
                        expired.append(key)
                
                for key in expired:
                    path = self._session_file(key)
                    if path.exists():
                        path.unlink()
                    del self.sessions[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """取得統計資訊"""
        with self._lock:
            by_kind = defaultdict(int)
            by_status = defaultdict(int)
            total_messages = 0
            
            for session in self.sessions.values():
                by_kind[session.kind.value] += 1
                by_status[session.status.value] += 1
                total_messages += session.message_count
            
            return {
                'total': len(self.sessions),
                'by_kind': dict(by_kind),
                'by_status': dict(by_status),
                'total_messages': total_messages,
                'storage_path': str(self.storage_path)
            }


def main():
    """測試/示範"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SessionManager(Path(tmpdir) / "sessions")
        
        # 建立 Session
        s1 = manager.create(SessionKind.MAIN, label="主對話")
        print(f"Created: {s1.key}")
        
        # 發送訊息
        manager.send(s1.key, "你好！", role="user")
        manager.send(s1.key, "你好！很高興見到你。", role="assistant")
        
        # 列出
        sessions = manager.list()
        print(f"Total sessions: {len(sessions)}")
        
        # 統計
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
