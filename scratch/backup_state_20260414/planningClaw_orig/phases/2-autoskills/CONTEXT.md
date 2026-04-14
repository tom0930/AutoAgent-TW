# Phase 2: AutoSkills — Self-Evolving Skill Platform

## Goal
讓 OpenClaw Agent 在面對新任務時，能**自動發現、安裝、生成、演化** Skill，無需人類手動介入。

## Context
OpenClaw 已有的基礎設施：
- **ClawHub**：Skill 商店 + Search API（`searchClawHubSkills`, `installSkillFromClawHub`）。
- **SKILL.md**：每個 Skill 的主入口。
- **Gateway hot-reload**：已支援不重啟載入新 Skill。
- **Sandbox**：Docker / Node sandbox 用於隔離執行。
- **skill-creator skill**：已有基礎的 Skill 產生器。

## 核心原則
- **Intent-driven**：一切以 Agent 的當前 Goal 為中心。
- **Safe-by-Default**：Permission Manifest + Sandbox + Human-in-the-Loop 梯度。
- **Versioned & Traceable**：每個 Skill 都有完整歷史、可 rollback。
- **ClawHub-First**：優先重用社群技能，減少重複生成。

## 三大自動化流程
1. **Skill Discovery** — Intent-based Auto-Install（從 ClawHub 自動搜尋安裝）。
2. **Dynamic Skill Generation** — Agent 自產完整 Skill Package（manifest + SKILL.md + tests）。
3. **Skill Evolution** — 背景 Cron 定期健檢 + 自動更新/再生成。

## 安全框架
- **5 層防禦**：Manifest 靜態宣告 → 安裝審核閘道 → Runtime Sandbox → Evolution 安全控制 → 監控稽核。
- **Approval Gradient**：Low-risk auto-approve → Medium 一次確認 → High 每次確認。
- **Rollback**：每次更新前自動備份。

## 約束
- 不可繞過 `allowCommands` / `denyCommands` 節點安全機制。
- 動態生成的 Skill 必須通過 Sandbox 測試才能啟用。
- Evolution 不可自動擴大權限，擴權必須重走 Approval Gate。
