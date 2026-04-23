"""
AI Harness Node Pairing
功能：設備配對管理、安全驗證、狀態同步
版本：v1.0.0
"""
import os
import json
import time
import uuid
import hashlib
import secrets
import struct
import base64
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging
import threading


class DeviceType(Enum):
    ANDROID = "android"
    IOS = "ios"
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"


class PairingStatus(Enum):
    PENDING = "pending"
    PAIRED = "paired"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"


class NodePairing:
    """
    Node Pairing - 設備配對管理
    
    功能：
    - 設備發現與配對
    - 配對碼驗證
    - 連接管理
    - 狀態同步
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, storage_path: Path, config: Optional[Dict] = None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {}
        self.logger = logging.getLogger("harness.node")
        
        # 配對記錄
        self.pairings: Dict[str, 'DevicePairing'] = {}
        
        # 待處理配對請求
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        
        # 配對碼有效期（秒）
        self.pairing_code_ttl = self.config.get('pairing_code_ttl', 300)
        
        # 配對有效期（天）
        self.pairing_validity_days = self.config.get('pairing_validity_days', 365)
        
        # 連接超時（秒）
        self.connection_timeout = self.config.get('connection_timeout', 30)
        
        # 事件回呼
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # 鎖
        self._lock = threading.RLock()
        
        # 載入已存在的配對
        self._load_pairings()
    
    def generate_pairing_code(self) -> str:
        """
        產生配對碼
        
        Returns:
            6 位數配對碼
        """
        code = secrets.randbelow(1000000)
        return f"{code:06d}"
    
    def generate_device_token(self) -> str:
        """產生設備令牌"""
        return secrets.token_urlsafe(32)
    
    def initiate_pairing(self, 
                        device_type: DeviceType,
                        device_name: str,
                        device_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        初始化配對流程
        
        Args:
            device_type: 設備類型
            device_name: 設備名稱
            device_info: 設備資訊
        
        Returns:
            配對請求資訊（包含配對碼）
        """
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        
        pairing_code = self.generate_pairing_code()
        expires_at = time.time() + self.pairing_code_ttl
        
        request = {
            'request_id': request_id,
            'device_type': device_type.value,
            'device_name': device_name,
            'device_info': device_info or {},
            'pairing_code': pairing_code,
            'created_at': time.time(),
            'expires_at': expires_at,
            'status': PairingStatus.PENDING.value
        }
        
        with self._lock:
            self.pending_requests[request_id] = request
        
        self.logger.info(f"Pairing initiated: {device_name} ({request_id})")
        
        return {
            'request_id': request_id,
            'pairing_code': pairing_code,
            'expires_in': self.pairing_code_ttl,
            'expires_at': expires_at
        }
    
    def confirm_pairing(self, request_id: str, pairing_code: str) -> Optional[Dict[str, Any]]:
        """
        確認配對
        
        Args:
            request_id: 配對請求 ID
            pairing_code: 配對碼
        
        Returns:
            配對結果，包含設備令牌
        """
        with self._lock:
            request = self.pending_requests.get(request_id)
            
            if not request:
                self.logger.warning(f"Pairing request not found: {request_id}")
                return None
            
            # 檢查是否過期
            if time.time() > request['expires_at']:
                request['status'] = PairingStatus.EXPIRED.value
                self.logger.warning(f"Pairing code expired: {request_id}")
                return None
            
            # 驗證配對碼
            if request['pairing_code'] != pairing_code:
                self.logger.warning(f"Invalid pairing code: {request_id}")
                return None
            
            # 建立配對
            pairing_id = f"pair_{uuid.uuid4().hex[:12]}"
            device_token = self.generate_device_token()
            
            pairing = DevicePairing(
                id=pairing_id,
                device_type=DeviceType(request['device_type']),
                device_name=request['device_name'],
                device_info=request['device_info'],
                device_token=device_token,
                token_hash=hashlib.sha256(device_token.encode()).hexdigest(),
                created_at=time.time(),
                expires_at=time.time() + (self.pairing_validity_days * 86400),
                status=PairingStatus.PAIRED,
                last_seen=time.time()
            )
            
            self.pairings[pairing_id] = pairing
            
            # 移除待處理請求
            del self.pending_requests[request_id]
            
            # 保存
            self._save_pairing(pairing)
            
            self.logger.info(f"Device paired: {request['device_name']} ({pairing_id})")
            
            # 觸發事件
            self._emit('device_paired', pairing)
            
            return {
                'pairing_id': pairing_id,
                'device_token': device_token,
                'expires_at': pairing.expires_at
            }
    
    def revoke_pairing(self, pairing_id: str) -> bool:
        """撤銷配對"""
        with self._lock:
            pairing = self.pairings.get(pairing_id)
            if not pairing:
                return False
            
            pairing.status = PairingStatus.REVOKED
            
            # 刪除檔案
            path = self._pairing_file(pairing_id)
            if path.exists():
                path.unlink()
            
            del self.pairings[pairing_id]
            
            self.logger.info(f"Pairing revoked: {pairing_id}")
            self._emit('device_revoked', pairing)
            
            return True
    
    def verify_token(self, device_token: str) -> Optional['DevicePairing']:
        """
        驗證設備令牌
        
        Args:
            device_token: 設備令牌
        
        Returns:
            配對資訊，驗證失敗返回 None
        """
        token_hash = hashlib.sha256(device_token.encode()).hexdigest()
        
        for pairing in self.pairings.values():
            if pairing.token_hash == token_hash:
                # 檢查是否過期
                if time.time() > pairing.expires_at:
                    pairing.status = PairingStatus.EXPIRED
                    return None
                
                # 更新最後連線時間
                pairing.last_seen = time.time()
                self._save_pairing(pairing)
                
                return pairing
        
        return None
    
    def list_devices(self, 
                    status: Optional[PairingStatus] = None,
                    device_type: Optional[DeviceType] = None) -> List[Dict[str, Any]]:
        """列出已配對的設備"""
        with self._lock:
            result = []
            
            for pairing in self.pairings.values():
                if status and pairing.status != status:
                    continue
                
                if device_type and pairing.device_type != device_type:
                    continue
                
                result.append({
                    'id': pairing.id,
                    'device_type': pairing.device_type.value,
                    'device_name': pairing.device_name,
                    'status': pairing.status.value,
                    'created_at': pairing.created_at,
                    'last_seen': pairing.last_seen,
                    'expires_at': pairing.expires_at
                })
            
            return result
    
    def get_device(self, pairing_id: str) -> Optional['DevicePairing']:
        """取得設備配對資訊"""
        return self.pairings.get(pairing_id)
    
    def register_event_handler(self, event: str, handler: Callable):
        """註冊事件處理器"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def _emit(self, event: str, *args):
        """觸發事件"""
        for handler in self.event_handlers.get(event, []):
            try:
                handler(*args)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}")
    
    def _pairing_file(self, pairing_id: str) -> Path:
        """取得配對檔案路徑"""
        key_hash = hashlib.md5(pairing_id.encode()).hexdigest()[:8]
        return self.storage_path / f"pairing_{key_hash}.json"
    
    def _save_pairing(self, pairing: 'DevicePairing'):
        """保存配對"""
        path = self._pairing_file(pairing.id)
        
        data = {
            'id': pairing.id,
            'device_type': pairing.device_type.value,
            'device_name': pairing.device_name,
            'device_info': pairing.device_info,
            'token_hash': pairing.token_hash,
            'created_at': pairing.created_at,
            'expires_at': pairing.expires_at,
            'status': pairing.status.value,
            'last_seen': pairing.last_seen
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_pairings(self):
        """載入所有配對"""
        for path in self.storage_path.glob("pairing_*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    data['device_type'] = DeviceType(data['device_type'])
                    data['status'] = PairingStatus(data['status'])
                    
                    pairing = DevicePairing(**data)
                    self.pairings[pairing.id] = pairing
                    
            except Exception as e:
                self.logger.warning(f"Failed to load pairing {path}: {e}")


@dataclass
class DevicePairing:
    """設備配對記錄"""
    id: str
    device_type: DeviceType
    device_name: str
    device_info: Dict[str, Any]
    device_token: str = ""  # 不持久化，只在確認時產生
    token_hash: str = ""
    created_at: float = 0
    expires_at: float = 0
    status: PairingStatus = PairingStatus.PENDING
    last_seen: float = 0


def main():
    """測試"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pairing = NodePairing(Path(tmpdir) / "nodes")
        
        # 初始化配對
        result = pairing.initiate_pairing(
            DeviceType.ANDROID,
            "My Phone",
            {"model": "Pixel 7", "os_version": "14"}
        )
        print(f"Pairing code: {result['pairing_code']}")
        print(f"Request ID: {result['request_id']}")
        
        # 確認配對
        confirm = pairing.confirm_pairing(result['request_id'], result['pairing_code'])
        if confirm:
            print(f"Device paired! Token: {confirm['device_token'][:20]}...")
            
            # 驗證令牌
            device = pairing.verify_token(confirm['device_token'])
            if device:
                print(f"Token verified for: {device.device_name}")
        
        # 列出設備
        print("\n=== Paired Devices ===")
        for device in pairing.list_devices():
            print(f"  {device['device_name']} ({device['device_type']}) - {device['status']}")


if __name__ == '__main__':
    main()
