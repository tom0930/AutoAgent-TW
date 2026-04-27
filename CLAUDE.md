# CLAUDE.md — AutoAgent-TW 專案規範

> **最後更新**: 2026-04-27
> **版本**: v2.0
> **維護者**: Tom (Senior Architect)

## 🔴 核心設計決策 (Design Decisions)

1. **指令優先級**: 優先使用 `/aa-orchestrate` 進行大任務拆解，而非直接寫代碼。
2. **記憶隔離**: 所有敏感 API 操作必須標註 `[SECURED]` 並在執行後清除臨時記憶 (L1)。
3. **修復而非重建**: 遇到問題先修復，而不是刪除重來。

## 🛠️ 技術棧版本

- Python: `3.11+`
- Node.js: `22.x`
- pnpm: `10.32.1`
- TypeScript: `5.x`
- 框架: LangGraph (Python), OpenClaw (TypeScript)

## 📝 程式碼風格 (Coding Style)

### Python

- 嚴格遵守 PEP 8
- 使用 `ruff` 與 `black` 格式化
- **必須**有完整的類型註解 (PEP 484)

### ❌ 錯誤寫法

```python
# ❌ 錯誤：使用 any 類型
def get_user(user_id: any) -> any:
    return db.query(user_id)

# ✅ 正確：明確類型
def get_user(user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
```

```python
# ❌ 錯誤：沒有錯誤處理
def delete_file(path: str):
    os.remove(path)

# ✅ 正確：完整的錯誤處理
def delete_file(path: str) -> Result[None, str]:
    try:
        os.remove(path)
        return Ok(None)
    except FileNotFoundError:
        return Err(f"File not found: {path}")
    except PermissionError:
        return Err(f"Permission denied: {path}")
```

### TypeScript

- 使用 `strict` mode
- 禁止使用 `any`，使用 `unknown` 搭配類型守衛
- 所有匯出的函式必須標註回傳型別

```typescript
// ❌ 錯誤：any 類型
const processData = (input: any): any => {
  return JSON.parse(input);
};

// ✅ 正確：明確類型
interface ProcessResult {
  success: boolean;
  data?: unknown;
  error?: string;
}

const processData = (input: string): ProcessResult => {
  try {
    return { success: true, data: JSON.parse(input) };
  } catch (e) {
    return { success: false, error: (e as Error).message };
  }
};
```

## 🧪 測試要求 (Testing)

### 靜態檢查

```bash
# Python
ruff check .
mypy .

# TypeScript
pnpm check
```

### 單元測試

- 覆蓋率至少需達 80%
- 禁止在 Production 分支中使用 `assert` 推理
- 所有測試必須有 `teardown` 清理

### 正確 vs 錯誤測試

```python
# ❌ 錯誤：測試依賴真實 API
def test_get_user():
    user = requests.get("https://api.example.com/user/1")
    assert user.name == "Tom"

# ✅ 正確：使用 mock
def test_get_user():
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value = Mock(json=lambda: {"name": "Tom"})
        user = get_user("1")
        assert user.name == "Tom"
```

## 📋 常見任務 SOP

### 當使用者說「幫我新增一個頁面」

1. 在 `src/views/` 底下建立對應的 `.vue` / `.tsx` 檔案
2. 在 `src/router/` 中加入路由設定
3. 如果有共用邏輯，在 `src/composables/` / `src/hooks/` 底下建立對應的 composable
4. 建立對應的測試檔案
5. **驗證**: `pnpm test`

### 當使用者說「幫我加一個 API 串接」

1. 在 `src/services/` 底下建立對應的 service 檔案
2. 在 `src/types/` 底下定義請求與回應的 TypeScript 型別
3. 使用統一的 `apiClient` 封裝（不要直接使用 `fetch` 或 `axios`）
4. 建立對應的測試檔案
5. **驗證**: `pnpm test`

### 當使用者說「幫我改一支 API」

1. 先執行風險評估：`python scripts/preflight_gate.py --files src/api/xxx.py`
2. 查看對應的測試檔案
3. 修改後運行靜態檢查：`ruff check src/api/xxx.py`
4. 執行測試：`pytest tests/test_api.py`
5. **驗證**: `python scripts/preflight_gate.py --check`

## 🌍 回應規範

- **語言**: 一律使用繁體中文回應
- **Commit**: 使用 Conventional Commits 格式，描述使用繁體中文
- **程式碼**: 變數名稱與註解使用英文

```
# Commit 格式範例
feat(harness): 新增 Preflight Gate 風險評估功能
fix(permission): 修復 permission_engine 類型錯誤
docs(agents): 新增反面示例與 SOP 章節
```

## 🔗 重要文件索引

- [AGENTS.md](AGENTS.md) — Agent 行為準則與禁止事項
- [risk-tiers.json](risk-tiers.json) — 風險分級配置
- [ARCHITECTURE.md](ARCHITECTURE.md) — 系統架構說明
- [SECURITY.md](SECURITY.md) — 安全政策
- [preflight_gate.py](scripts/preflight_gate.py) — 風險評估腳本

---

**📝 更新記錄**

| 日期 | 更新內容 | 作者 |
|------|----------|------|
| 2026-04-27 | 新增技術棧版本、錯誤寫法範例、常見任務SOP、回應規範、文件索引 | ai代可行 |
