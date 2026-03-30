---
description: ?箄疏?挾 N嚗遣蝡?PR + Phase ??
---

# Claw Ship Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 撽?摰?摨?1. 蝣箄? Phase N ???Plans 撌脣???2. 蝣箄? QA PASS
3. 蝣箄? Guardian checkpoint 撌脣遣蝡?
### Step 2: ?Ｗ Phase ??
撖怠 `N-SUMMARY.md`嚗?```markdown
# Phase N Summary: [Phase Name]

## Completed
- Plan 01: [Title] ??[files changed]
- Plan 02: [Title] ??[files changed]

## Stats
- Commits: X
- Files created: X
- Files modified: X
- Tests: X passed / Y total

## QA Result
- Overall Score: X/10
- Issues found and fixed: X

## Key Decisions
- [Decision 1]
- [Decision 2]
```

### Step 3: Git Tag
```bash
git tag "phase-${N}-shipped" -m "Phase ${N}: [Phase Name] ??shipped"
```

### Step 4: ?湔 STATE.md
- 璅? Phase N ??`shipped`
- ?湔 `.agent-state/current-phase` ??N+1

### Step 5: Commit
```bash
git add .planning/
git commit -m "docs: phase ${N} shipped"
```

