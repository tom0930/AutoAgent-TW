import os
import base64
import json
import logging
import httpx
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field

# 設置日誌
logger = logging.getLogger("RVA_Vision")

class VisionCoordinate(BaseModel):
    """Gemini Vision 回傳的座標結構"""
    bbox: List[int] = Field(..., description="[ymin, xmin, ymax, xmax] 0-1000 normalized coordinates")
    label: str = Field(..., description="Target name")
    confidence: float = Field(0.0, description="Confidence score")

class GeminiVisionClient:
    """
    Antigravity Gemini Vision Client
    負責將螢幕截圖傳送至 Gemini Flash 進行 UI 元素定位。
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # 優先指向本地代理 (AA-Bridge)，如果沒 Key 則強制走代理
        if not self.api_key:
            self.api_url = "http://127.0.0.1:18800/v1beta/models/gemini-1.5-flash:generateContent"
            logger.info("RVA: Using local AA-Bridge proxy (No API Key detected).")
        else:
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            logger.info("RVA: Using direct Gemini API.")

    async def locate_element(self, image_path: str, target: str) -> Optional[VisionCoordinate]:
        """呼叫 Gemini Vision 定位元素"""
        # 修正：即使沒有 api_key 也要允許執行，因為可能正在使用本地橋接器 (AA-Bridge)

        # 1. 讀取截圖並進行 Base64 編碼
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # 2. 構建 Prompt
        prompt = f"""
        Please locate the UI element '{target}' in the provided screenshot.
        Return ONLY a JSON object with the following schema:
        {{
            "bbox": [ymin, xmin, ymax, xmax],
            "label": "{target}",
            "confidence": 0.95
        }}
        The bbox coordinates should be normalized (0-1000).
        If you cannot find it, return an empty JSON {{}}.
        """

        # 3. 準備 Payload
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
            }
        }

        # 4. 發送請求
        async with httpx.AsyncClient() as client:
            try:
                # 如果 URL 已經包含路徑參數或代理，直接使用
                url = self.api_url
                if self.api_key and "key=" not in url:
                    url = f"{url}?key={self.api_key}"
                
                response = await client.post(
                    url,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析結果 (Gemini 1.5 Flash 回傳結構)
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # 強健性：處理可能的 Markdown 程式碼區塊
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.replace("```", "").strip()
                
                data = json.loads(content)
                
                if "bbox" in data and data["bbox"]:
                    return VisionCoordinate(**data)
            except Exception as e:
                # pyrefly: ignore [unbound-name]
                logger.error(f"RVA: Gemini Vision API error: {e} | Content: {content[:100] if 'content' in locals() else 'None'}")
        
        return None

    def denormalize_coords(self, bbox: List[int], width: int, height: int) -> Tuple[int, int, int, int]:
        """
        將 0-1000 的正規化座標轉換為像素座標。
        [ymin, xmin, ymax, xmax] -> (left, top, right, bottom)
        """
        ymin, xmin, ymax, xmax = bbox
        left = int(xmin * width / 1000)
        top = int(ymin * height / 1000)
        right = int(xmax * width / 1000)
        bottom = int(ymax * height / 1000)
        return (left, top, right, bottom)
