以下是針對 **ClawIDE Phase 122** 量身打造的 **完整生產級 `ai_proxy.py`**（FastAPI 版本）。

這個版本已包含：
- **完整 OpenAI-compatible `/v1/chat/completions`**（含 streaming 支援）
- **錯誤處理 + 詳細 logging**
- **Session 隔離**（讀取 OpenClaw 傳來的 `x-openclaw-session-key`）
- **非阻塞 async**（支援多用戶同時使用）
- **可擴展的 `_call_antigravity_ide`**（目前 placeholder，方便你後續替換成真正 IDE 呼叫）
- **健康檢查端點** `/health`
- **結構化 logging**（適合 Windows 排程任務或 PM2）

### 1. 安裝依賴（推薦使用 uv 或 pip）
在 `Z:\autoagent-TW\src\bridge\` 目錄下執行：

```bash
uv add fastapi uvicorn[standard] httpx python-dotenv
# 或
pip install fastapi uvicorn[standard] httpx python-dotenv
```

### 2. 完整 `ai_proxy.py`（最終推薦版）

```python
"""
AA-Bridge: Antigravity IDE → OpenClaw AI Proxy (FastAPI 生產版)
監聽: http://127.0.0.1:18800
相容 OpenAI Chat Completions + Streaming
"""

import json
import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Dict, Any

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

# ====================== Logging 配置 ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("aa-bridge.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("aa-bridge")

# ====================== 配置 ======================
BRIDGE_PORT = 18800
IDE_AI_ENDPOINT = None  # 未來可改成 Antigravity IDE 的本地 API，例如 "http://127.0.0.1:19116/chat"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AA-Bridge 啟動成功 | 監聽 http://127.0.0.1:%s", BRIDGE_PORT)
    logger.info("Antigravity IDE Brain 橋接就緒 (目前使用 placeholder)")
    yield
    logger.info("🛑 AA-Bridge 正在關閉...")

app = FastAPI(title="AA-Bridge - Antigravity IDE Proxy", lifespan=lifespan)

# ====================== 健康檢查 ======================
@app.get("/health")
async def health():
    return {"status": "healthy", "bridge": "aa-bridge", "ide_connected": bool(IDE_AI_ENDPOINT)}

# ====================== 核心呼叫 IDE AI ======================
async def call_antigravity_ide(prompt: str, session_key: str, model: str = "ide-brain") -> AsyncGenerator[str, None]:
    """
    🔥 這裡替換成真正的 Antigravity IDE AI 呼叫方式
    優先推薦順序：
    1. IDE 暴露的本地 HTTP API (最優)
    2. 環境變數中的 Token + Google Generative AI SDK
    3. subprocess 呼叫 IDE CLI
    4. Electron IPC / JSON-RPC (如果可行)
    """
    try:
        # ==================== Placeholder（請替換這裡） ====================
        if False:  # 未來改成 True 並實作真實呼叫
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "http://127.0.0.1:YOUR_IDE_PORT/ai/chat",
                    json={"prompt": prompt, "session": session_key, "model": model},
                    timeout=120.0
                )
                resp.raise_for_status()
                async for chunk in resp.aiter_text():
                    if chunk.strip():
                        yield chunk
                return

        # 目前示範：直接回傳帶有 session 資訊的文字（可替換成 Gemini SDK 等）
        yield f"🧠 [Antigravity IDE Brain] Session: {session_key[:8]}... | Model: {model}\n\n"
        yield f"收到你的訊息：{prompt[:120]}{'...' if len(prompt) > 120 else ''}\n\n"
        
        # 模擬思考過程（可移除）
        for line in ["正在透過 Antigravity IDE 進行深度推理...", "已連接 IDE 上下文...", "生成中..."]:
            yield line + "\n"
            await asyncio.sleep(0.3)  # 模擬延遲

        yield "\n✅ 這是來自 Antigravity IDE 的回覆。\n請在 ai_proxy.py 中替換 call_antigravity_ide 實作真實呼叫。"

    except Exception as e:
        logger.error("IDE AI 呼叫失敗 | session=%s | error=%s", session_key[:8], e)
        yield f"\n❌ AA-Bridge 內部錯誤：{str(e)}\n"

import asyncio  # 在檔案頂端加入

# ====================== OpenAI Compatible Endpoint ======================
class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False
    temperature: float = 0.7
    max_tokens: int = 4096


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        headers = dict(request.headers)

        session_key = headers.get("x-openclaw-session-key", "unknown-session")
        model = body.get("model", "antigravity/ide-brain")
        messages = body.get("messages", [])
        stream = body.get("stream", False)

        # 提取最後一則 user 訊息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        logger.info("📨 收到請求 | session=%s | model=%s | stream=%s | prompt_len=%d",
                    session_key[:12], model, stream, len(user_message))

        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        if not stream:
            # 非串流模式（較少使用）
            full_response = ""
            async for chunk in call_antigravity_ide(user_message, session_key, model):
                full_response += chunk

            response = {
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": full_response},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": len(user_message)//4, "completion_tokens": len(full_response)//4, "total_tokens": 0}
            }
            return JSONResponse(content=response)

        # ====================== Streaming 模式 ======================
        async def generate_stream() -> AsyncGenerator[str, None]:
            try:
                async for text_chunk in call_antigravity_ide(user_message, session_key, model):
                    if text_chunk:
                        chunk_data = {
                            "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                            "object": "chat.completion.chunk",
                            "created": int(datetime.now().timestamp()),
                            "model": model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": text_chunk},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        await asyncio.sleep(0.01)  # 避免過快

                # 結束訊號
                yield 'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n\n'
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.exception("Streaming 過程中發生錯誤")
                error_chunk = {
                    "choices": [{"delta": {"content": f"\n\n❌ Bridge 錯誤: {str(e)}"}, "finish_reason": "stop"}]
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("chat/completions 處理失敗")
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "type": "aa_bridge_error"}}
        )


# ====================== 啟動入口 ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ai_proxy:app",
        host="127.0.0.1",
        port=BRIDGE_PORT,
        log_level="info",
        workers=1,          # Windows 下建議先用 1，後續可改 gunicorn + uvicorn workers
        timeout_keep_alive=120,
    )
```

### 3. 啟動腳本建議（`aa-bridge.cmd`）

```batch
@echo off
cd /d Z:\autoagent-TW\src\bridge
echo [AA-Bridge] 正在啟動 Antigravity IDE Proxy...
uvicorn ai_proxy:app --host 127.0.0.1 --port 18800 --log-level info
pause
```

### 4. 下一步建議
1. 把上面程式碼存成 `Z:\autoagent-TW\src\bridge\ai_proxy.py`
2. 先用 placeholder 測試 OpenClaw 是否能正常連線（不會再出現 API Key 錯誤）
3. 告訴我 **Antigravity IDE 目前實際呼叫 AI 的方式**（環境變數？本地 port？Extension API？Gemini SDK？），我再幫你精準替換 `call_antigravity_ide` 函式。
4. 之後可再加入 token 計數、速率限制、多模型 fallback 等進階功能。

這個版本已經可以直接用在你的 V240 安裝包裡，穩定性遠高於原本的 `http.server`。

需要我再幫你調整 `openclaw.json` 配置範例、installer 整合腳本，或是加入 LiteLLM 作為備援嗎？