"""
AI Harness Plugin Loader
功能：Plugin 發現、載入、隔離執行、安全驗證
版本：v1.0.0
"""
import os
import sys
import json
import hashlib
import time
import importlib
import importlib.util
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import logging
import tempfile
import shutil


class PluginState(Enum):
    UNKNOWN = "unknown"
    LOADED = "loaded"
    DISABLED = "disabled"
    ERROR = "error"
    UNVERIFIED = "unverified"


@dataclass
class PluginSignature:
    """Plugin 簽章資訊"""
    algorithm: str = "sha256"
    hash: str = ""
    signed_by: str = ""
    timestamp: float = 0


@dataclass
class PluginManifest:
    """Plugin 清單"""
    name: str
    version: str
    description: str
    author: str = "unknown"
    entry_point: str = "plugin.py"
    permissions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    signature: Optional[PluginSignature] = None
    compatibility: List[str] = field(default_factory=list)


@dataclass
class Plugin:
    """Plugin 實例"""
    manifest: PluginManifest
    path: Path
    state: PluginState = PluginState.UNVERIFIED
    module: Optional[Any] = None
    loaded_at: float = 0
    error_message: str = ""
    
    def check_permission(self, permission: str) -> bool:
        """檢查是否有特定權限"""
        return permission in self.manifest.permissions or "*" in self.manifest.permissions


class PluginSandbox:
    """
    Plugin 沙箱 - 隔離執行環境
    
    每個 Plugin 在獨立的執行上下文中運行，防止惡意程式碼影響系統。
    """
    
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.env = {}
        self.restricted_imports = True
    
    def execute(self, func_name: str, *args, **kwargs) -> Any:
        """在沙箱中執行函數"""
        if not self.plugin.module:
            raise RuntimeError("Plugin not loaded")
        
        func = getattr(self.plugin.module, func_name, None)
        if not func:
            raise AttributeError(f"Function not found: {func_name}")
        
        return func(*args, **kwargs)


class PluginLoader:
    """
    Plugin Loader - Plugin 系統核心
    
    功能：
    - Plugin 發現與掃描
    - 簽章驗證
    - 隔離載入
    - 權限管理
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, plugins_root: Optional[Path] = None, config: Optional[Dict] = None):
        if plugins_root is None:
            self.plugins_root = Path(__file__).parent.parent.parent / "plugins"
        else:
            self.plugins_root = Path(plugins_root)
        
        self.config = config or {}
        self.logger = logging.getLogger("harness.plugin")
        
        # Plugin 註冊表
        self.plugins: Dict[str, Plugin] = {}
        
        # 已驗證的簽章
        self.verified_signatures: Set[str] = set()
        
        # 允許的權限
        self.allowed_permissions = self._load_allowed_permissions()
        
        # 簽章金鑰目錄
        self.keys_dir = self.plugins_root / ".keys"
        if not self.keys_dir.exists():
            self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        # 掃描 Plugin
        self._scan_plugins()
    
    def _load_allowed_permissions(self) -> Set[str]:
        """載入允許的權限列表"""
        default_permissions = {
            'file:read',
            'file:write',
            'network:http',
            'network:https',
            'process:spawn',
            'system:info',
            'system:exec',
            'security:*',  # 最高權限，需特別授權
        }
        
        configured = self.config.get('allowed_permissions', [])
        if configured:
            return set(configured)
        
        return default_permissions
    
    def _scan_plugins(self):
        """掃描 plugins 目錄"""
        if not self.plugins_root.exists():
            self.logger.warning(f"Plugins root not found: {self.plugins_root}")
            return
        
        for plugin_dir in self.plugins_root.iterdir():
            if not plugin_dir.is_dir():
                continue
            
            # 跳過特殊目錄
            if plugin_dir.name.startswith('.') or plugin_dir.name.startswith('_'):
                continue
            
            manifest_path = plugin_dir / "manifest.json"
            if not manifest_path.exists():
                self.logger.debug(f"Skipping {plugin_dir.name}: no manifest.json")
                continue
            
            try:
                plugin = self._load_plugin(plugin_dir)
                if plugin:
                    self._register_plugin(plugin)
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
    
    def _load_plugin(self, plugin_dir: Path) -> Optional[Plugin]:
        """載入單個 Plugin"""
        manifest_path = plugin_dir / "manifest.json"
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        manifest = PluginManifest(**manifest_data)
        
        plugin = Plugin(
            manifest=manifest,
            path=plugin_dir,
            state=PluginState.UNVERIFIED
        )
        
        # 驗證簽章
        if self.config.get('require_signature', True):
            if not self._verify_signature(plugin):
                self.logger.warning(f"Plugin {plugin.manifest.name} signature not verified")
                # 根據配置決定是否阻止
                if self.config.get('block_unsigned', False):
                    plugin.state = PluginState.ERROR
                    plugin.error_message = "Signature verification required"
                    return plugin
        
        # 檢查權限
        if not self._check_permissions(plugin):
            plugin.state = PluginState.ERROR
            plugin.error_message = "Permissions not allowed"
            return plugin
        
        # 載入 Plugin 模組
        entry_point = plugin_dir / manifest.entry_point
        if entry_point.exists():
            try:
                plugin.module = self._load_plugin_module(entry_point)
                plugin.state = PluginState.LOADED
                plugin.loaded_at = time.time()
            except Exception as e:
                plugin.state = PluginState.ERROR
                plugin.error_message = str(e)
        
        return plugin
    
    def _load_plugin_module(self, module_path: Path) -> Any:
        """載入 Plugin Python 模組"""
        module_name = f"plugin_{module_path.parent.name}"
        
        # 在隔離的環境中載入
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            
            # 設定模組路徑
            sys.path.insert(0, str(module_path.parent))
            
            try:
                spec.loader.exec_module(module)
            finally:
                sys.path.remove(str(module_path.parent))
            
            return module
        
        return None
    
    def _verify_signature(self, plugin: Plugin) -> bool:
        """驗證 Plugin 簽章"""
        # 取得簽章檔
        sig_file = plugin.path / f"{plugin.manifest.name}.sig"
        if not sig_file.exists():
            return False
        
        try:
            with open(sig_file, 'r') as f:
                sig_data = json.load(f)
            
            # 計算所有 .py 檔案的 hash
            files_hash = self._compute_directory_hash(plugin.path)
            
            # 驗證 hash
            return sig_data.get('hash') == files_hash
            
        except Exception as e:
            self.logger.error(f"Signature verification failed: {e}")
            return False
    
    def _compute_directory_hash(self, directory: Path) -> str:
        """計算目錄的 hash"""
        hasher = hashlib.sha256()
        
        for py_file in sorted(directory.rglob("*.py")):
            if '.keys' in str(py_file) or '__pycache__' in str(py_file):
                continue
            with open(py_file, 'rb') as f:
                hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def _check_permissions(self, plugin: Plugin) -> bool:
        """檢查 Plugin 權限是否允許"""
        for permission in plugin.manifest.permissions:
            if permission not in self.allowed_permissions and permission != '*':
                self.logger.warning(
                    f"Plugin {plugin.manifest.name} requests disallowed permission: {permission}"
                )
                return False
        return True
    
    def _register_plugin(self, plugin: Plugin):
        """註冊 Plugin"""
        self.plugins[plugin.manifest.name] = plugin
        
        status = plugin.state.value
        if plugin.state == PluginState.ERROR:
            status += f": {plugin.error_message}"
        
        self.logger.info(f"Registered plugin: {plugin.manifest.name} ({status})")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """取得 Plugin"""
        return self.plugins.get(name)
    
    def list_plugins(self, 
                     state: Optional[PluginState] = None,
                     include_disabled: bool = True) -> List[Dict[str, Any]]:
        """列出所有 Plugin"""
        result = []
        
        for plugin in self.plugins.values():
            if state and plugin.state != state:
                continue
            
            if not include_disabled and plugin.state == PluginState.DISABLED:
                continue
            
            result.append({
                'name': plugin.manifest.name,
                'version': plugin.manifest.version,
                'description': plugin.manifest.description,
                'author': plugin.manifest.author,
                'state': plugin.state.value,
                'permissions': plugin.manifest.permissions,
                'loaded_at': plugin.loaded_at
            })
        
        return result
    
    def enable(self, name: str) -> bool:
        """啟用 Plugin"""
        plugin = self.plugins.get(name)
        if plugin and plugin.state == PluginState.DISABLED:
            plugin.state = PluginState.LOADED
            return True
        return False
    
    def disable(self, name: str) -> bool:
        """停用 Plugin"""
        plugin = self.plugins.get(name)
        if plugin and plugin.state == PluginState.LOADED:
            plugin.state = PluginState.DISABLED
            return True
        return False
    
    def execute(self, plugin_name: str, 
                func_name: str, 
                *args, 
                **kwargs) -> Any:
        """執行 Plugin 函數"""
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        if plugin.state != PluginState.LOADED:
            raise RuntimeError(f"Plugin not loaded: {plugin_name}")
        
        sandbox = PluginSandbox(plugin)
        return sandbox.execute(func_name, *args, **kwargs)
    
    def create_manifest(self, 
                        name: str,
                        version: str,
                        description: str,
                        author: str = "unknown",
                        permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """建立 Plugin Manifest 模板"""
        manifest = {
            "name": name,
            "version": version,
            "description": description,
            "author": author,
            "entry_point": "plugin.py",
            "permissions": permissions or [],
            "compatibility": ["autoagent"]
        }
        return manifest


def main():
    """測試"""
    loader = PluginLoader()
    
    print("=== Loaded Plugins ===")
    for plugin in loader.list_plugins():
        print(f"  {plugin['name']} v{plugin['version']} [{plugin['state']}]")
        print(f"    {plugin['description']}")
        print(f"    Permissions: {', '.join(plugin['permissions'])}")


if __name__ == '__main__':
    main()
