---
description: ?弦 + 閬??挾 N嚗??RESEARCH.md ??PLAN.md
---

# Claw Plan Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 頛銝???1. 霈??Phase N ??CONTEXT.md嚗?摮嚗?2. 霈??ROADMAP.md 銝?Phase N ?璅??瘙?3. 霈??STATE.md ??鈭圾??摰??摰?4. 瑼Ｘ `.planning/config.json` ??workflow.research 閮剖?

### Step 2: ???弦嚗??嚗?**??config.workflow.research == true嚗?*
1. ?? Phase N ?擃?銵?瘙脰??弦
2. ?Ｗ `N-RESEARCH.md`嚗?   - ?雿喳祕頦?   - ?祕雿?   - 瞏??
   - ?刻?寞?

### Step 3: ?圾??Plans
1. 撠?Phase N ??瘙?閫??琿??臬銵? Plans
2. 瘥?Plan ?嚗?   - **?格?**嚗???暻?   - **瑼?皜**嚗?閬遣蝡?靽格??獢?   - **甇仿?**嚗擃祕雿郊撽?   - **撽?**嚗?雿Ⅱ隤???   - **靘陷**嚗?鞈游鈭隞?Plans

### Step 4: Wave ??
1. ?? Plan ??鞈湧?靽?2. ?∩?鞈渡? Plans ??? Wave嚗撟唾??瑁?嚗?3. ??鞈渡? Plans ?敺? Wave

### Step 5: ?Ｗ PLAN.md
撖怠 `N-PLAN.md`嚗?```markdown
# Phase N: [Phase Name]

## Goal
[Phase goal from ROADMAP.md]

## Wave 1 (parallel)
### Plan 01: [Title]
- **Goal:** ...
- **Files:** ...
- **Steps:** ...
- **Verify:** ...

### Plan 02: [Title]
- **Goal:** ...
- **Files:** ...
- **Steps:** ...
- **Verify:** ...

## Wave 2 (after Wave 1)
### Plan 03: [Title]
- **Depends on:** Plan 01, Plan 02
- **Goal:** ...
- **Files:** ...
- **Steps:** ...
- **Verify:** ...
```

### Step 6: Commit
```bash
git add ".planning/phases/"
git commit -m "docs: phase ${N} plan (X plans, Y waves)"
```

### Step 7: ?內銝?甇?- 鈭?璅∪?嚗遣霅?`/aa-execute N`
- Auto-build 璅∪?嚗?匱蝥?
