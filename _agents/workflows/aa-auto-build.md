---
description: 銝?菔?遣瑽????摰?嚗?芸?敺芰???Phase??---

# Claw Auto-Build Workflow

## Trigger
雿輻?撓??`/aa-auto-build` ??"auto build" ??"?芸?撱箸?"

## ?芸???蝝?甇?workflow ????L3/L4嚗?芸? / ?芯蜓璅∪?嚗?
// turbo-all

## Execution Steps

### Step 1: Initialize
1. 憒? `.planning/PROJECT.md` 銝??剁?
   - ?瑁? `/aa-new-project --auto`
   - 雿輻???身?芸?????
   - 摰?敺?敺?roadmap

### Step 2: Phase Auto-Loop
**撠???Phase ?芸??瑁?隞乩?餈游?嚗?*

```
FOR phase_num IN (1..total_phases):
    
    # 2a. 閮?嚗atch mode嚗?撠?蝑?
    echo "????Phase ${phase_num}: [Phase Name] ????
    /aa-discuss ${phase_num}    ???芸??Ｗ CONTEXT.md
    
    # 2b. 閬?
    /aa-plan ${phase_num}       ???芸??Ｗ PLAN.md
    
    # 2c. ?瑁?
    /aa-execute ${phase_num}    ???芸??瑁? + commit
    
    # 2d. QA 瑼Ｘ
    /aa-qa ${phase_num}
    
    # 2e. ?芣?靽桀儔嚗??閬?
    fix_count = 0
    WHILE QA_RESULT == "FAIL" AND fix_count < 3:
        /aa-fix ${phase_num}
        /aa-qa ${phase_num}
        fix_count++
    
    IF fix_count >= 3 AND QA_RESULT == "FAIL":
        NOTIFY_USER "Fix loop exceeded max iterations for Phase ${phase_num}"
        OFFER: retry / skip / manual
        WAIT_FOR_USER
    
    # 2f. Guardian checkpoint
    /aa-guard ${phase_num}
    
    # 2g. ?箄疏
    /aa-ship ${phase_num}
    
    # 2h. ?湔???    echo $((phase_num + 1)) > .agent-state/current-phase
    
    # ?脣銝? Phase
ENDFOR
```

### Step 3: Complete
1. ?瑁??蝯?QA pass
2. Guardian ?蝯?checkpoint + 摰??
3. ?Ｗ?函蔡?蔭嚗??拍嚗?4. ?湔 STATE.md ??milestone complete
5. ?雿輻????獢???????
## Error Handling
- 隞颱?甇仿?憭望? ???脣??? `.agent-state/auto-resume.json`嚗?  ```json
  {
    "phase": N,
    "step": "execute|qa|fix",
    "timestamp": "ISO-8601",
    "error": "error message"
  }
  ```
- ?雿輻?擃隤?- ??嚗etry / skip / manual intervention

## State Persistence
- 瘥郊撽????湔 `STATE.md`
- ?臬?隞颱?銝剜暺敺抬?`/aa-resume`嚗?
