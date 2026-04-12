---
description: "AI Memory System (MemPalace) / 持久化大腦記憶系統：跨對話檢索決策、架構與歷史背景。"
---

# AutoAgent-TW: Memory Workflow (MemPalace Integration)

<objective>
管理專案與對話的長期記憶。支援搜尋、挖掘與狀態檢索。
</objective>

<process>
// turbo-all
1. **Discuss**: 釐清記憶需求 (例如：搜尋特定的決策、Mining 當前目錄)。
2. **Plan**: 根據指令決定調用 `mempalace search` 或 `mempalace mine`。
3. **Execute**: 執行 CLI 指令並處理編碼問題 (使用 PYTHONUTF8=1)。
4. **Verify**: 檢查結果是否與預期相符。
5. **Ship**: 總結記憶檢索或更新結果。
</process>

## Commands

### Init
```bash
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8=1; python -m mempalace --palace . init .
```

### Search
```bash
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8=1; python -m mempalace --palace . search "{{query}}"
```

### Mine
```bash
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8=1; python -m mempalace --palace . mine . --mode projects
```

### Status
```bash
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8=1; python -m mempalace --palace . status
```
