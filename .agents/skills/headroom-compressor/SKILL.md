---
name: headroom-compressor
description: Integrated Context Compression Layer using Headroom (v0.33.0). Auto-compresses massive logs, JSON tool outputs, and code context before feeding into LLM. Supports reversible retrieval (CCR) and cross-agent memory.
---

# Headroom Context Compressor Skill v1.0

## 🎯 Goal
提供 `AutoAgent-TW` 與 `Antigravity` 高效 Context 壓縮機制（針對大型 JSON、Log、AST 及歷史對話，達到 60%~95% Token 節省率），並維護 CCR (Reversible Context Compression)。

## 🧩 Usage Modes

### 1. Python SDK Direct Bridge
在 `mcp-router` 或自訂腳本中直接調用：
```python
from headroom import compress

compressed_data = compress(messages, model="claude-3-5-sonnet-20241022")
```

### 2. MCP Server Mode
使用 `headroom_mcp_config.json` 設定，開啟 `headroom mcp serve`，提供 Antigravity 存取以下 Tools：
- `headroom_compress`: 執行高效率 Token 壓縮。
- `headroom_retrieve`: 透過 CCR 恢復被壓縮的原資料。
- `headroom_stats`: 檢查目前 Context 壓縮率與 Token 節省統計。

### 3. Background Proxy Mode
啟動 Headroom 本地代理網關：
```bash
headroom proxy --port 8787
```

## 📊 Performance Benchmark Expectations
- **JSON Data**: 60%–95% reduction
- **Coding Agents / Logs**: 15%–47% reduction
- **Accuracy**: Preserved via AST/SmartCrusher content-aware routing
