import base64
import json
import logging
import httpx
from io import BytesIO
from typing import Tuple, Optional
from PIL import Image

logger = logging.getLogger("RVA.VisionClient")

class RVAVisionClient:
    def __init__(self, bridge_port: int = 18800):
        self.bridge_url = f"http://127.0.0.1:{bridge_port}/v1beta/models/gemini-3-flash-vision:generateContent"
        
        self.SYSTEM_PROMPT = """
You are a robotic automation vision sensor. 
Your only task is to locate the target element in the provided screenshot.
Return ONLY valid JSON matching this schema exactly:
{
  "bbox": [ymin, xmin, ymax, xmax]
}
Where values are normalized floats between 0.0 and 1.0. 
If the target is not found, return {"bbox": null}.
No markdown, no explanation. Just JSON.
"""

    def prepare_image(self, img: Image.Image) -> str:
        """
        Compress image if it's too large, but preserve PNG structure to avoid JPEG artifacts.
        Scale down so the max dimension is 1440px to balance tokens vs precision for dense IDEs.
        """
        max_dim = 1440
        if img.width > max_dim or img.height > max_dim:
            ratio = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        buf = BytesIO()
        # Save as PNG to avoid artifacts on small fonts
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    async def find_target_bbox(self, image: Image.Image, target_query: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Send image and query to local aa-bridge relay, expect [ymin, xmin, ymax, xmax] back.
        """
        b64_img = self.prepare_image(image)
        
        prompt = f"{self.SYSTEM_PROMPT}\nTarget to find: '{target_query}'"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": b64_img}}
                ]
            }]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.bridge_url, json=payload)
                if resp.status_code != 200:
                    logger.error(f"Vision Bridge error: {resp.status_code} - {resp.text}")
                    return None
                
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Cleanup potential markdown ticks if model hallucinates them
                text = text.replace("```json", "").replace("```", "").strip()
                
                result = json.loads(text)
                bbox = result.get("bbox")
                
                if not bbox or len(bbox) != 4:
                    return None
                    
                # bbox is ymin, xmin, ymax, xmax
                return (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
                
        except Exception as e:
            logger.error(f"Failed to query Vision Client: {e}")
            return None
