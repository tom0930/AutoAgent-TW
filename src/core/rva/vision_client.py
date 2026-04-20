import base64
import json
import logging
import httpx
from io import BytesIO
from typing import Tuple, Optional, Dict, Any
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
        Compress image if it's too large. Using JPEG for transport to minimize payload size.
        """
        max_dim = 1440
        if img.width > max_dim or img.height > max_dim:
            ratio = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if it has alpha channel (JPEG doesn't support RGBA)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        buf = BytesIO()
        # Quality 85 is the sweet spot for vision models
        img.save(buf, format="JPEG", quality=85)
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close() # Explicitly close buffer
        return b64_str

    async def verify_action_result(self, before_img: Image.Image, after_img: Image.Image, expected_outcome: str) -> Dict[str, Any]:
        """
        Compare two images to judge if the RVA action achieved the expected goal.
        Returns: {"success": bool, "dx": int, "dy": int, "reason": str}
        """
        # Compress both images
        b64_before = self.prepare_image(before_img)
        b64_after = self.prepare_image(after_img)
        
        prompt = f"""
{self.SYSTEM_PROMPT}
Evaluate the result of a UI automation action.
Before image provided. After image provided.
Expected Goal: '{expected_outcome}'

Compare 'before' vs 'after'. 
Did the specific change occur? If it failed or was offset, estimate the pixel correction needed.

Return ONLY valid JSON:
{{
  "success": true/false,
  "reason": "description of what happened",
  "dx": estimated_x_correction_pixels, 
  "dy": estimated_y_correction_pixels
}}
"""
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": b64_before}},
                    {"inline_data": {"mime_type": "image/png", "data": b64_after}}
                ]
            }]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.bridge_url, json=payload)
                if resp.status_code != 200:
                    return {"success": False, "reason": f"Retry: Vision Bridge Error {resp.status_code}", "dx":0, "dy":0}
                
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
        except Exception as e:
            return {"success": False, "reason": str(e), "dx": 0, "dy": 0}

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
    async def reason_from_image(self, image: Image.Image, question: str) -> str:
        """
        Ask a semantic question about the UI state based on the image.
        Used for general 'AI Vision-based' reasoning.
        """
        b64_img = self.prepare_image(image)
        
        prompt = f"""
You are a senior UI analyst and robotic automation expert.
Visual context: A screenshot of a desktop application.
Task: {question}

Return a concise, factual summary or the specific answer needed for automation.
"""
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
                    return f"Vision Error: {resp.status_code}"
                
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return text.strip()
        except Exception as e:
            return f"Vision Exception: {str(e)}"
