# OpenClaw Planning (AutoAgent-TW .planningClaw)

## Project Overview
OpenClaw 是一個 AI 編排系統，能在使用者的裝置上執行真實任務。
此規劃目錄 (`.planningClaw`) 位於 AutoAgent-TW 專案下，管理 OpenClaw 的擴展功能開發。

## High-Level Vision (2026 Q2)
將 OpenClaw 從被動助手轉型為**自主自動化平台**。

### Phase 1: Automation Foundation（自動化基礎）
- **Automated Agent**：目標導向的多回合自主循環。
- **Web & GUI Control**：擴展 Browser 工具 + 原生 GUI 協議。
- **VLM UI Driver**：視覺模型驅動的 UI 自動化。

### Phase 2: AutoSkills（自動技能平台）
- **Skill Discovery**：Intent-based 自動搜尋 ClawHub 安裝。
- **Dynamic Skill Generation**：Agent 自產完整 Skill Package（manifest + SKILL.md + tests）。
- **Skill Evolution**：背景 Cron 定期健檢 + 自動更新/再生成。
- **Security Framework**：5 層安全防禦 + Permission Manifest + Approval Gradient。

### Phase 3: aa-clawinfo（OpenClaw 狀態報告）
- **即時報告**：Gateway sessions、running tasks、active skills。
- **歷史報告**：最近的 cron 執行、task 完成記錄、skill changes。
- **整合 AutoAgent-TW**：透過 `/aa-clawinfo` 工作流查詢。

## 文件結構
- `.planningClaw/STATE.md`：目前進度與活躍 phases。
- `.planningClaw/phases/1-automation/`：Phase 1 自動化基礎。
- `.planningClaw/phases/2-autoskills/`：Phase 2 自動技能平台。
