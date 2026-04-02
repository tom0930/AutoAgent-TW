---
description: Pipeline & Task Chaining / 組合任務鏈與管線執行。
---

# AutoAgent-TW Chain Workflow

## Purpose
基於 v1.6.0 透明度升級計畫，提供可組合的任務鏈 (Pipelines) 與條件執行邏輯。

## Usage
`/aa-chain "<命令1> [運算子] <命令2> ..."`

## Operators (運算子)
| 運算子 | 描述 |
|:---:|:---|
| `&&` | 只有上一步 **成功** (Exit Code 0) 才執行下一步。 |
| `\|\|` | 只有上一步 **失敗** 才執行下一步 (用於錯誤恢復)。 |
| `\|` | 兩步都執行，不論成功與否。 |

## Examples (範例)

### 1. 成功連續執行
`/aa-chain "git pull && aa-progress"`
- 如果 `git pull` 成功，則查看更新後的進度。

### 2. 失敗自動修復
`/aa-chain "aa-qa || aa-fix"`
- 如果 `aa-qa` 失敗，立即啟動修復程序。

### 3. 多階段全自動
`/aa-chain "git pull && aa-qa || aa-fix && aa-qa && git push"`
- 如果 QA 失敗，啟動修復，修復成功後再次 QA，最後才提交代碼。

## Usage Notes
- 每個步驟都會在透明度儀表板中獨立顯示。
- 命令中若含有特殊字元 (如 `&`, `|`)，建議用雙引號包裹。
- 支援所有 `aa-` 系列指令及標準 `python`/`git` 指令。
