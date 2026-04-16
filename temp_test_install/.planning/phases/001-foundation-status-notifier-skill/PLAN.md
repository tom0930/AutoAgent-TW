# Phase 1 Plan: Foundation & Status Notifier Skill

## Wave 1: Core Skill & Logic
### Task 1.1: Create Skill structure
- **Target File**: `.agents/skills/status-notifier/SKILL.md`
- **Action**: Define skill metadata and basic usage instructions.

### Task 1.2: Create Status Updater Script
- **Target File**: `.agents/skills/status-notifier/scripts/status_updater.py`
- **Action**: Write a Python script that takes arguments (task, next_goal, phase, etc.) and writes to `.agent-state/status_state.json`.

## Wave 2: Visualization Frontend
### Task 2.1: Create HTML Template
- **Target File**: `.agents/skills/status-notifier/templates/status.html`
- **Action**: Build a stunning, dark-mode dashboard with a fixed top banner. Use Tailwind via CDN.
- **Logic**: Fetch `status_state.json` periodically and update DOM.

### Task 2.2: Initial State Setup
- **Target File**: `.agent-state/status_state.json`
- **Action**: Create an initial dummy state for testing.

## Wave 3: Verification & Integration Test
### Task 3.1: Browser Injection Test
- **Action**: Use `browser_subagent` to open the `status.html` and verify the banner shows the initial state.
- **UAT Criteria**: Banner is visible, fixed, and shows correct task/goal.

### Task 3.2: Update State Test
- **Action**: Run `python scripts/status_updater.py --task "Testing phase 1" --next "Phase 2 Preparation"`
- **UAT Criteria**: Browser visual updates within 3 seconds.

## Verification Standards (UAT)
- [ ] `status_state.json` is correctly updated by Python.
- [ ] `status.html` renders without CORS errors (using absolute file paths if possible).
- [ ] Dashboard looks "premium" (dark mode, glassmorphism, pulse animations).
