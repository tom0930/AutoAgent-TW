---
description: Guardian 摰?? + ?遢 + checkpoint
---

# Claw Guard Workflow

## Trigger
?冽???Phase ??摰?敺????澆 `/aa-guard [N]`

// turbo-all

## Steps

### 1. Git ???霅?```bash
git status
# 蝣箄?撌乩??桅?銋暹楊嚗o uncommitted changes嚗?```

### 2. Checkpoint 撱箇?
```bash
# 撱箇? git tag
git tag "phase-${N}-complete" -m "Phase ${N} completed successfully"

# 閮? checkpoint
echo "Phase: ${N}" > .agent-state/checkpoint-$(printf '%03d' $N)
echo "Timestamp: $(date -Iseconds)" >> .agent-state/checkpoint-$(printf '%03d' $N)
echo "Git SHA: $(git rev-parse HEAD)" >> .agent-state/checkpoint-$(printf '%03d' $N)
echo "Status: complete" >> .agent-state/checkpoint-$(printf '%03d' $N)
```

### 3. 摰??
```bash
# 靘陷瞍?
npm audit 2>&1 || true
# pip audit 2>&1 || true

# 蝖祉楊蝣澆?蝣?撖??
grep -rn "password\|secret\|api_key\|private_key\|token" src/ --include="*.{js,ts,py,cpp,c,h}" 2>&1 || true

# 瑼Ｘ .gitignore ?臬甇?Ⅱ
# 蝣箄? .env?ode_modules?_pycache__ 蝑◤敹賜
```

### 4. .gitignore 撽?
蝣箄?隞乩?瑼?/?桅?撌脰◤甇?Ⅱ敹賜嚗?- `.env` / `.env.local`
- `node_modules/`
- `__pycache__/`
- `*.pyc`
- `.agent-state/error-log`嚗???閮?

### 5. Checkpoint 蝞∠?
- 蝬剛風?餈?5 ??checkpoint
- 頞? 5 ?????芷???

### 6. 頛詨 SECURITY-REPORT.md嚗??潛??嚗?```markdown
# Security Report ??Phase N

## Vulnerabilities
- [dependency]: [severity] ??[description]

## Hardcoded Secrets
- [file:line]: [matched pattern]

## .gitignore Status
- ??/ ?? [item]

## Recommendation
[action needed]
```

