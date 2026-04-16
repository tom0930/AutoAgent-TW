from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field

class FileSystemPermissions(BaseModel):
    read: List[str] = Field(default_factory=list)
    write: List[str] = Field(default_factory=list)

class SystemPermissions(BaseModel):
    run: List[str] = Field(default_factory=list)

class GUIPermissions(BaseModel):
    click: bool = False
    type: bool = False
    capture: bool = False
    mouse_move: bool = False

class NetworkPermissions(BaseModel):
    allow_domains: List[str] = Field(default_factory=list)
    deny_all: bool = False

class SkillPermissions(BaseModel):
    fs: Optional[FileSystemPermissions] = None
    system: Optional[SystemPermissions] = None
    gui: Optional[GUIPermissions] = None
    network: Optional[Union[NetworkPermissions, bool]] = False
    tools: List[str] = Field(default_factory=list)

class SkillManifest(BaseModel):
    """
    Skill Package v2 Manifest Schema (AutoSkills Phase 2 - Task 1.1).
    """
    name: str
    version: str
    description: str
    author: Optional[str] = "unknown"
    entry: str = "SKILL.md"
    
    # IRA 5-Level Risk Mapping
    risk_level: int = Field(default=3, ge=1, le=5)
    
    # Permissions
    permissions: SkillPermissions = Field(default_factory=SkillPermissions)
    
    # Dependency & Evolution
    requires: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    auto_evolve: bool = False
    
    # Metadata
    ui_integration: Optional[str] = None
    
if __name__ == "__main__":
    # Test valid manifest
    sample = {
        "name": "windows-gui-automation",
        "version": "2.1.0",
        "description": "Native Windows GUI control",
        "risk_level": 4,
        "permissions": {
            "gui": {"click": True, "type": True},
            "system": {"run": ["powershell"]}
        },
        "auto_evolve": True
    }
    
    try:
        manifest = SkillManifest(**sample)
        print(f"Success: Validated manifest for '{manifest.name}' v{manifest.version}")
        print(f"JSON Output: {manifest.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Validation Failed: {str(e)}")
