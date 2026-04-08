import os
import sys
import argparse
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GDriveSync:
    def __init__(self, credentials_path):
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"找不到認證檔案: {credentials_path}")
        
        # 使用 Service Account 認證
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path, 
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        self.service = build('drive', 'v3', credentials=self.creds)

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

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Google Drive 同步工具")
    parser.add_argument("--file", required=True, help="要上傳的本地檔案路徑")
    parser.add_argument("--folder", help="目標 Google Drive 資料夾 ID (選填)")
    parser.add_argument("--creds", default=".env/gdrive_creds.json", help="Service Account JSON 路徑")
    
    args = parser.parse_args()

    try:
        sync = GDriveSync(args.creds)
        sync.upload_file(args.file, args.folder)
    except Exception as e:
        logger.error(f"初始化失敗: {e}")
        print("\n[TIP] 請確保您已依照 KNOWLEDGE_BASE_SOP.md 申請 Service Account 並將 JSON 放入指定位置。")

if __name__ == "__main__":
    main()
