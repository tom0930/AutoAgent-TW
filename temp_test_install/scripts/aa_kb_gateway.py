import os
import sys

# Windows 終端機 Emoji 輸出修正
if sys.platform == "win32":
    # 嘗試重新配置 stdout，若 stdout 被導向可能不支援 reconfigure
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

import logging
import argparse
import subprocess
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from kb_gdrive_sync import GDriveSync, RcloneSync

try:
    # pyrefly: ignore [missing-import]
    import google.generativeai as genai
except ImportError:
    genai = None

# 載入環境變數
load_dotenv()

# 設定路由策略 (api | rclone)
KB_SYNC_MODE = os.environ.get("KB_SYNC_MODE", "rclone")
RCLONE_REMOTE = os.environ.get("RCLONE_REMOTE", "gdrive")
LOCAL_TEMP_DIR = os.environ.get("KB_TEMP_DIR", "data/kb_upload_queue")

# 確保暫存目錄存在
if not os.path.exists(LOCAL_TEMP_DIR):
    os.makedirs(LOCAL_TEMP_DIR)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='[LineBot-Gateway] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeBaseGateway:
    def __init__(self):
        logger.info("初始化知識庫閘道器 (Gateway)...")
        # 讀取白名單 (逗號分隔)
        whitelist_str = os.environ.get("LINE_ADMIN_UID_LIST", "pcvdep0101@gmail.com,U12345")
        self.whitelist = [uid.strip() for uid in whitelist_str.split(",") if uid.strip()]
        
        self.notebook_id = os.environ.get("NLM_TARGET_NOTEBOOK_ID", "")
        self.credentials_path = os.environ.get("GDRIVE_CREDS_PATH", ".env/gdrive_creds.json")
        
        # 初始化 Gemini OCR (若有設定 API Key)
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        if self.gemini_api_key and genai:
            genai.configure(api_key=self.gemini_api_key)
            self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.vision_model = None

    def verify_whitelist(self, user_id):
        """實作白名單驗證 (Zero-Cost 防禦)"""
        if user_id not in self.whitelist:
            logger.warning(f"❌ 阻擋未獲授權的使用者操作: {user_id}")
            return False
        return True

    def process_message(self, user_id, text_content=None, image_path=None):
        """核心處理發動點"""
        # 第一層保護：白名單
        if not self.verify_whitelist(user_id):
            return "❌ 無操作權限"

        if text_content and text_content.startswith("@大腦"):
            # 【查詢流】
            query = text_content.replace("@大腦", "").strip()
            return self._handle_query(query)

        elif text_content and text_content.startswith("#知識庫"):
            # 【文字匯入流】
            content = text_content.replace("#知識庫", "").strip()
            return self._handle_sync_text(content, f"Line知識分享_{user_id}.txt")

        elif image_path:
            # 【影像圖片匯入流】
            logger.info("偵測到圖片上傳，啟動 OCR 流程...")
            return self._handle_sync_image(image_path, f"Line圖片上傳_{user_id}")
        
        else:
             logger.info("ℹ️ 略過無關訊息不發送給 AI (防禦機制啟動)")
             return None

    def _handle_query(self, query):
        """透過 subprocess 呼叫 NotebookLM CLI 查詢大腦"""
        if not self.notebook_id:
             return "❌ NLM_TARGET_NOTEBOOK_ID 未設定"
             
        logger.info(f"🧠 發送查詢至 NotebookLM: {query}")
        try:
             # 注意：需要環境已經執行過 `nlm login`
             result = subprocess.run(
                 ["nlm", "notebook", "query", self.notebook_id, query],
                 capture_output=True,
                 text=True,
                 check=True
             )
             # 若成功，回傳輸出內容
             return result.stdout.strip()
        except subprocess.CalledProcessError as e:
             logger.error(f"❌ 查詢失敗: {e.stderr}")
             return "❌ 大腦連線失敗，請維護員確認 nlm session 狀態。"
        except Exception as e:
             logger.error(f"❌ 未知錯誤: {e}")
             return "❌ 系統異常"

    def _handle_sync_text(self, text_content, filename):
        """將純文字拋上 Drive 並同步 NotebookLM"""
        # 1. 寫入 Drive
        drive_file_id = self._upload_to_drive_as_text(text_content, filename)
        if not drive_file_id:
            return "❌ 上傳 Drive 失敗"
            
        # 2. 同步 NLM
        return self._sync_drive_to_nlm(drive_file_id)

    def _handle_sync_image(self, image_path, base_filename):
        """OCR 解析圖片變為文字，然後同步"""
        if not self.vision_model:
             logger.error("❌ Gemini API 未就緒，無法進行圖片解析。")
             return "❌ 系統缺乏視覺解析能力"
             
        # 進行 OCR
        logger.info("👁️ 進行圖片文字擷取...")
        try:
            try:
                import PIL.Image
            except ImportError:
                logger.warning("⚠️ 未安裝 Pillow 影像處理套件")
                return "⚠️ 此環境未安裝影像處理套件 (可選)"
                
            img = PIL.Image.open(image_path)
            # 必須非常精準的 Prompt，不讓他擴寫廢話
            response = self.vision_model.generate_content([
                "請擷取這張圖片中的所有重點文字，保留排版，不要加上任何您自己的問候與描述解讀。", 
                img
            ])
            ocr_text = response.text
             
            # 將結果轉為純文字放上 GDrive
            return self._handle_sync_text(ocr_text, f"{base_filename}_OCR 解析.txt")
            
        except Exception as e:
            logger.error(f"❌ 圖片解析失敗: {e}")
            return "❌ 圖片無法辨識"

    def _upload_to_drive_as_text(self, text, filename):
        """將文字儲存並同步到 Google Drive (支援 API 或 Rclone)"""
        # 1. 無論如何先存本地 (作為緩衝與紀錄)
        temp_path = os.path.join(LOCAL_TEMP_DIR, filename)
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"💾 已儲存本地快取: {temp_path}")
        except Exception as e:
            logger.error(f"❌ 本地快取寫入失敗: {e}")
            return None

        # 2. 根據模式進行同步
        if KB_SYNC_MODE == "rclone":
            rclone = RcloneSync(remote_name=RCLONE_REMOTE)
            if rclone.sync_file(temp_path):
                return f"rclone://{filename}" # 返回一個虛擬 ID 代表成功
            return None
        else:
            # 原有的 API 模式 (需要 Service Account)
            try:
                sync = GDriveSync(self.credentials_path)
                return sync.upload_text_as_file(text, filename)
            except ImportError as e:
                logger.warning(f"⚠️ 缺乏同步元件: {e}")
                return "⚠️ 此環境未安裝上傳套件 (可選)"
            except Exception as e:
                logger.error(f"❌ Drive 物件建立失敗: {e}")
                return None

    def _sync_drive_to_nlm(self, file_id):
        """呼叫 subprocess 執行 source add"""
        if not self.notebook_id:
             return "❌ NLM_TARGET_NOTEBOOK_ID 未設定"
             
        # 針對 Rclone 模式的處理
        if isinstance(file_id, str) and file_id.startswith("rclone://"):
             filename = file_id.replace("rclone://", "")
             local_path = os.path.join(LOCAL_TEMP_DIR, filename)
             logger.info(f"🔄 Rclone 模式：檔案已同步至雲端，嘗試同時新增本地備份至 NLM (Path: {local_path})")
             try:
                 subprocess.run(
                     ["nlm", "source", "add", self.notebook_id, "--file", local_path],
                     capture_output=True, text=True, check=True
                 )
                 return "✅ [Rclone] 雲端同步完成並已收錄本地備份"
             except Exception:
                 return "✅ [Rclone] 雲端同步完成 (本地 NLM 連結跳過)"

        logger.info(f"🔄 發送同步指令至 NotebookLM (Drive ID: {file_id})")
        try:
             subprocess.run(
                 ["nlm", "source", "add", self.notebook_id, "--drive", file_id],
                 capture_output=True,
                 text=True,
                 check=True
             )
             logger.info("✅ 同步至 NotebookLM 成功!")
             return "✅ 已收錄至知識大腦"
        except subprocess.CalledProcessError as e:
             logger.error(f"❌ NLM 同步指令失敗: {e.stderr}")
             return "❌ 收錄失敗，請確認 nlm 指令狀態"

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW: LineBot 閘道器測試工具")
    parser.add_argument("--test-text", action="store_true", help="測試文字查詢與拒絕機制作為")
    parser.add_argument("--test-sync", action="store_true", help="測試把文字同步拋上 GDrive 和 NLM")
    
    args = parser.parse_args()
    
    gateway = KnowledgeBaseGateway()
    
    # 這裡我們模擬 `pcvdep0101@gmail.com` 作為管理員進行測試
    test_uid = "pcvdep0101@gmail.com"
    
    print("="*60)
    print("LineBot x Google Drive x NotebookLM (Phase 133) 實作展示")
    print("="*60)
    
    if args.test_text:
        print("\n[測試 情境 1]: 無權限用戶胡亂要求")
        res = gateway.process_message("HackerX", "@大腦 公司明年的財務計畫是？")
        print(f"結果: {res}")
        
        print("\n[測試 情境 2]: 管理員一般閒聊 (不吃 Token)")
        res = gateway.process_message(test_uid, "今天晚餐吃什麼？")
        print(f"結果: {res}") # None
        
        print("\n[測試 情境 3]: 開發人員正確呼叫大腦查詢")
        # 如果終端機尚未 nlm login 或未設定 NLM_TARGET_NOTEBOOK_ID，這裡會被接住秀錯誤。
        res = gateway.process_message(test_uid, "@大腦 什麼是 GSD 工作流？")
        print(f"結果:\n{res}")
        
    elif args.test_sync:
        print("\n[測試 情境 4]: 開發人員餵食大腦新的知識")
        res = gateway.process_message(test_uid, "#知識庫 數位員工系統分為三層：底層、代理層、視覺層。")
        print(f"結果: {res}")
        
    else:
        print("💡 請加上 --test-text 或 --test-sync 來測試特定情境。")

if __name__ == "__main__":
    main()
