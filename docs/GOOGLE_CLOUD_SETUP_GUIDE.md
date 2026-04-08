# Google Cloud 憑證申請圖文教學 (Service Account 版)

本指南將引導您完成 Google Drive API 的金鑰申請，讓您的 AutoAgent 能夠具備「實體上傳」檔案至雲端硬碟的能力。

---

## 準備工作
*   一個有效的 Google 帳號。
*   已開啟的瀏覽器並登入 [Google Cloud Console](https://console.cloud.google.com/)。

---

## 第一步：建立新專案 (Project)
1.  點擊頁面左上角的「專案選單」。
2.  點擊「**新建專案 (New Project)**」。
    *   *圖示建議：尋找頂部藍色列的專案名稱旁的小箭頭。*
3.  輸入專案名稱（例如：`AutoAgent-KB-Sync`），點擊「建立」。

---

## 第二步：啟用 Google Drive API
1.  在左側選單中，選擇「**API 與服務**」 > 「**庫 (Library)**」。
2.  在搜尋框輸入：`Google Drive API`。
3.  選擇該 API，然後點擊「**啟用 (Enable)**」。
    *   *重要：若未啟用，即使有金鑰也無法上傳檔案。*

---

## 第三步：建立服務帳戶 (Service Account)
1.  在左側選單選擇「**IAM 與管理**」 > 「**服務帳戶**」。
2.  點擊頂部的「**+ 建立服務帳戶**」。
3.  輸入帳戶名稱（例如：`kb-uploader`），點擊「建立並繼續」。
4.  **角色設定 (選填)**：建議選擇 `Editor (編輯者)` 權限，或直接略過完成。

---

## 第四步：產生並下載 JSON 金鑰
1.  在服務帳戶清單中，點擊剛建立的帳號。
2.  切換到「**金鑰 (Keys)**」標籤頁。
3.  點擊「**新增金鑰**」 > 「**建立新金鑰**」。
4.  選取「**JSON**」格式，點擊「建立」。
5.  **重要操作**：
    *   瀏覽器會自動下載一個 `.json` 檔案。
    *   **請將此檔案命名為 `gdrive_creds.json`**。
    *   **放置位置**：放入專案目錄下的 `.env/` 資料夾中。

---

## 第五步：資料夾授權 (Final Step)
由於 Service Account 是一個「獨立的機器人帳號」，它預設看不到您的個人硬碟。
1.  打開您的 Google Drive。
2.  手動建立一個資料夾（例如：`AutoAgent_KB`）。
3.  右鍵點擊該資料夾 > 「**共用 (Share)**」。
4.  **在收件人處輸入您剛剛在 JSON 檔案中看到的 `client_email` 地址**。
    *   *(格式通常為：kb-uploader@xxxx.iam.gserviceaccount.com)*
5.  給予「**編輯者**」權限，點擊「傳送」。

---

## 技術總結 (Tom's Memo)
*   **安全警示**：JSON 金鑰等同於您的帳密，**絕對不要上傳到 GitHub**。請確認 `.gitignore` 已包含 `.env/*.json`。
*   **如何測試**：完成以上步驟後，直接執行 `python scripts/kb_gdrive_sync.py --file "test.txt"` 即可驗證。

---
> [!TIP]
> 照著這份指南操作，只需 5 分鐘即可完成實體雲端整合！
