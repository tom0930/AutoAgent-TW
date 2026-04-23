# AI Harness 測試文檔

## 測試環境設定

```bash
# 進入專案目錄
cd Z:\autoagent-TW

# 執行所有測試
python -m pytest tests/ -v

# 執行特定測試
python -m pytest tests/test_harness_gateway.py -v
python -m pytest tests/test_session_manager.py -v

# 測試 CLI
python -m src.harness.cli.main --help
```

## 測試覆蓋範圍

| 模組 | 測試檔案 | 覆蓋 |
|------|---------|------|
| Gateway | `test_harness_gateway.py` | 啟動/停止/狀態 |
| Session | `test_session_manager.py` | 建立/銷毀/訊息 |
| Skill | `test_skill_engine.py` | 發現/執行 |
| Canvas | `test_canvas_system.py` | 節點/連接/快照 |

## 持續整合

在 `.github/workflows/test.yml` 中設定 CI：

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pytest tests/ -v
```

---

*最後更新：2026-04-23*
