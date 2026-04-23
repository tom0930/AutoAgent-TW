"""
AI Harness Gateway 測試
"""
import pytest
import time
import tempfile
from pathlib import Path
import sys

# 確保可以匯入模組
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.harness_gateway import HarnessGateway


class TestHarnessGateway:
    """Gateway 測試"""
    
    @pytest.fixture
    def temp_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_gateway_init(self, temp_workspace):
        """測試 Gateway 初始化"""
        gateway = HarnessGateway(str(temp_workspace))
        assert gateway is not None
        assert gateway.VERSION == "1.0.0"
    
    def test_gateway_start_stop(self, temp_workspace):
        """測試啟動和停止"""
        gateway = HarnessGateway(str(temp_workspace))
        
        # 啟動
        result = gateway.start()
        assert result is True
        assert gateway.running is True
        
        # 停止
        gateway.stop()
        assert gateway.running is False
    
    def test_gateway_status(self, temp_workspace):
        """測試狀態查詢"""
        gateway = HarnessGateway(str(temp_workspace))
        
        # 未啟動時
        status = gateway.status()
        assert status['running'] is False
        
        # 啟動後
        gateway.start()
        status = gateway.status()
        assert status['running'] is True
        assert status['version'] == "1.0.0"
        assert 'services' in status
        
        gateway.stop()
    
    def test_gateway_restart(self, temp_workspace):
        """測試重啟"""
        gateway = HarnessGateway(str(temp_workspace))
        
        gateway.start()
        assert gateway.running is True
        
        result = gateway.restart()
        assert result is True
        assert gateway.running is True
        
        gateway.stop()
    
    def test_multiple_start(self, temp_workspace):
        """測試重複啟動"""
        gateway = HarnessGateway(str(temp_workspace))
        
        gateway.start()
        result = gateway.start()  # 應該失敗
        assert result is False
        
        gateway.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
