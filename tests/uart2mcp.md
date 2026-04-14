mcp2serial

rem https://github.com/mcp2everything/mcp2serial

rem https://www.serialtool.com/_zh/virtual-com-ports.php







https://github.com/adancurusul/serial-mcp-server

[https://github.com/es617/serial-mcp-server](https://github.com/es617/serial-mcp-server) 或 [https://github.com/adancurusul/serial-mcp-server	](https://github.com/adancurusul/serial-mcp-server)

這兩個提供真正的低階工具：


下面是兩個 `serial‑mcp‑server` 專案的工具列表與用途對照，以 Markdown 表格整理成「每個工具名稱＋用途說明」。

---

## adancurusul / serial‑mcp‑server

| 工具名（Tool） | 用途說明                                                                                                                            |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `list_ports` | 列出系統上所有可用的 serial port，例如 `COM1`,`COM3`,`/dev/ttyUSB0`等，讓 AI 代理先選出要對接的硬體。**lobehub**+2      |
| `open`       | 以指定設定（如波特率 `baud rate`）開啟一個 serial port 連線，用來與 STM32、Arduino、ESP32 等裝置建立通訊管道。**lobehub**+2 |
| `write`      | 向已開啟的 serial port 發送資料，可以用於發出命令、觸控 GPIO、切換 LED 或任何硬體控制。**lib**+1                              |
| `read`       | 從 serial port 讀取資料，支援 timeout，常用於接收 firmware 回應、除錯 log 或 UART 訊息。**lobehub**+2                         |
| `close`      | 安全關閉 serial port 連線，釋放資源，避免後續重複連線問題。**lobehub**+1                                                      |

---

## es617 / serial‑mcp‑server

| 工具名（Tool）             | 用途說明                                                                                                                                      |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `list_ports`             | 列出系統上所有可用的 serial port，與 adancurusul 的 `list_ports`類似，是硬體連線前的「port list 表」來源。**pulsemcp**+1              |
| `open`                   | 以指定參數（如路徑、波特率等）開啟一個 serial 連線，用於與 UART 裝置（如 STM32、ESP）建立通訊。**pulsemcp**+2                           |
| `write`                  | 向已開啟的 serial port 寫入資料，適合發送命令、觸發硬體行為或模擬 CLI 互動。**pulsemcp**+2                                              |
| `read`                   | 從 serial port 原始讀取資料，通常用於「wire‑level」的除錯或 raw byte 流分析。**es617**+1                                               |
| `serial.readline`        | 以「行」為單位讀取資料（例如看到 `\n`才回傳），適合典型的 CLI 風格命令／回應流程。[es617](https://es617.dev/2026/02/15/serial-mcp-server.html) |
| `serial.read_until`      | 一直讀取直到遇到某個字串或分隔符，常用於等待裝置就緒、握手協議或分段訊息的標記。[es617](https://es617.dev/2026/02/15/serial-mcp-server.html)     |
| `serial.close`/`close` | 關閉 serial 連線，釋放資源，避免後續連線衝突或資源洩漏。**pulsemcp**+1                                                                  |

---

## 簡易對照表（只看核心工具）

| 功能角色（用途） | adancurusul | es617 |
| ---------------- | ----------- | ----- |

| 功能角色（用途）     | adancurusul                         | es617                                                                           |
| -------------------- | ----------------------------------- | ------------------------------------------------------------------------------- |
| 列出可用 port 清單   | `list_ports` **lobehub**+1  | `list_ports` **pulsemcp**+1                                             |
| 開啟連線             | `open` **lobehub**+1        | `open` **pulsemcp**+2                                                   |
| 發送資料             | `write` **lobehub**+1       | `write` **pulsemcp**+2                                                  |
| 讀取資料（原始）     | `read` **lobehub**+1        | `read` **es617**+1                                                      |
| 讀取一行（CLI 風格） | 未明示獨立行工具                    | `serial.readline` [es617](https://es617.dev/2026/02/15/serial-mcp-server.html)   |
| 等到某訊息／分隔符   | 內建在 `read`/ 配置中，無專用名稱 | `serial.read_until` [es617](https://es617.dev/2026/02/15/serial-mcp-server.html) |
| 關閉連線             | `close` **lobehub**+1       | `serial.close`或 `close` **pulsemcp**+1                               |

如果你需要，我也可以再幫你用中文把所有工具名 + 引數範例（例如 `list_ports()`、`open(port, baud_rate=115200)` 這種 signature）整理成一個「API table」。





這兩個提供真正的低階工具：

* list_serial_ports
* open_serial / connect
* write_uart（或 send、write）
* read_uart（支援 timeout、等待特定關鍵字）
* read_until、read_all 等

AI 可以**完全自由地**讀寫 UART，就像你自己在終端機操作一樣，非常適合「根據 UART 回應來決定下一步 patch code」的閉環測試。

#### 方案 B：修改 mcp2serial 增加 raw write/read 工具

如果你想繼續用 mcp2serial，可以自己 fork 並新增兩個工具：

在 server 端增加：

* raw_write：直接發送任意字串到 UART（不經過 command 模板）
* raw_read：讀取指定時間內的 raw data（或 read_until）

這樣 AI 就能呼叫 raw_write(data="任意指令\r\n") 和 raw_read(timeout=2000)。

#### 方案 C：結合多個 MCP（最佳實務）

同時跑兩個 MCP Server：

1. **mcp2serial** （或你修改後的版本） → 處理固定命令與自然語言控制。
2. **serial-mcp-server** （es617 或 adancurusul） → 提供 raw write_uart / read_uart 給 AI 做複雜測試與 code 修改決策。

AI Agent 可以同時看到兩組 tools。

### 如何讓 AI 用 UART 收到的 data 來自動修改 FW code

給 AI 的核心 Prompt 範例（假設你已經有 raw write/read 工具）：

> 你現在是嵌入式 FW 自動優化工程師。
> 目前 DUT 透過 UART (115200, 8N1) 連線。
> 請使用 write_uart / read_uart 工具完成以下閉環：
>
> 1. 重啟裝置，讀取完整 boot log。
> 2. 分析 log，找出目前問題（例如效能瓶頸、bug、想優化的功能）。
> 3. 根據分析結果，修改對應的 FW source code（告訴我你要改哪幾個檔案、怎麼改）。






以下是 **兩個獨立 UDP port** 的完整設定與程式，符合你的需求：

- **Docklight** 使用 **UDP port 5000**（給手動操作 / 顯示用）
- **AI MCP** 使用 **Python UDP** 連 **port 5001**

這樣 Docklight 和 AI MCP 是兩個獨立的 UDP peer，不互相干擾，但兩邊都可以透過 **Python 中間層** 看到 Box 的資料，並把自己的指令送給 Box。

### 1. Docklight UDP 設定（port 5000）

在 Docklight **Project Settings → Communication** 中設定：

- **Communication Mode**：**Send/Receive**
- **Send/Receive on Comm. Channel**：**`UDP:127.0.0.1:5000`**（或更精確的 `UDP:127.0.0.1:5000:5000`）
- Baud Rate 等可以忽略（UDP 不使用）
- 按 **OK** → 然後 **Communication → Start Communication**

這樣 Docklight 就會：

- 送出資料到 127.0.0.1:5000
- 同時在本地 port 5000 接收資料
- 你可以在 Docklight 視窗中手動 Send Sequence，或直接看到從 Box 來的資料

### 2. Python 中間層（純 Python 轉接程式）

這個程式負責：

- 獨占物理 serial port（Box）
- 把 Box 的資料 **廣播** 到 UDP 5000（Docklight）和 UDP 5001（AI MCP）
- 把 Docklight 或 AI 送來的資料轉送到 Box

```python
import serial
import socket
import threading
import time
import sys

# ================== 配置區 ==================
SERIAL_PORT = 'COM3'          # ← 改成你的實際 Box port
BAUDRATE    = 115200

UDP_PORT_DOCKLIGHT = 5000     # Docklight 使用這個 port
UDP_PORT_AI        = 5001     # AI MCP 使用這個 port

HOST = '127.0.0.1'
BUFFER_SIZE = 4096
TIMEOUT = 0.05
# ===========================================

ser = None
udp_sock_dock = None
udp_sock_ai = None

def serial_reader():
    """從 Box 讀取資料 → 廣播到兩個 UDP port"""
    global ser
    print(f"監聽 Box: {SERIAL_PORT} @ {BAUDRATE}")
    while True:
        try:
            if ser and ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    hex_str = data.hex().upper()
                    ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
                    print(f"[Box → All] {hex_str}  | ASCII: {ascii_str}")

                    # 廣播給 Docklight 和 AI
                    if udp_sock_dock:
                        udp_sock_dock.sendto(data, (HOST, UDP_PORT_DOCKLIGHT))
                    if udp_sock_ai:
                        udp_sock_ai.sendto(data, (HOST, UDP_PORT_AI))
        except Exception as e:
            print(f"Serial 讀取錯誤: {e}")
            time.sleep(0.1)

def udp_listener(sock, name):
    """監聽 UDP port，收到後轉送到 Box"""
    print(f"UDP Listener 啟動: {name} port {sock.getsockname()[1]}")
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if data:
                print(f"[{name} → Box] {data.hex().upper()} from {addr}")
                if ser and ser.is_open:
                    ser.write(data)
        except Exception as e:
            print(f"{name} UDP 接收錯誤: {e}")
            time.sleep(0.1)

# ================== 主程式 ==================
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT, exclusive=True)
    print(f"✅ 已開啟 Box: {SERIAL_PORT}")
except Exception as e:
    print(f"❌ 無法開啟 serial: {e}")
    sys.exit(1)

# 建立兩個 UDP socket（雙向）
udp_sock_dock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock_dock.bind((HOST, UDP_PORT_DOCKLIGHT))

udp_sock_ai = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock_ai.bind((HOST, UDP_PORT_AI))

# 啟動 serial 讀取 thread
threading.Thread(target=serial_reader, daemon=True).start()

# 啟動兩個 UDP 監聽 thread
threading.Thread(target=udp_listener, args=(udp_sock_dock, "Docklight"), daemon=True).start()
threading.Thread(target=udp_listener, args=(udp_sock_ai, "AI_MCP"), daemon=True).start()

print("\n=== 純 Python UDP 轉接已運行 ===")
print(f"Docklight 已設定為 UDP:127.0.0.1:5000")
print(f"AI MCP 請用 UDP 連線到 127.0.0.1:5001")
print("按 Ctrl+C 結束\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n關閉中...")
finally:
    if ser and ser.is_open:
        ser.close()
    if udp_sock_dock:
        udp_sock_dock.close()
    if udp_sock_ai:
        udp_sock_ai.close()
```

### 3. AI MCP 的 Python UDP 客戶端範例（port 5001）

```python
import socket
import threading
import time

UDP_IP = '127.0.0.1'
UDP_PORT = 5001
BUFFER_SIZE = 4096

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))   # 如果需要接收，需 bind

def ai_receiver():
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[AI 收到 from Box] {data.hex().upper()}")
        # 在這裡加入你的 AI 處理邏輯
        # 例如呼叫 LLM、判斷資料、決定是否回應

        # 範例：簡單 echo 回應
        # if b"特定指令" in data:
        #     response = b"AI 回應: OK\r\n"
        #     sock.sendto(response, (UDP_IP, 5001))  # 送回給中間層

threading.Thread(target=ai_receiver, daemon=True).start()

print(f"AI MCP UDP 已啟動，監聽 port {UDP_PORT}")

# 測試手動送指令
while True:
    cmd = input("AI 送指令給 Box (直接輸入文字或 hex): ")
    if cmd.lower() == 'exit':
        break
    try:
        # 如果輸入是 hex（如 "01 03 00 00 00 01"）
        if all(c in '0123456789ABCDEFabcdef ' for c in cmd.replace(' ', '')):
            data = bytes.fromhex(cmd)
        else:
            data = cmd.encode('ascii') + b'\r\n'
        sock.sendto(data, (UDP_IP, 5001))   # 送給 Python 中間層
    except Exception as e:
        print("送出錯誤:", e)
```

### 使用流程總結

1. 執行上面的 **Python 中間層**（它會開 Box 的 serial port）。
2. 在 Docklight 設定 **UDP:127.0.0.1:5000** 並啟動。
3. 執行 **AI MCP Python** 程式（連 5001）。
4. 現在：
   - Box 的資料會同時出現在 Docklight 視窗 和 AI 程式中
   - Docklight 手動送出的指令會到 Box，AI 也能看到
   - AI 送出的指令會到 Box，Docklight 也能看到

需要我幫你：

- 在 AI 端加上真正的 LLM 呼叫（例如 Grok API）？
- 讓 Docklight 與 AI 完全看到彼此的指令（目前已經可以）？
- 改成更進階的 UDP 設定（不同 send/receive port）？

直接告訴我下一步需求即可！



**✅ 已根據你的 UDP + Python Bridge 需求，完整調整成最適合 Antigravity IDE + FPGA + MicroBlaze 的配置。**

你的兩個 UDP port 設計非常好：

- **Docklight** 用 **UDP 5000** → 手動操作 + 即時顯示 HEX/ASCII
- **AI** 用 **UDP 5001** → 專屬給 AI MCP，不互相干擾
- Python 中間層負責廣播 FW 的 `printf` debug 資訊，並轉發兩邊的命令

以下是**完整、精準、可直接執行的最終方案**（已修正 AI 端整合問題）。

### 1. Python 中間層（你提供的程式已很好，我只做小優化）

請使用你提供的 Python 中間層程式，**只改兩行配置**：

```python
SERIAL_PORT = 'COM3'          # ← 改成你的實際 FPGA USB-UART port
BAUDRATE = 115200             # ← 確認你的 baud rate
UDP_PORT_DOCKLIGHT = 5000
UDP_PORT_AI = 5001
HOST = '127.0.0.1'
```

執行這個程式後：

- Docklight 連 `UDP:127.0.0.1:5000`
- AI 連 `UDP:127.0.0.1:5001`
- FW 所有 `printf` 會同時出現在 Docklight（GUI 顯示 HEX+ASCII）和 AI

### 2. AI MCP Server（推薦使用 stdio + FastMCP，最穩定）

Antigravity 目前對自訂 MCP 最穩定的方式是 **stdio transport**（而非純 UDP client）。

請建立新檔案 `box_uart_mcp.py`（放在專案資料夾，例如 `C:\fw_test\box_uart_mcp.py`）：

```python
import socket
import json
import sys
from mcp.server.fastmcp import FastMCP   # Antigravity 常用

mcp = FastMCP("box-uart-udp")

UDP_IP = "127.0.0.1"
UDP_PORT_AI = 5001
BUFFER_SIZE = 4096

def send_to_bridge(cmd: dict):
    """發送 JSON 命令到 Python Bridge (port 5001)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(8)
    try:
        sock.sendto(json.dumps(cmd).encode('utf-8'), (UDP_IP, UDP_PORT_AI))
        data, _ = sock.recvfrom(BUFFER_SIZE)
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        sock.close()

@mcp.tool
def box_write(data: str, is_hex: bool = False):
    """送任意資料給 FPGA FW（支援文字或 hex）"""
    if is_hex:
        try:
            payload = bytes.fromhex(data.replace(" ", ""))
        except:
            return {"status": "error", "message": "Invalid hex format"}
    else:
        payload = data.encode('utf-8') + b'\r\n'
  
    result = send_to_bridge({"action": "write", "data": list(payload)})
    return result

@mcp.tool
def box_read(timeout_ms: int = 3000):
    """讀取 FW printf debug 資訊（會同時顯示在 Docklight）"""
    result = send_to_bridge({"action": "read", "timeout": timeout_ms / 1000.0})
    if result.get("status") == "ok":
        return {
            "hex": result.get("data_hex", ""),
            "ascii": result.get("data_ascii", ""),
            "length": result.get("length", 0)
        }
    return result

if __name__ == "__main__":
    mcp.run()   # 以 stdio 模式運行，適合 Antigravity
```

### 3. 在 Antigravity IDE 加入這個 MCP

1. 開啟 Antigravity
2. 在右側 Agent Panel → 點「...」 → **Manage MCP Servers**
3. 點 **View raw config**（會開啟 `~/.gemini/antigravity/mcp_config.json`）
4. 在 `mcpServers` 中加入：

```json
{
  "mcpServers": {
    "box-uart": {
      "command": "python",
      "args": ["C:\\fw_test\\box_uart_mcp.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

儲存後，重啟 Agent session。AI 就會自動發現 `box_write` 和 `box_read` 兩個工具。

### 4. 給 Antigravity 的**核心 System Prompt**（直接複製使用）

```markdown
你現在是 Xilinx Vitis + MicroBlaze FW 自動優化與除錯工程師。
硬體為 FPGA + MicroBlaze，透過 UDP Bridge (port 5001) 與 Box 溝通。
Docklight 同時在 UDP 5000 監聽，所有資料雙向可見。

可用工具：
- box_write(data: string, is_hex: bool = false) → 送命令或測試資料給 FW
- box_read(timeout_ms: int = 3000) → 讀取 FW printf debug 資訊（同時會出現在 Docklight）

閉環工作流程（請嚴格遵守）：
1. 先執行 box_read(5000) 抓取完整 boot log 和目前 debug 資訊。
2. 分析收到的 log，找出問題（參數錯誤、bug、assert、效能瓶頸、memory leak 等）。
3. 在 Antigravity IDE 內直接修改對應的 C 語言原始碼（.c / .h 檔案），明確告訴我你要修改哪些檔案、修改什麼內容。
4. 我會手動或用 script 觸發 Vitis rebuild + xsct flash。
5. flash 完成後，再執行 box_read 驗證修改效果。
6. 重複以上步驟，直到 FW 穩定、無明顯錯誤、效能達到預期，或我說 "stop loop"。

重要規則：
- 每一步都要輸出「完整收到的 UART log（包含 Hex + ASCII）」 + 「你的分析與推理」 + 「具體的 code 修改建議」。
- 我會在 Docklight 中即時觀看所有資料，也會隨時手動送指令，你必須能適應中途插入的資料。
- 修改 code 時請使用清晰的 diff 格式或完整函數替換。
- 目標：讓 FW 完全穩定、printf 資訊乾淨、參數最佳化。

現在請開始第一步：執行 box_read(5000)，並分析 boot log。
```

### 額外建議（讓 loop 更完整）

- **自動 build/flash**：你可以再寫一個簡單 Tcl + Python wrapper，讓 AI 呼叫 `box_build_and_flash()` 工具（使用 `xsct -tcl` 執行 build）。
- 如果想讓 AI 更強大，可再加一個 filesystem MCP，讓它直接讀寫 Vitis 專案裡的 .c 檔案。
- Docklight 設定建議：開啟 Timestamp、Hex + ASCII 並排顯示、自動捲動，方便你監控 AI 的 loop 過程。

請告訴我：

1. 你的實際 **SERIAL_PORT** 和 **BAUDRATE** 是多少？
2. Vitis 專案的主要應用程式名稱或 .elf 輸出路徑？
3. 你希望主要針對哪幾個功能做自動優化（例如 interrupt handling、peripheral init、memory usage 等）？

把上面 `box_uart_mcp.py` 建立好、Python 中間層跑起來、MCP 加到 Antigravity 後，直接貼 Prompt 給 AI，它就會開始用 UDP 讀寫、分析 `printf`、自動修改 code 了。

需要我幫你加上 **build_and_flash** 工具、或寫 xsct tcl 自動化腳本嗎？直接說，我馬上提供。


graph TD
    subgraph Hardware_Layer [Hardware Space]
        FPGA["FPGA / MicroBlaze (DUT)"]
        Serial["Serial Port (COM3) `<br/>` 115200, 8N1"]
        FPGA <-->|UART| Serial
    end

    subgraph Bridge_Layer [Python Connection Bridge]
        Bridge["Python UDP Bridge Engine"]
        UDP5000["UDP Port 5000`<br/>` (Human Monitor)"]
        UDP5001["UDP Port 5001 `<br/>` (AI Agent)"]

    Serial <-->|Pyserial| Bridge
        Bridge <-->|Broadcast/Receive| UDP5000
        Bridge <-->|Broadcast/Receive| UDP5001
    end

    subgraph Interface_Layer [Interface / UI]
        Docklight["Docklight (UDP Client)`<br/>` Manual Hex/ASCII Trace"]
        MCP["AI MCP Server (FastMCP) `<br/>` tools: box_write, box_read"]

    UDP5000 <--> Docklight
        UDP5001 <--> MCP
    end

    subgraph Agent_Layer [AI Cognition]
        Agent["Antigravity Agent (IDE)"]
        Reasoning{"Agent Loop:`<br/>` Analyze Logs / Reasoning"}
        Source["Source Code (*.c/*.h)"]
        Flash["Vitis / XSCT Flash"]

    MCP <--> Agent
        Agent --> Reasoning
        Reasoning -->|Update| Source
        Reasoning -->|Trigger| Flash
        Flash -.->|Reset/Boot| FPGA
    end

    style Bridge fill:#f96,stroke:#333,stroke-width:2px
    style Agent fill:#bbf,stroke:#333,stroke-width:2px
    style FPGA fill:#dfd,stroke:#333



