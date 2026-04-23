"""
AI Harness Messages - 統一訊息介面
功能：跨平台訊息發送、頻道路由、格式化
版本：v1.0.0
"""
import json
import time
import uuid
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging


class MessageChannel(Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    WECHAT = "wechat"
    SIGNAL = "signal"
    SLACK = "slack"
    LINE = "line"
    WEBCHAT = "webchat"
    INTERNAL = "internal"


class MessagePriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Message:
    """訊息資料結構"""
    msg_id: str
    channel: MessageChannel
    content: str
    to: str  # 目標（channel/user/group）
    from_: Optional[str] = field(default=None, metadata={'alias': 'from'})
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 選項
    reply_to: Optional[str] = None
    media: Optional[Dict[str, Any]] = None  # {"type": "image", "url": "..."}
    buttons: Optional[List[Dict[str, str]]] = None  # [{"text": "...", "action": "..."}]
    silent: bool = False
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.msg_id:
            self.msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        if self.from_ is None:
            self.from_ = "harness"


@dataclass
class MessageResult:
    """訊息發送結果"""
    msg_id: str
    success: bool
    channel: str
    sent_at: float = 0
    error: Optional[str] = None
    response: Optional[Dict[str, Any]] = None


class MessageRouter:
    """
    Message Router - 統一訊息路由
    
    功能：
    - 跨平台訊息發送
    - 頻道適配器管理
    - 訊息格式化
    - 發送歷史
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger("harness.messages")
        
        # 頻道適配器
        self.adapters: Dict[MessageChannel, 'ChannelAdapter'] = {}
        
        # 發送歷史
        self.history: List[MessageResult] = []
        self.max_history = 1000
        
        # 初始化適配器
        self._init_adapters()
    
    def _init_adapters(self):
        """初始化頻道適配器"""
        # 延遲載入，避免循環依賴
        try:
            # 嘗試載入各平台適配器
            # 這些適配器應該由各平台的 skill/plugin 提供
            pass
        except Exception as e:
            self.logger.warning(f"Failed to init adapters: {e}")
    
    def register_adapter(self, channel: MessageChannel, adapter: 'ChannelAdapter'):
        """註冊頻道適配器"""
        self.adapters[channel] = adapter
        self.logger.info(f"Registered adapter for {channel.value}")
    
    def send(self,
             content: str,
             to: str,
             channel: MessageChannel = MessageChannel.INTERNAL,
             priority: MessagePriority = MessagePriority.NORMAL,
             **kwargs) -> MessageResult:
        """
        發送訊息
        
        Args:
            content: 訊息內容
            to: 目標
            channel: 頻道
            priority: 優先級
            **kwargs: 其他選項
        
        Returns:
            MessageResult 發送結果
        """
        msg = Message(
            msg_id=f"msg_{uuid.uuid4().hex[:12]}",
            channel=channel,
            content=content,
            to=to,
            priority=priority,
            **kwargs
        )
        
        return self._send_message(msg)
    
    def _send_message(self, msg: Message) -> MessageResult:
        """實際發送訊息"""
        result = MessageResult(
            msg_id=msg.msg_id,
            success=True,
            channel=msg.channel.value if hasattr(msg.channel, 'value') else str(msg.channel),
            sent_at=time.time()
        )
        
        adapter = self.adapters.get(msg.channel)
        
        if not adapter:
            # 沒有適配器，使用內部處理
            result.success = True
            result.response = {"status": "queued", "internal": True}
            self.logger.info(f"Message {msg.msg_id} queued (no adapter for {msg.channel.value})")
        else:
            try:
                response = adapter.send(msg)
                result.success = True
                result.response = response
            except Exception as e:
                result.success = False
                result.error = str(e)
                self.logger.error(f"Failed to send message {msg.msg_id}: {e}")
        
        # 記錄歷史
        self.history.append(result)
        
        # 限制歷史長度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        return result
    
    def send_to_user(self, user_id: str, content: str, **kwargs) -> MessageResult:
        """發送訊息給使用者"""
        return self.send(content, to=user_id, channel=MessageChannel.INTERNAL, **kwargs)
    
    def broadcast(self,
                  content: str,
                  targets: List[str],
                  channel: MessageChannel = MessageChannel.INTERNAL) -> List[MessageResult]:
        """廣播訊息"""
        results = []
        
        for target in targets:
            result = self.send(content, to=target, channel=channel)
            results.append(result)
        
        return results
    
    def format_message(self, 
                      msg: str,
                      template: str = "default",
                      **kwargs) -> str:
        """
        格式化訊息
        
        Args:
            msg: 訊息內容
            template: 模板名稱
            **kwargs: 模板變數
        """
        templates = {
            "default": "{msg}",
            "bold": "*{msg}*",
            "code": "```\n{msg}\n```",
            "alert": "🚨 {msg}",
            "success": "✅ {msg}",
            "info": "ℹ️ {msg}",
            "warning": "⚠️ {msg}",
            "error": "❌ {msg}",
        }
        
        fmt = templates.get(template, templates["default"])
        return fmt.format(msg=msg, **kwargs)
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """列出可用頻道"""
        return [
            {
                'channel': ch.value,
                'adapter': 'registered' if ch in self.adapters else 'not_registered'
            }
            for ch in MessageChannel
        ]
    
    def get_history(self, 
                   limit: int = 50,
                   channel: Optional[MessageChannel] = None,
                   success_only: bool = False) -> List[Dict[str, Any]]:
        """取得發送歷史"""
        history = self.history[-limit:]
        
        history = self.history[-limit:]
        
        if channel:
            channel_val = channel.value if hasattr(channel, 'value') else str(channel)
            history = [r for r in history if r.channel == channel_val]
        
        if success_only:
            history = [r for r in history if r.success]
        
        return [asdict(r) for r in history]


class ChannelAdapter:
    """頻道適配器基類"""
    
    def send(self, msg: Message) -> Dict[str, Any]:
        """發送訊息"""
        raise NotImplementedError
    
    def receive(self) -> List[Message]:
        """接收訊息"""
        raise NotImplementedError


def main():
    """測試"""
    router = MessageRouter()
    
    # 列出頻道
    print("=== Available Channels ===")
    for ch in router.list_channels():
        print(f"  {ch['channel']}: {ch['adapter']}")
    
    # 發送測試訊息
    result = router.send("測試訊息", to="user123")
    print(f"\nSend result: {'✓' if result.success else '✗'} {result.msg_id}")
    
    # 格式化
    print("\n=== Formatted Messages ===")
    for template in ["success", "error", "warning", "info"]:
        print(f"  {template}: {router.format_message('測試內容', template)}")


if __name__ == '__main__':
    main()
