# AI Harness Skill Engine

## 概述

Skill Engine 是 AI Harness 的核心擴展系統，允許使用者以插件形式新增功能。

## 核心概念

### Skill 基本結構

```
skill-name/
├── SKILL.md              # Skill 描述檔
├── scripts/              # 輔助腳本
├── prompts/              # 提示詞模板
└── assets/               # 資源檔
```

### SKILL.md 必填欄位

| 欄位 | 說明 | 範例 |
|------|------|------|
| name | 唯一識別名稱 | `browser-automation` |
| version | 版本號 | `1.0.0` |
| description | 功能描述 | `自動化瀏覽器操作` |
| triggers | 觸發關鍵字 | `["自動化", "browser"]` |

## 觸發機制

Skill 透過關鍵字觸發。當使用者的輸入包含觸發關鍵字時，Engine 會：

1. 解析意圖
2. 載入對應 Skill
3. 執行 Skill 邏輯
4. 返回結果

## 安全模型

- 所有 Skill 在隔離環境執行
- 敏感操作需要明確授權
- 網路請求需在白名單中

## 開發指南

### 建立新 Skill

1. 在 `skills/` 下建立目錄
2. 撰寫 `SKILL.md`
3. 實作核心邏輯
4. 註冊到 `skills/registry.json`
5. 提交 Git commit

---

*最後更新：2026-04-23*
