---
description: ?芸???QA 瑼Ｘ嚗??QA-REPORT.md
---

# Claw QA Workflow

## Trigger
?冽???`/aa-execute` 摰?敺?銵??????`/aa-qa [N]`

// turbo-all

## Checks嚗?撠?憿??芸??菜葫嚗?
### 1. Code Quality
```bash
# Node.js 撠?
npm run lint 2>&1 || true
npm run type-check 2>&1 || true

# Python 撠?
python -m ruff check . 2>&1 || true
python -m mypy . 2>&1 || true

# C/C++ 撠?
# 雿輻 cppcheck ??clang-tidy
```

### 2. Tests
```bash
# Node.js
npm test 2>&1

# Python
python -m pytest 2>&1

# C/C++
# cmake --build . --target test
```

### 3. Security
```bash
# 靘陷摰
npm audit 2>&1 || true
# pip audit 2>&1 || true

# 蝖祉楊蝣澆?蝣潭???grep -rn "password\|secret\|api_key\|token\|private_key" src/ --include="*.{js,ts,py,cpp,c,h}" 2>&1 || true
```

### 4. Requirements Traceability
霈??`.planning/REQUIREMENTS.md`嚗???Phase N ??瘙?撽?嚗?- 瘥?REQ-ID ?臬???祕雿?- 瑼Ｘ??臬?舀迤撣賊?銵?
### 5. Build Verification
```bash
# Node.js
npm run build 2>&1

# Python
python -m py_compile [main files]

# C/C++
# cmake --build .
```

## Report
撖怠 `.planning/phases/{N}-*/QA-REPORT.md`嚗?
```markdown
# QA Report ??Phase N

| Category | Score (1-10) | Details |
|----------|-------------|---------|
| Code Quality | X | ... |
| Test Coverage | X | ... |
| Security | X | ... |
| Requirements Compliance | X | ... |

**Overall: PASS/FAIL (avg score)**

## Issues Found
1. [Issue description] ??Severity: High/Medium/Low
2. ...

## Recommendations
1. ...
```

## Escalation
- PASS (??) ??蝜潛?銝? Phase
- FAIL (<7) ??閫貊 `/aa-fix N`嚗uto-fix ?憭?3 頛迎?
- Critical (<5) ???餅?銝? Phase
- Security issues ??蝡?雿輻??
