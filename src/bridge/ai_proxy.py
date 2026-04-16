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
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

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
async def call_antigravity_ide(prompt: str, session_key: str, model: str = "gemini-3-flash") -> AsyncGenerator[str, None]:
    """
    對接截圖所示的本地 Antigravity Tools (Port 8045):
    """
    try:
        local_token = os.environ.get("IDE_LOCAL_TOKEN") or os.environ.get("LANGSMITH_API_KEY")
        if not local_token:
            yield "❌ [AA-Bridge] 錯誤：在 .env 中未找到 IDE_LOCAL_TOKEN (sk-...)。"
            return

        headers = {
            "Authorization": f"Bearer {local_token}",
            "Content-Type": "application/json"
        }
        
        # 截圖 1 顯示 Gemini 3 Flash 配額充足，我們對接到本機端的 OpenAI 相容接口
        url = "http://127.0.0.1:8045/v1/chat/completions"
        payload = {
            "model": model if model != "ide-brain" else "gemini-3-flash",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    yield f"❌ 本機服務 (8045) 調用失敗: HTTP {response.status_code} - {response.text}"
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]
                        if line == "[DONE]": break
                        try:
                            chunk = json.loads(line)
                            if "choices" in chunk and "delta" in chunk["choices"][0]:
                                text = chunk["choices"][0]["delta"].get("content", "")
                                if text: yield text
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

# ====================== Gemini 格式處理器 (Relay) ======================
@app.post("/v1beta/models/{model_path}:generateContent")
async def gemini_relay(model_path: str, request: Request):
    """
    Gemini 視覺轉發器：將 RVA Engine 的截圖轉發給本地 Port 8045
    """
    local_token = os.environ.get("IDE_LOCAL_TOKEN") or os.environ.get("LANGSMITH_API_KEY")
    if not local_token:
        return JSONResponse({"error": "No IDE_LOCAL_TOKEN found"}, status_code=500)
    
    body = await request.json()
    
    # 轉換 Gemini 格式為 OpenAI 格式 (帶 Vision)
    # 擷取 prompt 與 base64
    try:
        parts = body['contents'][0]['parts']
        prompt = next((p['text'] for p in parts if 'text' in p), "")
        image_data = next((p['inline_data']['data'] for p in parts if 'inline_data' in p), None)
        
        openai_payload = {
            "model": "gemini-3-flash", # 使用截圖中的正式型號
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }
        
        if image_data:
            openai_payload["messages"][0]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
            })
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {local_token}"}
            logger.info("📡 Forwarding Vision request to Port 8045 | Model: google/gemini-3-flash")
            
            try:
                response = await client.post("http://127.0.0.1:8045/v1/chat/completions", headers=headers, json=openai_payload)
                logger.info("📥 Port 8045 Response: %s", response.status_code)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result['choices'][0]['message']['content']
                    logger.info("✅ Vision Relay Success | Extracted: %s", text[:50])
                    return JSONResponse({
                        "candidates": [{"content": {"parts": [{"text": text}]}}]
                    })
                elif response.status_code == 503 and "disabled" in response.text.lower():
                    logger.error("❌ Port 8045 禁用中。修復建議：請在本機 IDE 控制台按一下 [Enable Proxy] 按鈕。")
                    return JSONResponse({"error": "Proxy disabled. Please click [Enable Proxy] in IDE."}, status_code=503)
                else:
                    logger.error("❌ Vision Relay Failed: HTTP %s | Body: %s", response.status_code, response.text[:100])
                    return JSONResponse({"error": f"Upstream Error: {response.status_code}"}, status_code=response.status_code)
            except httpx.ConnectError:
                logger.error("❌ 無法連接到 Port 8045。")
                return JSONResponse({"error": "Connection to local AI (8045) failed"}, status_code=502)


                
    except Exception as e:
        return JSONResponse({"error": f"Relay logic error: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    # 確保日誌目錄存在
    os.makedirs("logs", exist_ok=True)
    uvicorn.run(app, host="127.0.0.1", port=BRIDGE_PORT)
