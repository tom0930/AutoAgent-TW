"""
AI Harness Skill Engine
功能：Skill 發現、載入、執行、意圖路由
版本：v1.0.0
"""
import os
import re
import json
import time
import hashlib
import importlib
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import logging


class TriggerMatch(Enum):
    EXACT = "exact"       # 精確匹配
    CONTAINS = "contains" # 包含匹配
    FUZZY = "fuzzy"       # 模糊匹配
    REGEX = "regex"       # 正則表達式


@dataclass
class SkillMetadata:
    """Skill 中繼資料"""
    name: str
    version: str
    description: str
    author: str = "unknown"
    triggers: List[str] = field(default_factory=list)
    compatibility: List[str] = field(default_factory=list)
    security_level: str = "normal"  # "normal", "elevated", "critical"
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Skill:
    """Skill 實例"""
    metadata: SkillMetadata
    path: Path
    module: Optional[Any] = None
    enabled: bool = True
    loaded_at: float = 0
    execution_count: int = 0
    last_executed: float = 0
    
    def trigger(self, text: str) -> Optional[TriggerMatch]:
        """檢查文字是否觸發此 Skill"""
        text_lower = text.lower()
        
        for trigger in self.metadata.triggers:
            trigger_lower = trigger.lower()
            
            # 精確匹配
            if trigger_lower == text_lower:
                return TriggerMatch.EXACT
            
            # 包含匹配
            if trigger_lower in text_lower:
                return TriggerMatch.CONTAINS
            
            # 正則匹配
            if trigger_lower.startswith('^') or trigger_lower.endswith('$'):
                if re.search(trigger_lower, text, re.IGNORECASE):
                    return TriggerMatch.REGEX
        
        return None


@dataclass
class SkillResult:
    """Skill 執行結果"""
    skill_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillEngine:
    """
    Skill Engine - AI Harness 的核心擴展系統
    
    功能：
    - 自動發現 skills 目錄下的 Skill
    - 意圖路由（根據觸發關鍵字）
    - Skill 執行環境隔離
    - 安全驗證
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, skills_root: Optional[Path] = None, config: Optional[Dict] = None):
        # 預設路徑
        if skills_root is None:
            # 從專案根目錄計算
            self.skills_root = Path(__file__).parent.parent.parent / "skills"
        else:
            self.skills_root = Path(skills_root)
        
        self.config = config or {}
        self.logger = logging.getLogger("harness.skill")
        
        # 已註冊的 Skills
        self.skills: Dict[str, Skill] = {}
        self.skills_by_trigger: Dict[str, str] = {}  # trigger -> skill_name
        
        # 執行鉤子
        self.pre_execute_hooks: List[Callable] = []
        self.post_execute_hooks: List[Callable] = []
        
        # 安全白名單
        self._load_security_config()
        
        # 初始化時自動掃描
        self._scan_skills()
    
    def _load_security_config(self):
        """載入安全配置"""
        # 從 harness.toml 讀取
        harness_config = self.config.get('security', {})
        
        self.allowed_imports: Set[str] = set(harness_config.get(
            'allowed_imports',
            ['os', 'sys', 'pathlib', 'json', 'time', 'datetime', 're', 'math']
        ))
        
        self.max_execution_time_ms: int = harness_config.get(
            'max_execution_time_ms', 30000
        )
        
        self.elevated_skills: Set[str] = set(harness_config.get(
            'elevated_skills', []
        ))
    
    def _scan_skills(self):
        """掃描 skills 目錄，發現所有 Skill"""
        if not self.skills_root.exists():
            self.logger.warning(f"Skills root not found: {self.skills_root}")
            return
        
        self.logger.info(f"Scanning skills from: {self.skills_root}")
        
        for skill_dir in self.skills_root.iterdir():
            if not skill_dir.is_dir():
                continue
            
            # 跳過特殊目錄
            if skill_dir.name.startswith('.') or skill_dir.name.startswith('_'):
                continue
            
            # 跳過 examples 等輔助目錄
            if skill_dir.name in ('examples', 'scripts'):
                continue
            
            # 嘗試載入 SKILL.md
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                self.logger.debug(f"Skipping {skill_dir.name}: no SKILL.md")
                continue
            
            try:
                skill = self._load_skill(skill_dir)
                if skill:
                    self._register_skill(skill)
            except Exception as e:
                self.logger.error(f"Failed to load skill {skill_dir.name}: {e}")
    
    def _load_skill(self, skill_dir: Path) -> Optional[Skill]:
        """載入單個 Skill"""
        # 解析 SKILL.md
        metadata = self._parse_skill_md(skill_dir / "SKILL.md")
        if not metadata:
            return None
        
        skill = Skill(
            metadata=metadata,
            path=skill_dir,
            loaded_at=time.time()
        )
        
        # 嘗試載入主要模組
        main_py = skill_dir / "skill.py"
        if main_py.exists():
            try:
                module = self._load_skill_module(main_py)
                skill.module = module
            except Exception as e:
                self.logger.warning(f"Could not load module for {skill_dir.name}: {e}")
        
        return skill
    
    def _parse_skill_md(self, md_path: Path) -> Optional[SkillMetadata]:
        """解析 SKILL.md"""
        try:
            content = md_path.read_text(encoding='utf-8')
            
            # 簡單的 front-matter 解析
            metadata = {}
            
            # 解析 YAML front-matter
            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    yaml_content = content[3:end].strip()
                    # 簡單解析 key: value
                    for line in yaml_content.split('\n'):
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().strip('-').strip()
                            value = value.strip()
                            
                            if key == 'triggers':
                                # 解析列表
                                triggers = []
                                # 簡單處理：假設是 JSON 陣列
                                if value.startswith('['):
                                    try:
                                        triggers = json.loads(value)
                                    except:
                                        triggers = [t.strip().strip('"').strip("'") 
                                                   for t in value.strip('[]').split(',')]
                                else:
                                    triggers = [value]
                                metadata[key] = triggers
                            elif key in ('name', 'version', 'description', 'author', 
                                        'compatibility', 'security_level'):
                                metadata[key] = value
                            elif key in ('dependencies',):
                                if value.startswith('['):
                                    try:
                                        metadata[key] = json.loads(value)
                                    except:
                                        metadata[key] = []
                                else:
                                    metadata[key] = []
            
            # 從內容中提取資訊
            if 'name' not in metadata:
                # 嘗試從檔名取得
                metadata['name'] = md_path.parent.name
            
            if 'description' not in metadata:
                # 嘗試從內容取得
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        metadata['description'] = line[2:].strip()
                        break
            
            # 確保必要欄位
            required = ['name', 'version']
            for key in required:
                if key not in metadata:
                    metadata[key] = '1.0.0'
            
            # 設定預設值
            metadata.setdefault('version', '1.0.0')
            metadata.setdefault('author', 'unknown')
            metadata.setdefault('triggers', [])
            metadata.setdefault('compatibility', ['autoagent', 'openclaw'])
            metadata.setdefault('security_level', 'normal')
            metadata.setdefault('dependencies', [])
            
            return SkillMetadata(**metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to parse SKILL.md: {e}")
            return None
    
    def _load_skill_module(self, module_path: Path) -> Any:
        """載入 Skill Python 模組"""
        module_name = f"skill_{module_path.parent.name}"
        
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        
        return None
    
    def _register_skill(self, skill: Skill):
        """註冊 Skill"""
        self.skills[skill.metadata.name] = skill
        self.logger.info(f"Registered skill: {skill.metadata.name}")
        
        # 建立觸發映射
        for trigger in skill.metadata.triggers:
            self.skills_by_trigger[trigger.lower()] = skill.metadata.name
    
    def find_skill(self, text: str) -> Optional[Skill]:
        """根據輸入文字找到觸發的 Skill"""
        text_lower = text.lower()
        
        # 1. 精確觸發查找
        for trigger, skill_name in self.skills_by_trigger.items():
            if trigger == text_lower:
                return self.skills.get(skill_name)
        
        # 2. 包含匹配
        for trigger, skill_name in self.skills_by_trigger.items():
            if trigger in text_lower or text_lower in trigger:
                return self.skills.get(skill_name)
        
        # 3. 遍歷所有 Skill 檢查正則
        for skill in self.skills.values():
            if skill.trigger(text):
                return skill
        
        return None
    
    def execute(self, skill_name: str, 
                params: Optional[Dict[str, Any]] = None,
                context: Optional[Dict[str, Any]] = None) -> SkillResult:
        """
        執行 Skill
        
        Args:
            skill_name: Skill 名稱
            params: 執行參數
            context: 執行上下文
        
        Returns:
            SkillResult 執行結果
        """
        start_time = time.time()
        
        skill = self.skills.get(skill_name)
        if not skill:
            return SkillResult(
                skill_name=skill_name,
                success=False,
                error=f"Skill not found: {skill_name}"
            )
        
        if not skill.enabled:
            return SkillResult(
                skill_name=skill_name,
                success=False,
                error=f"Skill disabled: {skill_name}"
            )
        
        # 安全檢查
        if skill.metadata.security_level == "critical":
            if skill_name not in self.elevated_skills:
                return SkillResult(
                    skill_name=skill_name,
                    success=False,
                    error="Critical skill requires elevated permissions"
                )
        
        # 執行前置鉤子
        for hook in self.pre_execute_hooks:
            try:
                hook(skill, params, context)
            except Exception as e:
                self.logger.warning(f"Pre-execute hook failed: {e}")
        
        # 執行 Skill
        try:
            result = self._execute_skill(skill, params or {}, context or {})
            
            execution_time = (time.time() - start_time) * 1000
            
            # 更新統計
            skill.execution_count += 1
            skill.last_executed = time.time()
            
            return SkillResult(
                skill_name=skill_name,
                success=True,
                result=result,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Skill execution failed: {e}")
            return SkillResult(
                skill_name=skill_name,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
        
        finally:
            # 執行後置鉤子
            for hook in self.post_execute_hooks:
                try:
                    hook(skill, params, context)
                except Exception as e:
                    self.logger.warning(f"Post-execute hook failed: {e}")
    
    def _execute_skill(self, skill: Skill, 
                      params: Dict[str, Any],
                      context: Dict[str, Any]) -> Any:
        """實際執行 Skill"""
        if skill.module and hasattr(skill.module, 'execute'):
            # 呼叫模組的 execute 函數
            return skill.module.execute(params, context)
        elif skill.module and hasattr(skill.module, 'run'):
            return skill.module.run(params, context)
        else:
            # 沒有可執行模組
            return {"status": "ok", "message": f"Skill {skill.metadata.name} loaded but no executable found"}
    
    def list_skills(self, 
                   enabled_only: bool = True,
                   security_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有 Skill"""
        skills = []
        
        for skill in self.skills.values():
            if enabled_only and not skill.enabled:
                continue
            
            if security_level and skill.metadata.security_level != security_level:
                continue
            
            skills.append({
                'name': skill.metadata.name,
                'version': skill.metadata.version,
                'description': skill.metadata.description,
                'triggers': skill.metadata.triggers,
                'enabled': skill.enabled,
                'execution_count': skill.execution_count,
                'last_executed': skill.last_executed
            })
        
        return skills
    
    def enable(self, skill_name: str) -> bool:
        """啟用 Skill"""
        skill = self.skills.get(skill_name)
        if skill:
            skill.enabled = True
            return True
        return False
    
    def disable(self, skill_name: str) -> bool:
        """停用 Skill"""
        skill = self.skills.get(skill_name)
        if skill:
            skill.enabled = False
            return True
        return False
    
    def reload(self, skill_name: Optional[str] = None):
        """重新載入 Skill"""
        if skill_name:
            skill = self.skills.get(skill_name)
            if skill:
                self._load_skill(skill.path)  # type: ignore[arg-type]
        else:
            # 重新掃描所有
            self._scan_skills()


def main():
    """測試"""
    engine = SkillEngine()
    
    print("=== Available Skills ===")
    for skill in engine.list_skills():
        print(f"  {skill['name']}: {skill['description']}")
        print(f"    Triggers: {', '.join(skill['triggers'])}")
    
    print("\n=== Testing Skill Detection ===")
    test_inputs = [
        "自動化任務",
        "帮我浏览网页",
        "schedule something",
        "random text"
    ]
    
    for text in test_inputs:
        skill = engine.find_skill(text)
        if skill:
            print(f"  '{text}' -> {skill.metadata.name}")
        else:
            print(f"  '{text}' -> No match")


if __name__ == '__main__':
    main()
