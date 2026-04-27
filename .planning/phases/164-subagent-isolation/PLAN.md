# Phase 164 Implementation Plan: Subagent Context Isolation

## 1. Goal Description
導入 VoltAgent 專家角色與 RTK 語境隔離。

## 2. Proposed Changes
- [NEW] `src/core/orchestration/subagents.json`
- [NEW] `.agents/personas/`
- [MODIFY] `src/core/orchestration/spawn_manager.py`
- [NEW] `src/core/orchestration/vfs_guard.py`
- [NEW] `scripts/rtk_prune.py`

## 3. Atomic Tasks
- [ ] Task 1: Registry Setup (subagents.json & personas)
- [ ] Task 2: SpawnManager & RTK Integration
- [ ] Task 3: VFS Guard Implementation
- [ ] Task 4: Verification Contract & E2E Test
