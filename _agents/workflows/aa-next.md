---
description: ?芸??菜葫銝血銵?銝甇?---

# Claw Next Workflow

// turbo-all

## Steps

### Step 1: 霈????1. 瑼Ｘ `.planning/PROJECT.md` ?臬摮
2. 霈??`.agent-state/current-phase`
3. 霈??`.planning/STATE.md`
4. 霈??`.planning/ROADMAP.md`

### Step 2: ?箄頝舐

```
IF no PROJECT.md:
    ???瑁? /aa-new-project
    
ELIF no ROADMAP.md:
    ???瑁? /aa-new-project嚗匱蝥摰???憪?嚗?    
ELIF current_phase > total_phases:
    ???瑁? milestone complete
    
ELSE:
    phase = current_phase
    phase_dir = ".planning/phases/{NNN}-*"
    
    IF no CONTEXT.md for phase:
        ???瑁? /aa-discuss ${phase}
        
    ELIF no PLAN.md for phase:
        ???瑁? /aa-plan ${phase}
        
    ELIF PLAN.md has incomplete plans:
        ???瑁? /aa-execute ${phase}
        
    ELIF no QA-REPORT.md for phase:
        ???瑁? /aa-qa ${phase}
        
    ELIF QA-REPORT says FAIL:
        ???瑁? /aa-fix ${phase}
        
    ELIF no checkpoint for phase:
        ???瑁? /aa-guard ${phase}
        
    ELIF phase not shipped:
        ???瑁? /aa-ship ${phase}
        
    ELSE:
        # Phase 摰?嚗???        echo $((phase + 1)) > .agent-state/current-phase
        ???艘?瑁? /aa-next
ENDIF
```

### Step 3: 頛詨
- 憿舐內?嗅????- 憿舐內?喳??瑁???雿?- ?瑁???

