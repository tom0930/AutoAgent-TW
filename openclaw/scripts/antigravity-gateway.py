import uvicorn
import logging
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# =================================================================
# Antigravity Mock Gateway v2.0
# Author: Tom - Senior System Architect
# Purpose: Bypass Cloud-Code Auth & Real-time AI Reasoning Bridge
# =================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ag-gateway")

app = FastAPI(title="Antigravity Mock Gateway")

# -----------------------------------------------------------------
# 1. 驗證偽裝端點 (Auth Mocking)
# -----------------------------------------------------------------

@app.post("/v1internal:fetchUserInfo")
async def fetch_user_info(request: Request):
    logger.info("📡 Intercepted fetchUserInfo request")
    return {
        "user": {
            "email": "tom@openclaw.ai",
            "displayName": "Tom (Senior Architect)",
            "photoUrl": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom"
        },
        "status": "AUTHENTICATED",
        "roles": ["OWNER", "BILLING_ADMIN"],
        "quotas": {
            "tokenLimit": 1000000,
            "requestsPerMinute": 1000
        }
    }

@app.post("/v1internal:loadCodeAssist")
async def load_code_assist(request: Request):
    logger.info("📡 Intercepted loadCodeAssist request")
    return {
        "authorized": True,
        "featureFlags": {
            "enableThinking": True,
            "enablePro": True,
            "enableLocalIndexing": True
        }
    }

@app.post("/v1internal:fetchAdminControls")
async def fetch_admin_controls(request: Request):
    logger.info("📡 Intercepted fetchAdminControls request")
    return {
        "adminControls": {
            "enableCloudCode": True,
            "enableGemini": True,
            "requireLogin": False
        }
    }

@app.get("/v1/people/me")
@app.get("/v1/peopleInfo")
async def get_people_info(request: Request):
    logger.info("📡 Intercepted peopleInfo request")
    return {
        "names": [{"displayName": "Tom (Senior Architect)"}],
        "emailAddresses": [{"value": "tom@openclaw.ai"}]
    }

# -----------------------------------------------------------------
# 2. 推理轉發邏輯 (AI Reasoning Bridge)
# -----------------------------------------------------------------

def transform_google_to_generic(payload: dict):
    """將 Google Gemini 格式轉換為通用 Message 格式"""
    messages = []
    for content in payload.get("contents", []):
        role = "user" if content.get("role") == "user" else "assistant"
        parts = content.get("parts", [])
        text = "".join([p.get("text", "") for p in parts if "text" in p])
        messages.append({"role": role, "content": text})
    return messages

@app.post("/v1beta/models/{model}:streamGenerateContent")
@app.post("/v1/models/{model}:streamGenerateContent")
async def streaming_generate_content(model: int | str, request: Request):
    """
    處理 IDE 的推理請求，目前先實作 Mock 串流驗證管道
    """
    payload = await request.json()
    messages = transform_google_to_generic(payload)
    logger.info(f"🧠 Reasoning Request (Model: {model}) | Last Prompt: {messages[-1]['content'][:50]}...")

    async def mock_stream_generator():
        # TODO: 未來在此處發送請求至 OpenClaw Core (Task 2.3)
        mock_response = [
            "Hello! I am your local Antigravity Bridge. ",
            "I have detected your request and I am currently processing it ",
            "without sending any data to Google's servers. ",
            "\n\n**System Status:** Local Gateway Active 🛡️",
        ]
        
        for part in mock_response:
            # Google SSE 格式: [{"candidates": [{"content": {"parts": [{"text": "..."}]}}]}]
            chunk = {
                "candidates": [{
                    "content": {
                        "parts": [{"text": part}]
                    },
                    "finishReason": "STOP" if part == mock_response[-1] else None
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(mock_stream_generator(), media_type="text/event-stream")

@app.post("/v1beta/models/{model}:generateContent")
@app.post("/v1/models/{model}:generateContent")
async def generate_content(model: int | str, request: Request):
    """處理非串流推理請求"""
    payload = await request.json()
    messages = transform_google_to_generic(payload)
    logger.info(f"🧠 Non-streaming Request (Model: {model})")
    
    response_text = "I am Antigravity Mock Gateway (Non-streaming mode). Local processing active."
    return {
        "candidates": [{
            "content": {"parts": [{"text": response_text}]},
            "finishReason": "STOP"
        }]
    }

# -----------------------------------------------------------------
# 3. 未知路徑轉發 (Fallback Proxy)
# -----------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "bridge-v2"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def universal_proxy(path: str, request: Request):
    logger.warning(f"🏗️ Unhandled Proxy Path: {path}")
    return JSONResponse(
        status_code=501,
        content={"error": "Proxy path not implemented yet", "path": path}
    )

if __name__ == "__main__":
    logger.info("🚀 Antigravity Gateway v2.0 is starting on http://127.0.0.1:18788")
    uvicorn.run(app, host="127.0.0.1", port=18788)
