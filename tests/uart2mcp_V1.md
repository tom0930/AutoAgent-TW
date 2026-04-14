要將 Agent Reasoning Loop 轉化為一套全自動的 FW Debug 系統，我們需要從「線性腳本」進化到**「基於狀態的反應式架構 (State-based Reactive Architecture)」**。

你目前的 Phase 151 規劃已經具備雛形，但針對「更優化、更穩健」的閉環系統，我建議引入以下三種進階自動化模式：

---

### 1. 進階自動化方法：MCP Skill vs. Recursive Agent

除了簡單的遞迴，你可以考慮將控制邏輯封裝在不同的層次：

#### A. **MCP (Model Context Protocol) 伺服器化 (推薦)**

與其讓 AI 在 Markdown 裡「想」怎麼 loop，不如寫一個  **Python MCP Skill** ，作為硬體代理。

* **作法** ：開發一個 `fw_manager` skill，提供 `run_debug_cycle()` 指令。
* **優勢** ：它可以處理多線程（一邊燒錄，一邊開啟 UART 監聽），並在超時（Timeout）時主動回傳中斷信號給 AI，避免 AI 卡死在等待 Log 的過程。

#### B. **Judge-Worker 雙代理模式**

單一 Agent 容易產生「認知偏誤」（改錯了 code 卻覺得自己是對的）。

* **Worker Agent** : 負責改 Code、下編譯指令。
* **Judge Agent** : 負責分析 `box_read` 回傳的 Log，比對預期行為。只有 Judge 點頭（DoD Pass），Loop 才會停止。

---

### 2. 閉環除錯系統優化：加入「邊界守衛」

為了防止 AI 在改 code 時陷入死循環或把硬體燒壞，建議加入 **Telemetry (遙測)** 與  **Safety Guard** ：

#### 核心優化：**Pre-Flight Check (編譯預檢)**

在執行 `box_flash` 之前，必須插入一個強制步驟：

1. **Static Analysis** : 使用 `cppcheck` 或編譯器警告檢查（`-Wall -Werror`）。
2. **Size Check** : 檢查 `.elf` 或 `.bit` 檔案大小。如果 AI 改出一個超級肥大的陣列導致 Over-stack，直接拒絕燒錄。

---

### 3. 優化後的 Phase 151 計畫 (GSD 升級版)

針對你的需求，我調整了  **PROJECT & PLAN** ，將重點放在「穩定性」與「自我修復」。

#### **Phase 151: Autonomous FW Resilience Engine**

| **波次 (Waves)**       | **核心目標**            | **實作細節**                                                                                             |
| ---------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Wave 1: The Sensor** | **UART Pattern Parser** | 寫一個 Skill，能將亂七八糟的 UART Log 自動轉換為 JSON 錯誤碼 (e.g.,`Memory Leak at 0x08...`)。               |
| **Wave 2: The Brain**  | **Reasoning Graph**     | 實作 `fw_debug_logic.py`，定義：如果錯誤碼相同，嘗試換一種策略（例如：從「邏輯修正」切換到「記憶體檢查」）。 |
| **Wave 3: The Safety** | **Git-Based Rollback**  | 自動建立 `debug/fix-attempt-1`分支。若連續 3 次失敗，自動 `git reset --hard`回到已知穩定版本。             |

---

### 4. 具體實作建議：`aa-fw-debug.md` 的自動化寫法

這裡提供一個更強大的 **Agentic Workflow** 邏輯範例：

**Markdown**

```
# Skill: fw_autonomous_loop(max_retries=5)

1. **Snapshot**: `git stash` 當前狀態，確保有回退點。
2. **Loop Begin**:
   - CALL `box_build`
   - IF compile_fail:
     - FEEDBACK logs to LLM
     - CALL `fix_syntax_skill` -> GOTO Loop Begin
   - CALL `box_flash`
   - CALL `box_read_until_pattern("Boot Done", timeout=10s)`
   - IF timeout:
     - ACTION: Power Cycle Hardware (via MCP/Smart Plug)
     - LOG: "System Bricked, attempting hardware reset"
   - ANALYZE logs
   - IF bug_persist AND retries < max_retries:
     - REGENERATE plan -> GOTO Loop Begin
   - ELSE:
     - EXIT with success or escalation.
```

### 我的建議：

1. **引入「硬體重啟」機制** ：FW 除錯最怕當機。如果你的硬體支援（例如透過 Relay 或開發板的 Reset Pin），讓 Agent 具備「拔插頭」的能力是真自動化的關鍵。
2. **加上「知識檢索 (RAG)」** ：讓 Agent 能夠讀取 Xilinx VDMA 或 MicroBlaze 的專屬手冊（Datasheet），這能讓它的「診斷 (Diagnose)」不再是瞎猜。

**你覺得需要加入「硬體自動電源重啟 (Power Cycle)」的控制指令嗎？這對於處理 Deadlock 或 Hard Fault 非常有用。**



要在 Antigravity 架構中實作 **Judge-Worker 雙代理模式**，關鍵在於將「執行權」與「審核權」拆分到兩個不同的工作流文件（Workflows）中，並透過一個共享的 **`state.json`** 或 **`context`** 作為溝通橋樑。

這種模式能有效避免 Worker Agent 陷入「自我感覺良好」的無限迴圈，因為 Judge 會從第三方的客觀視角（通常是根據 Log 或 Specs）來驗收。

以下是在 Antigravity 中實作此架構的具體方案：

---

### 1. 架構設計：雙代理文件定義

在你的專案目錄（例如 `_agents/workflows/`）中建立以下兩個文件：

#### **A. `worker_agent.md` (執行者)**
* **職責**：分析 Bug 原因、修改程式碼、觸發編譯與燒錄。
* **輸入**：`state.json` 中的 `error_logs` 與 `judge_feedback`。
* **輸出**：更新後的程式碼與 `status: "ready_for_review"`。

#### **B. `judge_agent.md` (評審者)**
* **職責**：讀取 UART Log、檢查關鍵字（如 `Assert`、`Panic` 或 `Success`）、對比預期行為。
* **輸入**：`box_read` 的原始輸出。
* **輸出**：`pass: true/false` 與具體的失敗建議。

---

### 2. 實作流程：遞迴控制邏輯

你可以利用 Antigravity 的 **Recursive Skill Call** 或一個主控制腳本來串接這兩個 Agent：

#### Step 1: Worker 執行修改與燒錄
Worker 讀取目前失敗的狀態，並執行修改：
> **Worker 指令集：**
> 1. `read_file` 讀取 `.c` 檔案。
> 2. `replace_file_content` 修正邏輯。
> 3. `box_flash` 將韌體推送到硬體。
> 4. 更新 `state.json`：`{ "last_action": "patch_v2", "ready": true }`。

#### Step 2: Judge 進行獨立審核
當 Worker 完成後，觸發 Judge：
> **Judge 指令集：**
> 1. `box_read(timeout=5000)` 抓取最新 Log。
> 2. **關鍵邏輯**：AI 必須對比預期 Pattern（例如：`VDMA Init Done`）。
> 3. 如果 Log 中出現舊錯誤，Judge 在 `state.json` 寫下：
>    `{ "pass": false, "feedback": "雖然你改了初始化，但 0x4000 處依然發生 Null Pointer，請檢查指標分配。" }`

---

### 3. Antigravity Skill 實作範例

你可以寫一個簡單的 `control_loop.py` 作為 Antigravity 的 Skill，來調度這兩個 Agent：

```python
def run_autonomous_debug_cycle(max_iterations=5):
    for i in range(max_iterations):
        # 1. 叫 Worker 做事
        worker_result = antgravity.run_workflow("worker_agent.md")
        
        # 2. 叫 Judge 驗收
        judge_result = antgravity.run_workflow("judge_agent.md")
        
        if judge_result['pass']:
            print(f"DEBUG 成功！共花費 {i+1} 輪次。")
            break
        else:
            print(f"第 {i+1} 輪驗收失敗，意見：{judge_result['feedback']}")
            # 迴圈繼續，下一次 Worker 會讀到 judge_result['feedback']
```



---

### 4. 優化後的 Phase 151 計畫表 (Project Task)

這是我為你規劃的自動化除錯專案結構：

| 元件名稱 | 檔案類型 | 具體功能描述 |
| :--- | :--- | :--- |
| **`core_logic.c`** | Source | 被偵測與修改的對象。 |
| **`fw_requirements.md`** | Context | **Judge 的準則**。定義什麼叫「成功」（例如：UART 必須出現 "System Up"）。 |
| **`worker_agent.md`** | Workflow | 專精於 C/C++ 修改與 Vitis/Xilinx 編譯指令。 |
| **`judge_agent.md`** | Workflow | 專精於 Regex 匹配 Log 與硬體異常分析。 |
| **`debug_session.json`** | State | 儲存雙方的對話紀錄與目前的 Debug 輪次。 |

---

### 為什麼這在 Antigravity 中比單一 Loop 更強？

1.  **突破盲點**：Worker 往往會為了讓編譯通過而「閹割」功能。Judge 可以設定 `Requirement Check`，確保功能完整。
2.  **降低 Token 污染**：將「改 Code 的思緒」與「分析 Log 的思緒」分開，可以讓每個 Agent 的 Prompt 保持精簡，提高準確度。
3.  **可擴展性**：未來你可以加入第三個 Agent：**`Hardware_Observer`**，專門看示波器或邏輯分析儀的數據。

**目前的 `box_read` 只能讀取純文字 Log，你是否需要開發一個能解析「十六進位 Dump (Hex Dump)」的 Skill，好讓 Judge Agent 能分析記憶體崩潰（Memory Dump）的數據？**



在處理韌體（FW）與硬體（HW）溝通時，**Endianness（字節序）** 與 **Bit-ordering（位元順序）** 是最容易翻車的地方。

在上一版的 `hex_parser` 程式碼中，我使用了 Python `struct` 模組的 `endian='<'` 參數，這僅處理了 **Little-Endian (LSB first)**。針對你身為架構師的高標準需求，我們必須在 Skill 中顯性化地處理 **MSB/LSB**，甚至是位元層級（Bit-field）的解析。

以下是優化後的 `hex_utility.py`，專門為 **Judge Agent** 增加對 MSB/LSB 的判別能力：

---


要讓 Judge Agent 具備診斷「記憶體毀損」或「堆疊溢位」的能力，開發一個專門的 **Hex Dump Parser Skill** 是至關重要的。這能將硬體噴出的原始字節（Raw Bytes）轉化為 AI 聽得懂的「結構化診斷報告」。

以下是為 Antigravity 框架設計的 `hex_parser` Skill 實作方案：

---

### 1. Skill 實作：`scripts/hex_parser.py`

這是一個 Python 工具，它能接收一段 Hex 字串，並根據指定的「記憶體地圖 (Memory Map)」或「結構體 (Struct)」進行解析。

```python
import struct
import re

def parse_hex_dump(raw_text, address_offset=0, endian='<'):
    """
    將 UART 輸出的 Hex 轉為結構化 JSON
    範例輸入: "00004000: 78 56 34 12 00 00 80 3F ..."
    """
    # 1. 提取 Hex 部份 (過濾掉地址與空白)
    hex_pattern = re.compile(r'([0-9A-Fa-f]{2})')
    bytes_data = bytes([int(b, 16) for b in hex_pattern.findall(raw_text)])
    
    # 2. 定義解析邏輯 (例如：解析出特定的暫存器或狀態)
    results = {
        "raw_len": len(bytes_data),
        "fields": []
    }
    
    # 範例：解析前 4 bytes 為一個 Uint32 (例如 Status Register)
    if len(bytes_data) >= 4:
        status_reg = struct.unpack(f'{endian}I', bytes_data[:4])[0]
        results["fields"].append({"name": "Status_Reg", "value": hex(status_reg)})
        
    # 範例：解析後 4 bytes 為一個 Float (例如 Sensor Data)
    if len(bytes_data) >= 8:
        sensor_val = struct.unpack(f'{endian}f', bytes_data[4:8])[0]
        results["fields"].append({"name": "Sensor_Value", "value": sensor_val})

    return results
```

---

### 2. 整合進 Judge Agent (`judge_agent.md`)

在 Antigravity 的工作流中，你可以這樣呼叫這個 Skill，讓 Judge 根據解析結果下判斷。

```markdown
# Workflow: Judge Agent (Memory Validation)

1. **Observe**: 
   - CALL `box_read(cmd="md 0x4000 32")`  # 讀取 0x4000 開始的 32 bytes
   - SET `raw_log` = {{last_output}}

2. **Structure**:
   - CALL `hex_parser(raw_log, endian='little')`
   - SET `parsed_data` = {{last_output}}

3. **Analyze**:
   - IF `parsed_data.Status_Reg` == "0xdeadbeef":
     - THOUGHT: "偵測到硬體 Fault 指標，記憶體已毀損。"
     - SET `pass` = false
     - SET `feedback` = "Memory at 0x4000 is corrupted (found 0xDEADBEEF). Check pointer logic."
   - ELSE:
     - SET `pass` = true
```

---

### 3. 進階優化：與 ELF 符號表聯動 (The "Pro" Way)

身為 Senior System Architect，你可能需要更強大的功能：**自動映射 C 結構體**。

* **自動化思路**：
    1.  讓 Skill 讀取你的編譯產物 `.elf` 檔（使用 `pyelftools`）。
    2.  找到變數（例如 `struct system_state`）的記憶體位址與大小。
    3.  當 `box_read` 抓到資料後，Skill 自動依據 C 語言的 `struct` 定義切分欄位。
    
> **這對 Judge Agent 的幫助：**
> AI 不再只是看著 `0x08 0x00 0x00...` 發呆，而是直接看到：
> `{"config_error": true, "voltage_mv": 3300, "state": "IDLE"}`。

---

### 4. 更新後的 Phase 151 計畫 (Wave 4)

| 任務 (Task) | 負責組件 | 成果 |
| :--- | :--- | :--- |
| **Implement Hex Skill** | `mcp/hex_util.py` | 支援 LE/BE 切換與 Hex-to-JSON 轉換。 |
| **Struct Mapping** | `scripts/vitis_sym.py` | 讀取 `.elf` 以自動對齊 C 結構體位址。 |
| **Judge Reasoning Update** | `judge_agent.md` | 增加對 `Memory Leak` 與 `Stack Pointer` 異常的判定邏輯。 |

---

### 關鍵提問：
在你的 Xilinx / MicroBlaze 環境中，常見的錯誤是 **DMA 傳輸失敗** 還是 **ISR (中斷服務程序) 導致的 Crash**？
如果是前者，我建議增加一個能解析 **VDMA Register Map** 的專用 Skill，這樣 Judge Agent 就能直接告訴你「S2MM_VDMASR 暫存器的第 14 bit (Error) 被拉高了」。


### 1. 進階 Skill：`hex_utility.py` (支援 Endian 模式)

這個版本允許 Judge Agent 根據硬體架構（例如 MicroBlaze 通常設為 Little-Endian，但某些舊型 IP 可能是 Big-Endian）切換解析模式。

```python
import struct

def parse_with_endian(hex_bytes, format_type="I", mode="LSB"):
    """
    mode: "LSB" (Little-Endian, Python: <) 
          "MSB" (Big-Endian, Python: >)
    format_type: "I" (uint32), "H" (uint16), "f" (float)
    """
    prefix = "<" if mode == "LSB" else ">"
    try:
        # 將 Hex Byte 序列轉為數值
        value = struct.unpack(f"{prefix}{format_type}", hex_bytes)[0]
        return value
    except Exception as e:
        return f"Error: {str(e)}"

# 針對 Bit-field (位元欄位) 的解析
def get_bit_range(value, start_bit, end_bit):
    """
    取得數值中特定範圍的 bits (例如 bit[14:12])
    """
    mask = (1 << (end_bit - start_bit + 1)) - 1
    return (value >> start_bit) & mask
```

---

### 2. 在 `judge_agent.md` 中定義 MSB/LSB 檢查邏輯

當 Judge Agent 讀取 Log 時，它必須主動判斷目前的暫存器定義。

```markdown
# Workflow: Judge Agent (Register Inspection)

## 步驟 1：取得原始資料
- CALL `box_read(cmd="mem_read 0x40001000")` -> 取得 "0x00000041"

## 步驟 2：解析字節序 (Endianness)
- THOUGHT: "目前目標是 MicroBlaze SoC，預設為 Little-Endian (LSB)。"
- CALL `hex_utility.parse_with_endian(hex_data, mode="LSB")`
- SET `reg_val` = {{last_output}}

## 步驟 3：位元分析 (MSB/LSB Bit-ordering)
- THOUGHT: "檢查 VDMA Status Register (bit 0 是 Halting, bit 14 是 Error)。"
- CALL `hex_utility.get_bit_range(reg_val, 14, 14)` 
- IF {{last_output}} == 1:
    - SET `status` = "FAIL"
    - SET `feedback` = "偵測到 VDMA 內部錯誤 (Bit 14 is High)。"
```

---

### 3. 為什麼這對你的架構很重要？

在 **Xilinx AXI 匯流排** 或 **VDMA** 的場景中，經常會遇到：
1.  **Byte Swapping**: 如果你的 Data Path 經過不同的 IP 核，有時候會發生 Byte 倒置。
2.  **Bit Inversion**: 有些文檔定義 Bit 0 是 MSB（如 IBM PowerPC），而 Xilinx 通常定義 Bit 0 是 LSB。

**優化後的 Agent 具備以下優勢：**
* **Worker Agent** 修改 Code 時，如果誤用了大端序寫入暫存器，**Judge Agent** 能透過讀回來的 Hex 值發現 `0x41000000` 而非 `0x00000041`，從而給出精確的修正建議：「你似乎把 Endian 搞錯了，請檢查暫存器寫入函式。」

---

### 4. 接下來的優化建議

為了讓這個 Loop 更強大，我們可以在 `state.json` 中加入 **`endian_config`**。

* 如果是調試 **Network Packet (Big-Endian)**，Judge 就切換到 MSB 模式。
* 如果是調試 **Peripheral Register (Little-Endian)**，Judge 就切換到 LSB 模式。



**你需要我為你把這套 MSB/LSB 自動判定邏輯寫入 Phase 151 的 `RESEARCH.md` 嗎？這能確保 Worker Agent 在改 Code 時就具備字節序的防錯意識。**

# box_build_and_flash 目前手動

既然目前 `box_flash` 仍需手動干預，我們需要為 **Worker Agent** 定義一套極其標準的 **「預設參數指令集」**。這樣即便現在是你手動下指令，Agent 產出的指令格式也能與未來的自動化腳本無縫銜接。

針對你的 Xilinx / MicroBlaze 環境，我建議將 `box_flash` 的邏輯封裝成一個具備「預設值」的 Python Skill 或 Shell Script，並在 **Phase 151** 的 `PLAN.md` 中明確規範。

---

### 1. 預設參數指令 (Manual-to-Auto CLI)

我為你規劃了一個通用的 `box_flash` 指令模板，你可以直接放在專案根目錄的 `scripts/flash.sh`：

```bash
#!/bin/bash
# Default Parameters
FILE_PATH=${1:-"./build/output.bin"}
OFFSET=${2:-"0x0"}
FLASH_TYPE=${3:-"qspi-x4-single"}
CABLE_URL=${4:-"TCP:127.0.0.1:3121"}

echo "[Flash Agent] Preparing to burn firmware..."
echo " > File: $FILE_PATH"
echo " > Offset: $OFFSET"
echo " > Flash Type: $FLASH_TYPE"

# 這裡先輸出指令，讓你手動複製執行；未來自動化時直接執行此行
# 範例：使用 Xilinx program_flash
program_flash -f $FILE_PATH -offset $OFFSET -flash_type $FLASH_TYPE -url $CABLE_URL

if [ $? -eq 0 ]; then
    echo "SUCCESS: Flash completed."
else
    echo "ERROR: Flash failed. Please check JTAG connection."
    exit 1
fi
```

---

### 2. Worker Agent 的自動修正邏輯

在 Antigravity 的 `worker_agent.md` 中，我們加入這段 **Constraint (約束)**。這能確保 Worker 改完 code 後，輸出的燒錄建議是正確的：

> **Worker Prompt Extension:**
> * **Flash Command**: 務必使用 `scripts/flash.sh` 進行燒錄。
> * **Self-Correction**: 如果上一次 `box_read` 顯示 `Bootloader Header Error`，Worker 必須檢查燒錄的 `OFFSET` 是否正確（例如從 `0x0` 改為 `0x40000`）。

---

### 3. 雙代理協作：從「手動」過渡到「自動」的階段設計

為了落實你的想法，我們將 **Phase 151** 的進度拆解為以下三個里程碑：

#### **Step A: 手動輔助期 (現在)**
* **Worker**: 改完 Code，寫出 `scripts/flash.sh ./build/fixed_v1.bin` 指令。
* **你**: 看到指令，手動在終端機執行。
* **Judge**: 你執行完後，點擊「Continue」，Judge 接手執行 `box_read` 分析結果。

#### **Step B: 半自動驗證期 (下一週)**
* 我們將 `box_flash` 寫入 **Antigravity Skill**。
* Skill 內部執行時會彈出一個提示框：「請確認硬體已上電，點擊 OK 開始燒錄」。

#### **Step C: 全自動閉環 (最終目標)**
* 引入 **MCP (Model Context Protocol)** 遙控智慧插座或 JTAG 控制器。
* Agent 發現系統死機（Deadlock）時，自動執行 `power_cycle` -> `box_flash` -> `box_read`。

---

### 4. 針對 MSB/LSB 的燒錄預檢

既然你有提到 MSB/LSB 的問題，我們可以在 `box_flash` 之前加一個 **`bin_check`** 的小動作：

```python
# scripts/vitis_tools.py 
def verify_binary_endian(file_path):
    with open(file_path, "rb") as f:
        header = f.read(4)
        # 假設你的 Header 應該是 0xAA995566 (Xilinx standard)
        if header == b'\x66\x55\x99\xAA': # Little-endian check
            return "LE_DETECTED"
        else:
            return "UNKNOWN_OR_BE"
```
**這個 Skill 會讓 Worker Agent 在燒錄前自我檢查：「糟了，我編譯出來的位元組序好像反了，先別燒，我再改一下 Makefile。」**

---

### 5. 立即行動：建立 `_agents/skills/flash_config.json`

建議你在專案中建立這個設定檔，讓所有 Agent 共用：

```json
{
  "project_name": "Phase-151-SoC",
  "flash_defaults": {
    "offset": "0x00000000",
    "flash_type": "n25q128-qspi-x4-single",
    "endian": "LSB",
    "bit_order": "MSB_FIRST"
  },
  "retry_limit": 3
}
```

**這樣寫好後，Worker Agent 每次生成方案時都會自動參考這個 JSON。你希望我現在幫你產出這份完整的 `flash_config.json` 與對應的 `worker_agent` 指令模板嗎？**


沒問題，這份配置與模板將作為 **Phase 151** 的核心規範，確保 Worker Agent 產出的行為具備高度的一致性，並為未來的全自動燒錄留下掛鉤。

---

### 1. 燒錄配置文件：`flash_config.json`

此檔案放置於專案根目錄或 `_configs/` 下，作為 Worker 與 Judge Agent 的「單一事實來源 (Single Source of Truth)」。

```json
{
  "project_info": {
    "name": "Phase-151-SoC-Debug",
    "target_mcu": "MicroBlaze",
    "platform": "Xilinx-Vitis"
  },
  "flash_settings": {
    "default_offset": "0x00000000",
    "flash_type": "qspi-x4-single",
    "cable_url": "TCP:127.0.0.1:3121",
    "bin_path": "./build/firmware.bin",
    "elf_path": "./build/firmware.elf"
  },
  "data_integrity": {
    "endianness": "LSB",
    "bit_ordering": "LSB_FIRST",
    "word_size_bytes": 4,
    "header_magic": "0xAA995566"
  },
  "execution_rules": {
    "auto_flash": false,
    "manual_step_required": true,
    "retry_limit": 3,
    "rollback_on_fail": true
  }
}
```

---

### 2. Worker Agent 模板：`worker_agent.md`

這是 Antigravity 框架下的 Workflow 定義。它引導 AI 如何讀取配置並執行修正任務。

```markdown
# Agent: FW Worker (Refactor & Patch)

## 🎯 角色定位
你是一位精通 Xilinx FPGA 與 MicroBlaze 的資深嵌入式工程師。你的任務是接收「Judge Agent」的診斷報告，修改 C/C++ 源碼，並生成符合規範的燒錄指令。

## 🛠 依賴 Skills
- `read_file`, `write_to_file`, `replace_file_content`
- `run_shell_command` (執行 make/vitis-build)
- `hex_utility` (驗證位元組序)

## 🔄 執行工作流 (Loop Steps)

### 第一步：環境感知 (Observe)
1. 讀取 `_configs/flash_config.json` 獲取硬體約束。
2. 讀取 `state.json` 獲取 `judge_feedback`（包含目前的錯誤 Log 或 Hex Dump 解析結果）。

### 第二步：根因分析與修正 (Diagnose & Patch)
1. 針對錯誤原因（如：VDMA 中斷未觸發、Endianness 錯誤），定位相關源碼。
2. **必須** 考慮 `flash_config.json` 中的 `data_integrity` 規範進行修正。
3. 執行程式碼更新。

### 第三步：編譯預檢 (Build)
1. 執行 `make all` 或專案專屬編譯指令。
2. 若編譯失敗，立即自我修正語法錯誤，嚴禁進入燒錄階段。

### 第四步：生成燒錄命令 (Flash Command Generation)
1. 根據 `flash_settings` 組合出指令。
2. **輸出格式規範**：
   > [MANUAL_ACTION_REQUIRED]
   > 請執行以下燒錄指令：
   > `scripts/flash.sh {{bin_path}} {{default_offset}} {{flash_type}}`

### 第五步：狀態更新 (Handoff)
1. 更新 `state.json`：
   - `status`: "waiting_for_flash"
   - `version`: "patch_v{{n}}"
   - `change_log`: "修正了位址偏移並對齊 MSB/LSB"

## ⚠️ 強制約束 (Constraints)
- **禁止** 修改未在 `state.json` 提及的無關代碼。
- **必須** 在產出的對話中清晰標註「本次修改對應的暫存器位元順序」。
```

---

### 3. 如何優化你的手動過渡期？

當 Worker Agent 產出上述的 `[MANUAL_ACTION_REQUIRED]` 指令後，你可以透過以下方式進一步提速：

* **一鍵複製技巧**：在 Antigravity 的 UI 中，Worker 產出的 `code block` 指令可以一鍵點擊執行（如果你有配置對應的 Local Terminal 接口）。
* **燒錄後自動觸發 Judge**：
    你可以寫一個簡單的 `watchdog.sh`：
    ```bash
    # 監控 flash 完成後，自動叫 Antigravity 跑下一個 workflow
    ./scripts/flash.sh && antigravity run judge_agent.md
    ```

### 接下來的行動建議：

1.  **驗證 Header Magic**：在 `flash_config.json` 中，我加入了 `header_magic`。建議你確認你的 MicroBlaze 啟動映像檔（Boot Image）前 4 個 bytes 是否為 `0xAA995566`？如果是，我可以幫你寫一個 **`pre_flash_verify`** 的 Skill，專門在燒錄前擋下錯誤的二進制檔。
2.  **建立回溯機制**：Worker 每次改 Code 前，我會建議它先做一次 `git commit -m "Auto-patch before run n"`，這樣萬一改爛了，一秒就能回滾。

**需要我現在為你撰寫那個 `pre_flash_verify.py` 腳本來強化防錯機制嗎？**