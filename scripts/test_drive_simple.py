import os
import sys
import logging
from dotenv import load_dotenv

# 新增 scripts 路徑以載入自定義模組
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

try:
    from kb_gdrive_sync import GDriveSync
except ImportError:
    print("❌ 找不到 kb_gdrive_sync.py，請確保在專案根目錄執行此腳本。")
    sys.exit(1)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_drive_upload():
    load_dotenv()
    
    # 1. 取得認證路徑
    creds_path = os.environ.get("GDRIVE_CREDS_PATH", ".env/gdrive_creds.json")
    
    if not os.path.exists(creds_path):
        print(f"❌ 錯誤：找不到金鑰檔案於 {creds_path}")
        print("💡 請將 Google Service Account JSON 放入該路徑，或設定環境變數 GDRIVE_CREDS_PATH")
        return

    print("="*50)
    print("🚀 開始測試：本地檔案 -> Google Drive")
    print("="*50)

    try:
        # 2. 初始化同步物件
        sync = GDriveSync(creds_path)
        
        # 3. 執行測試上傳 (上傳一段測試文字)
        test_content = "這是一段從 AutoAgent-TW 傳出的實體測試文字，時間：" + os.popen('date /t').read().strip()
        filename = "AutoAgent_實測上傳.txt"
        
        print(f"正在上傳內容至：{filename}...")
        file_id = sync.upload_text_as_file(test_content, filename)
        
        if file_id:
            print(f"\n✅ 上傳成功！")
            print(f"📄 檔案名稱: {filename}")
            print(f"🆔 檔案 ID: {file_id}")
            print("\n💡 提示：請確保您已將目標資料夾共用給 Service Account 的 Email，")
            print("   這樣您才能在網頁版 Google Drive 看到這個檔案。")
        else:
            print("❌ 上傳失敗：未取得 File ID")

    except Exception as e:
        print(f"❌ 執行中發生錯誤: {e}")

if __name__ == "__main__":
    test_drive_upload()
