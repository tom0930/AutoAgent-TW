### 📚 `aa-memory` 指令完全使用指南 (AutoAgent-TW v1.9.0)

`aa-memory` 是專為 AutoAgent-TW 設計的持久化記憶管理工具。它允許您跨會話 (Session) 儲存架構決策、偏好設定或解決方案，並能靈活控制 AI 的專注力。

---

### 1. 基礎概念

記憶共分為三層 (`--level`)：

- **L1 (Session)**: 當前對話臨時記憶。
- **L2 (Project)**: **[預設]** 專案級持久記憶，儲存於 `.agent-state/memory/`。
- **L3 (Global)**: 跨專案通用記憶，儲存於使用者家目錄。

---

### 2. 常用操作指令

#### 📘 **列出項目 (List)**

顯示當前所有儲存的記憶、短 ID、標籤與建立時間。

```bash
python scripts/aa_memory.py list
```

> [!TIP]
> 帶有 `[FOCUSED]` 標籤的項目表示目前 AI **只會專注於此內容**。

#### 📝 **新增記憶 (Add)**

將重要的架構決策或 Bug 解決方案存入專案。

```bash
python scripts/aa_memory.py add "API 逾時設定應統一為 30 豪秒" --tags networking,config --level L2
```

#### 🎯 **專注模式 (Focus / Clear)**

當記憶過多且內容相互衝突時，讓 AI 只看特定的條目。

- **針對特定 ID 專注**:
  ```bash
  python scripts/aa_memory.py focus <ID末8碼>
  ```
- **解除專注 (恢復全部可見)**:
  ```bash
  python scripts/aa_memory.py focus clear
  ```

#### ❌ **刪除記憶 (Delete)**

永久移除過時或錯誤的上下文。

```bash
python scripts/aa_memory.py delete <ID末8碼>
```

#### 📤 **匯出上下文 (Export)**

預覽 AI 將會讀取到的記憶文字。

```bash
python scripts/aa_memory.py export
```

---

### 3. 進階參數速查表

| 參數        | 說明                             | 範例                       |
| :---------- | :------------------------------- | :------------------------- |
| `--level` | 指定記憶層級 (L1/L2/L3)          | `--level L3`             |
| `--tags`  | 為記憶加上標籤 (逗號分隔)        | `--tags database,v2,fix` |
| `id`      | 使用 `list` 指令輸出的 8 碼 ID | `d5386c74`               |

---

### 💡 實戰小技巧

1. **清理環境**：每當開始一個新子任務，建議先執行 `focus clear` 確保 AI 有完整的背景知識。
2. **解決衝突**：若 AI 重複犯錯（例如一直使用舊的 Library），請將正確的做法 `add` 進去，並對其執行 `focus`。

您可以現在輸入 `python scripts/aa_memory.py list` 來確認目前的記憶清單。
