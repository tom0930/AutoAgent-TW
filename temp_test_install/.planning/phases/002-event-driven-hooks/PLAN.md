# Phase 1 Plan: Event-Driven Hooks

## Wave 1: Core Hub
### Task 1.1: Create `.agent-state/hooks.json`
- **Goal**: Define initial git and ci mappings using standard JSON.
- **Example**: `{"git.post-commit": "aa-progress"}`.

### Task 1.2: Create `scripts/event_handler.py`
- **Goal**: Read `hooks.json`, execute mapped command in background.
- **Logging**: Log to `.agents/logs/events.log`.

## Wave 2: Git Integration
### Task 2.1: Implement Hook Management
- **Action**: Add `register-hooks` command to `aa_schedule_cli.py` to copy/symlink scripts to `.git/hooks/`.

## Wave 3: CI Simulation
### Task 3.1: Tool for CI failure trigger
- **Action**: A simple flag-based trigger for `aa-fix` or `/aa-auto-build`.

## Verification Standards (UAT)
- [ ] Manual execution of `event_handler.py git.post-commit` triggers the correct command.
- [ ] Git commit actually triggers the handler.
- [ ] CI failure flag correctly starts a repair loop.
