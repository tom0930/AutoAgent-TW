import os
import argparse
import logging
import io
import subprocess

try:
    # pyrefly: ignore [missing-import]
    from google.oauth2 import service_account
    # pyrefly: ignore [missing-import]
    from googleapiclient.discovery import build
    # pyrefly: ignore [missing-import]
    from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RcloneSync:
    """使用 Rclone 進行本地與雲端同步 (推薦本地開發使用)"""
    def __init__(self, remote_name="gdrive"):
        self.remote_name = remote_name
        # 檢查 rclone 是否可用
        try:
            subprocess.run(["rclone", "version"], capture_output=True, check=True)
            self.available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.available = False
            logger.warning("⚠️ Rclone 未安裝或未加入環境變數 (PATH)")

    def sync_file(self, local_path, remote_path="LineBot_Knowledge/"):
        """使用 rclone copy 將本地檔案同步到雲端"""
        if not self.available:
            logger.error("❌ Rclone 不可用，請先安裝 Rclone 並執行 rclone config")
            return False
            
        target = f"{self.remote_name}:{remote_path}"
        logger.info(f"🔄 Rclone 同步中: {local_path} -> {target}")
        
        try:
            # rclone copy <src> <dest>
            subprocess.run(["rclone", "copy", local_path, target], check=True)
            logger.info("✅ Rclone 同步完成!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Rclone 指令失敗: {e}")
            return False

class GDriveSync:
    def __init__(self, credentials_path=None):
        if not GDRIVE_AVAILABLE:
            raise ImportError("Google API 套件未安裝。如需使用 Drive 同步功能，請執行: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            
        if credentials_path and not os.path.exists(credentials_path):
            raise FileNotFoundError(f"找不到認證檔案: {credentials_path}")
        
        if credentials_path:
            # 使用 Service Account 認證
            self.creds = service_account.Credentials.from_service_account_file(
                credentials_path, 
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            self.service = build('drive', 'v3', credentials=self.creds)
        else:
             logger.warning("未提供認證檔案，GDriveSync 將無法工作。")

    def upload_file(self, file_path, folder_id=None):
        """上傳檔案至指定 Google Drive 資料夾"""
        file_name = os.path.basename(file_path)
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            logger.info(f"✅ 檔案已上傳! Drive ID: {file.get('id')}")
            return file.get('id')
        except Exception as e:
            logger.error(f"❌ 上傳失敗: {e}")
            return None

    def upload_text_as_file(self, text_content, file_name, folder_id=None):
        """將字串內容作為文字檔上傳至指定 Google Drive 資料夾"""
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # 將字串轉為 BytesIO 以供 MediaIoBaseUpload 讀取
        text_stream = io.BytesIO(text_content.encode('utf-8'))
        media = MediaIoBaseUpload(text_stream, mimetype='text/plain', resumable=True)

        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            logger.info(f"✅ 純文字檔已建立! Drive ID: {file.get('id')}")
            return file.get('id')
        except Exception as e:
            logger.error(f"❌ 文字檔建立失敗: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Google Drive 同步工具")
    parser.add_argument("--file", required=True, help="要上傳的本地檔案路徑")
    parser.add_argument("--folder", help="目標 Google Drive 資料夾 ID 或 Rclone 路徑")
    parser.add_argument("--mode", choices=["api", "rclone"], default="rclone", help="使用 Google API 或 Rclone")
    parser.add_argument("--creds", default=".env/gdrive_creds.json", help="Service Account JSON 路徑 (API 模式)")
    parser.add_argument("--remote", default="gdrive", help="Rclone 配置的名稱")
    
    args = parser.parse_args()

    if args.mode == "rclone":
        sync = RcloneSync(args.remote)
        sync.sync_file(args.file, args.folder or "LineBot_Knowledge/")
    else:
        try:
            sync = GDriveSync(args.creds)
            sync.upload_file(args.file, args.folder)
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            print("\n[TIP] API 模式需要 Service Account JSON。")

if __name__ == "__main__":
    main()

