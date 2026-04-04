import json
import logging
import os
import sys
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AA-Bridge 啟動成功 | 監聽 http://127.0.0.1:%s", BRIDGE_PORT)
    yield
    logger.info("🛑 AA-Bridge 正在關閉...")

app = FastAPI(title="AA-Bridge - Antigravity IDE Proxy", lifespan=lifespan)

# ====================== 核心：呼叫 Antigravity IDE AI ======================
async def call_antigravity_ide(prompt: str, session_key: str, model: str = "ide-brain") -> AsyncGenerator[str, None]:
    """
    實作 IDE 大腦共享：
    1. 優先從環境變數 GEMINI_API_KEY 獲取 IDE 的 AI 能力。
    2. 未來可擴展為直接呼叫 IDE 的內部 RPC。
    """
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            yield "❌ [AA-Bridge] 錯誤：在 IDE 環境中未偵測到 GEMINI_API_KEY。\n請確保 Antigravity IDE 已正確啟動並配置 AI 能力。"
            return

        # 使用 Google Gemini API 模擬 IDE 大腦回覆
        # (這裡使用的是 IDE 共享出來的憑證)
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    yield f"❌ IDE AI 調用失敗 (HTTP {response.status_code})"
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "): # 處理 SSE 或 Google 格式
                        continue
                    try:
                        chunk = json.loads(line)
                        if "candidates" in chunk:
                            text = chunk["candidates"][0]["content"]["parts"][0]["text"]
                            yield text
                    except:
                        continue

    except Exception as e:
        logger.error("IDE AI 呼叫失敗: %s", e)
        yield f"\n❌ AA-Bridge 內部錯誤：{str(e)}\n"

# ====================== OpenAI 格式處理器 ======================
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    headers = dict(request.headers)
    
    session_key = headers.get("x-openclaw-session-key", "unknown")
    model = body.get("model", "ide-brain")
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    logger.info("📨 Request | session=%s | model=%s", session_key[:8], model)

    if not stream:
        full_text = ""
        async for chunk in call_antigravity_ide(user_message, session_key, model):
            full_text += chunk
        return JSONResponse({
            "id": f"chatcmpl-{int(datetime.now().timestamp())}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": model,
            "choices": [{"message": {"role": "assistant", "content": full_text}, "finish_reason": "stop"}]
        })

    async def generate():
        async for text in call_antigravity_ide(user_message, session_key, model):
            yield f"data: {json.dumps({'choices': [{'delta': {'content': text}, 'finish_reason': None}]})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=BRIDGE_PORT)
