# AI Harness Skill Engine 使用指南

## 概述

Skill Engine 是 AI Harness 的核心擴展系統，允許以插件形式新增功能。

## 快速開始

```python
from src.core.skill import SkillEngine

# 建立 Engine
engine = SkillEngine()

# 列出所有 Skill
for skill in engine.list_skills():
    print(f"{skill['name']}: {skill['description']}")

# 執行 Skill
result = engine.execute("skill-name", params={"key": "value"})
```

## 建立新 Skill

### 1. 建立目錄結構

```
skills/
└── my-skill/
    ├── SKILL.md          # 必要
    ├── skill.py          # 可選
    └── assets/           # 可選
```

### 2. 撰寫 SKILL.md

```markdown
# My Skill

- **name**: my-skill
- **version**: 1.0.0
- **description**: 這是我的 Skill
- **triggers**: ["關鍵字1", "關鍵字2"]

## 功能說明

描述這個 Skill 的功能。

## 使用方式

1. 觸發方式
2. 參數說明
```

### 3. 實作 skill.py

```python
def execute(params, context):
    # 處理邏輯
    return {"status": "ok", "result": "..."}
```

## 觸發機制

| 匹配類型 | 說明 | 範例 |
|---------|------|------|
| EXACT | 完全匹配 | `"自動化"` 完全等於觸發字 |
| CONTAINS | 包含匹配 | `"自動化任務"` 包含 `"自動化"` |
| REGEX | 正則匹配 | `"^自動化.*"` 匹配正則表達式 |

## 安全等級

| 等級 | 說明 | 需要的權限 |
|------|------|-----------|
| normal | 普通 Skill | 無特殊要求 |
| elevated | 提升權限 | 需在配置中明確授權 |
| critical | 關鍵操作 | 需最高權限 |

---

*最後更新：2026-04-23*
