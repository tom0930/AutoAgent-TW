# AI Harness Skills

本目錄存放 AI Harness 的 Skill 擴展套件。

## 目錄結構

```
skills/
├── SKILL.md              # 本文件
├── examples/
│   ├── automation/       # 自動化相關 Skill 範例
│   ├── web/              # 網頁相關 Skill 範例
│   └── system/           # 系統相關 Skill 範例
└── registry.json         # 已註冊的 Skill 清單
```

## Skill 結構

每個 Skill 應包含：

```
skill-name/
├── SKILL.md              # 必要：Skill 描述檔
├── scripts/              # 輔助腳本（如有）
├── prompts/              # 提示詞模板（如有）
└── assets/               # 資源檔（如有）
```

## SKILL.md 格式

```markdown
# Skill 名稱

- **name**: skill-name
- **version**: 1.0.0
- **description**: 簡短描述
- **author**: 開發者
- **triggers**: ["關鍵字1", "關鍵字2"]
- **compatibility**: ["openclaw", "autoagent"]

## 功能說明

詳細描述...

## 使用方式

1. 觸發方式
2. 參數說明
3. 回傳格式

## 實作

（實作指引或腳本）

## 安全考量

（如有）
```

## 觸發關鍵字

| 關鍵字 | Skill |
|--------|-------|
| 自動化 | automation |
| 瀏覽器 | browser |
| 檔案 | file |
| 排程 | cron |
| 郵件 | email |
| 天氣 | weather |
| 搜尋 | search |

## 貢獻

歡迎貢獻新的 Skill！請確保：

1. 完整的 SKILL.md 文件
2. 足夠的錯誤處理
3. 安全考量說明
4. 測試覆蓋

---

*最後更新：2026-04-23*
