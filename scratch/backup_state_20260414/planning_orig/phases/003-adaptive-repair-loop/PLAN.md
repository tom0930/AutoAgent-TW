# Phase 3 Plan: Adaptive Repair Loop

## Wave 1: Data Ledger
### Task 1.1: Create `.agent-state/repair_history.json` 結構
- **Goal**: Define the schema for tracking (id, timestamp, err, diff, result, metrics).

## Wave 2: Decision Logic
### Task 2.1: Create `scripts/repair_loop_strategy.py`
- **Goal**: Implement `RepairStrategy` class.
- **Logic**:
  - `calculate_diversity()`: Compare diff patches.
  - `calculate_trend()`: Compare error/failure counts.
  - `should_continue(history)` -> bool.

## Wave 3: Integration Wrapper
### Task 3.1: Create `scripts/adaptive_fix_wrapper.py`
- **Goal**: A script that wraps `aa-fix` and uses the logic to decide whether to loop again.

## Verification Standards (UAT)
- [ ] Multiple repair rounds are allowed if error counts decrease.
- [ ] Task stops immediately if same diff is repeated.
- [ ] History is correctly persisted.
