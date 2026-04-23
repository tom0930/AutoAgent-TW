# AI Harness Cron Scheduler 使用指南

## 概述

Cron Scheduler 提供完整的排程任務管理功能。

## 支援的任務類型

| 類型 | 排程表達式 | 範例 |
|------|-----------|------|
| CRON | 標準 5 欄位 cron | `"*/5 * * * *"` 每 5 分鐘 |
| INTERVAL | 秒數間隔 | `"3600"` 每小時 |
| ONCE | 一次性 | `"once"` 執行一次後停用 |

## Cron 表達式格式

```
┌───────────── 分鐘 (0-59)
│ ┌──────────── 小時 (0-23)
│ │ ┌────────── 日 (1-31)
│ │ │ ┌──────── 月 (1-12)
│ │ │ │ ┌────── 星期 (0-6, 0=星期日)
│ │ │ │ │
* * * * *
```

### 特殊字元

- `*` - 任意值
- `,` - 列表分隔
- `-` - 範圍
- `/` - 步進

### 範例

| 表達式 | 說明 |
|--------|------|
| `* * * * *` | 每分鐘 |
| `0 * * * *` | 每小時整點 |
| `0 9 * * *` | 每天早上 9 點 |
| `*/15 * * * *` | 每 15 分鐘 |
| `0 9-17 * * 1-5` | 上班日 9-17 點每小時 |

## 使用方式

```python
from src.core.cron import CronScheduler, JobKind

# 初始化
scheduler = CronScheduler(Path("data/cron"))

# 新增 cron 任務
job_id = scheduler.add(
    name="Daily backup",
    kind=JobKind.CRON,
    schedule_expr="0 2 * * *",  # 每天凌晨 2 點
    payload={"action": "exec", "command": "python backup.py"}
)

# 立即執行
run = scheduler.run(job_id)
print(f"Result: {run.result}")
```

## 執行歷史

```python
# 列出最近 50 次執行
for run in scheduler.list_runs(limit=50):
    print(f"{run['status']} - {run['duration_ms']}ms")

# 列出特定任務的執行歷史
for run in scheduler.list_runs(job_id=job_id):
    print(f"  {run['started_at']}: {run['status']}")
```

---

*最後更新：2026-04-23*
