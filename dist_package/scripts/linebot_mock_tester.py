import os
import sys
import logging

# 模擬 LineBot 整合環境
logging.basicConfig(level=logging.INFO, format='[LineBot-Mock] %(message)s')
logger = logging.getLogger(__name__)

class LineBotIntegrator:
    def __init__(self):
        self.tags = ["#教學", "#技術", "#生活"]
        logger.info("初始化 LineBot 整合器... [OK]")

    def handle_message(self, user_id, message_text):
        """模擬收到的訊息處理"""
        logger.info(f"收到來自用戶 {user_id} 的訊息: \"{message_text}\"")
        
        # 1. 解析標籤
        tag_found = None
        for tag in self.tags:
            if message_text.startswith(tag):
                tag_found = tag
                break
        
        if tag_found:
            clean_text = message_text.replace(tag_found, "").strip()
            logger.info(f"🔍 偵測到分類標籤: {tag_found}")
            self.send_to_gdrive(clean_text, tag_found)
        else:
            logger.info("ℹ️ 無標籤訊息，視為一般對話。")

    def send_to_gdrive(self, content, category):
        """模擬傳送至 Google Drive"""
        logger.info(f"🚀 [整合測試] 正在呼叫 kb_gdrive_sync.py...")
        logger.info(f"📂 目標資料夾: Google Drive -> AutoAgent_KB -> {category[1:]}")
        logger.info(f"📄 儲存內容摘要: {content[:30]}...")
        logger.info("✅ 模擬同步成功！")

def main():
    print("="*50)
    print("AutoAgent-TW: LineBot 知識庫整合實戰 Demo")
    print("="*50)
    
    bot = LineBotIntegrator()
    
    # 測試情境 1: 帶有標籤的訊息
    bot.handle_message("U12345", "#教學 如何在 Windows 建立 Python 虛擬環境？")
    
    print("-" * 30)
    
    # 測試情境 2: 無標籤訊息
    bot.handle_message("U12345", "你今天好嗎？")
    
    print("-" * 30)
    
    # 測試情境 3: 技術類標籤
    bot.handle_message("U67890", "#技術 Docker Container 部署腳本範例")

    print("\n[Tom 的架構筆記]:")
    print("- 此 Demo 展示了標籤解析與流程路由 (Routing) 的核心邏輯。")
    print("- 實際環境只需將 handle_message 放入 Flask 的 /callback 路由即可。")

if __name__ == "__main__":
    main()
