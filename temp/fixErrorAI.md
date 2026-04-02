# 針對 AutoAgent-TW 安裝包 (Installer) 問題的分析與改善方案

從近期的錯誤報告、反覆發生的執行緒問題以及安裝邏輯 (`aa_installer_logic.py`) 的分析，整理出安裝包一直發生問題的核心原因與對應的改善方案：

## 1. 無窮迴圈與行程爆炸 (PID Leak / Infinite Loop)
**問題狀況：** 
執行打包後的安裝程式 (`AutoAgent-TW_Setup.exe`) 會觸發無窮盡的子程序建立，直到系統資源耗盡。發生原因是 PyInstaller 打包環境下，使用 `sys.executable` 時會指向打包後的 `exe` 自己，而不是系統原生 Python。當使用它來 `subprocess.Popen` 或建立虛擬環境 (venv) 時，就變成了自己呼叫自己。
**改善方案：**
- **防範與隔離：** 在安裝腳本中加入 `find_python()` 函數掃描系統原生的 `python` 或 `python3`，並在啟動 subprocess 前嚴格防範自己呼叫自己。
- **最佳實踐：** 將開發環境建立與執行檔分離。並在程式進入點明確加上 `multiprocessing.freeze_support()` 避免 Windows 平台上的無窮生成。

## 2. 依賴環境衝突 (Pyinstaller 相依錯誤)
**問題狀況：** 
打包跟建構過程中因為要求具體的套件版本（如 `pyinstaller==6.5.0`），當使用者的系統升級導致虛擬環境無法找到該版本時，安裝/建構會卡死或閃退。
**改善方案：**
- **解耦 Requirement：** 將打包器依賴 (`build_requirements.txt`) 與核心系統執行依賴 (`requirements.txt`) 分離結構。
- **寬容版號設定：** 使用 `>=`, 而非 `==` 鎖死版號 (例如 `pyinstaller>=6.5.0`)，或使用 `pip-tools` 或 `poetry` 管理依賴以提高跨電腦容錯率，建立穩健的 lockfile。

## 3. 全域環境變數 PATH 寫入問題與指令失效
**問題狀況：** 
雖然呼叫了 `setx PATH` 來寫入環境變數以便使用 `autoagent` 指令，但常有副作用：
(1) `setx` 對超過 1024 字元的 PATH 可能有截斷風險，會破壞使用者的系統變數。
(2) 指令變更後不會立刻在當前命令列生效，導致使用者剛裝好打 `autoagent` 仍然跳出 "不是內部或外部指令"。
**改善方案：**
- **安全升級：** 於 Windows 環境中，應使用 PowerShell API `[System.Environment]::SetEnvironmentVariable('Path', $NewPath, 'User')`，以解除字元長度限制問題並防止毀損環境變數。
- **明確的安裝提示與環境廣播：** 發送 `WM_SETTINGCHANGE` 廣播，並於安裝腳本末尾加上強烈提示：「⚠️ 安裝完成！請重新啟動終端機 (Terminal) 或 IDE 以讓系統辨識 \`autoagent\` 全域指令！」

## 4. 全域指令 (Global Workflows) 註冊不確實
**問題狀況：**
有時 `/aa-` 相關工作流程即使安裝了，在其他路徑依然無法全局觸發。
**改善方案：**
- **強制作業目錄 (CWD) 校準：** 確保指令註冊墊片 (`autoagent.cmd`) 的內部路徑是寫死為安裝目錄的絕對路徑，而非依賴當下終端機位置。
- **格式檢查：** 安裝時複製至 `~/.gemini/antigravity/global_workflows` 時，可追加簡單檢查驗證 YAML 檔頭結構。

## 5. Workspaces 跨專案干擾 (Dirty Path Deployment)
**問題狀況：**
若從開發環境直接複製 (`shutil.copytree`) 至使用者目錄，很可能會把開發者的歷史殘留文件（例如自己的 `.planning/`、`.agent-state/`）全數複製到使用者環境內，造成專案初始化狀態被污染。
**改善方案：**
- **嚴格白名單 (Whitelist)：** `deploy_core_files` 應該要維護發佈白名單或過濾清單 (`ignore=shutil.ignore_patterns('.planning', '.agent-state', 'venv', '__pycache__')`)，避免複製隱藏資料夾與暫存檔。
