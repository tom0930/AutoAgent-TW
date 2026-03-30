---
description: ?瑁??挾 N ????Plans嚗蝙??Wave 撟唾???---

# Claw Execute Workflow

## Input
- Phase number: N (from $ARGUMENTS)
- Optional: `--fix` ???芸銵耨敺抵???- Optional: `--wave W` ???芸銵?摰?Wave

// turbo-all

## Steps

### Step 1: 頛閮
1. 霈??`N-PLAN.md`
2. 閫?????Plans ??Wave ??
3. 瑼Ｘ?芯? Plans 撌脣????踹????瑁?嚗?4. ?湔 `.agent-state/builder-status`嚗?```
Phase: N
Status: executing
Start: [timestamp]
```

### Step 2: Wave ?瑁?
**撠???Wave ??摨銵?**

```
FOR wave IN waves:
    echo "?? Wave ${wave.number} ??"
    
    FOR plan IN wave.plans:
        IF plan.completed:
            echo "  ??Plan ${plan.id}: already done, skipping"
            CONTINUE
        
        echo "  ??Executing Plan ${plan.id}: ${plan.title}"
        
        # 2a. ?瑁? Plan
        - ??Plan ?郊撽遣蝡?靽格瑼?
        - 撖怎?撘Ⅳ
        - 憒?皜祈岫嚗?頝葫閰衣Ⅱ隤?        
        # 2b. ?? Commit
        git add [changed files]
        git commit -m "Phase ${N}: ${plan.title}"
        
        # 2c. ?湔???        - 璅? Plan ?箏歇摰?
        - ?湔 .agent-state/builder-status
    ENDFOR
    
    echo "  Wave ${wave.number} complete ??
ENDFOR
```

### Step 3: ?瑁?摰?
1. ?湔 `.agent-state/builder-status`嚗?```
Phase: N
Status: executed
End: [timestamp]
Plans: X/X complete
```
2. ?湔 `.planning/STATE.md`
3. ???遣蝡?靽格??獢? commits

### Step 4: ?內銝?甇?- 鈭?璅∪?嚗遣霅?`/aa-qa N`
- Auto-build 璅∪?嚗?銵?QA

