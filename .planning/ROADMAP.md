# Roadmap: v1.6.0 Autonomous Scheduling Upgrade

## Phase 1: Scheduler Foundation (`/aa-schedule`)
- Implement a background daemon using Python `apscheduler`.
- Create `/aa-schedule` command to manage (add/list/remove) tasks.
- Persistent task storage (`.agent-state/scheduled_tasks.json`).
- Verify: Agent automatically starts a task at a scheduled time (e.g., in 1 minute).

## Phase 2: Event-Driven Hooks
- Integrate git hook triggers (local `post-commit` / `post-merge`).
- Support webhook ingestion for CI failures (mocked or simple HTTP listener).
- Configurable `hooks.json` for mapping events to actions.

## Phase 3: Adaptive Repair Loop
- Refactor `aa-fix` and `aa-qa` logic to use trend analysis.
- Implement loop detection (same error appearing multiple times).
- Support for "Diversity score" in repair attempts.

## Phase 4: Task Chaining & Pipelines (`/aa-chain`)
- Implement a task orchestrator that can execute a sequence of `aa-` commands.
- Support conditional logic (if-fail-then).
- Command format: `/aa-chain "pull | build | test | repair | push"`.

## Phase 5: Multi-Project Dashboard & QA
- Centralized monitoring for multiple project paths.
- Final visual polish for the transparency dashboard (scheduler tab).
- Release Note and documentation update.
