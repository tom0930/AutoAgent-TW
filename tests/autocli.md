# AutoCLI (nashsu/AutoCLI) POC 測試計畫

## 1. 測試目標 (Objectives)
驗證 AutoCLI 作為 AutoAgent-TW RVA 引擎的 `Eye-2 (CDP/Adapter Layer)` 的可行性、效能與安全性。

## 2. 測試環境 (Environment)
- 作業系統：Windows
- 瀏覽器：Chrome (需已登入 GitHub)
- AutoCLI 版本：最新 Rust 穩定版

## 3. 測試矩陣 (Test Matrix)

### 3.1 基礎部署與啟動效能 (Deployment & Performance)
- [ ] 下載 AutoCLI Windows Binary 並設置環境變數。
- [ ] 執行冷啟動 (Cold Start) 測速：確保啟動時間 < 100ms。
- [ ] 記憶體監控：觀察抓取網頁時的 RAM 波動 (預期 < 50MB)。

### 3.2 憑證與 Session 繼承 (Browser Session Reuse)
- [ ] 測試無頭模式 (Headless) 抓取公開頁面。
- [ ] 測試掛載現有 Chrome Profile，抓取需要登入的 GitHub 私有 Repo PR。
- [ ] 驗證 Token 刷新與 Cookie 存活狀態。

### 3.3 資料解析精準度 (Structural Parsing)
- [ ] 執行 `autocli fetch https://github.com/nashsu/AutoCLI`。
- [ ] 檢驗回傳的 JSON 結構是否乾淨無雜訊 (Token-efficient)。
- [ ] 測試動態網頁 (如 SPA) 元素的延遲載入解析能力。

### 3.4 資安與沙箱防禦 (Security & Sandbox)
- [ ] 嘗試用 AutoCLI 存取非白名單網域 (如 banking site)，驗證攔截機制。
- [ ] 嘗試透過惡意 prompt 觸發 `eval()` 或敏感操作，確認 Adapter 是否具備防護邊界。

## 4. 驗收標準 (UAT Criteria)
- 成功透過 `autocli-skill` 在 < 2 秒內獲取目標頁面的乾淨 JSON。
- 記憶體消耗嚴格控制在 Stealth Mode 規範內。
- 未發生任何資安越權行為。
