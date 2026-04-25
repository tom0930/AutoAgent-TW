# 🐛 Bug Fix Report — AutoAgent-TW v3.3.2-patch1
**Date:** 2026-04-25
**Scope:** Phase 160 → Phase 160-patch1
**Total Bugs Found:** 8 · **Fixed:** 6 · **Deferred:** 2
**Files Changed:** 4 source files + 2 documentation files

---

## 📋 Bug Matrix

| ID  | Severity | Type     | File                                      | Status   |
|-----|----------|----------|-------------------------------------------|----------|
| B1  | 🔴 HIGH  | Type-annot bug | `src/core/harness_gateway.py`      | ✅ FIXED |
| B2  | 🔴 HIGH  | Typo / Logic   | `src/core/orchestration/spawn_manager.py` | ✅ FIXED |
| B3  | 🟠 MED   | Stub / Missing | `src/harness/cli/main.py`           | ✅ FIXED |
| B4  | 🟠 MED   | Wrong data type | `src/harness/cli/main.py`          | ✅ FIXED |
| B5  | 🟠 MED   | Edge-case URL | `scripts/autocli_guard.py`          | ✅ FIXED |
| B6  | 🟡 LOW   | Tech Debt | `src/core/harness_gateway.py`           | ✅ FIXED |
| B7  | 🟡 LOW   | Feature Gap | `src/harness/cli/main.py` (orchestrate tools) | ⚠️ DEFERRED |
| B8  | 🟡 LOW   | Test Gap  | `tests/` missing unit coverage          | ⚠️ DEFERRED |

---

## 🔧 Fix Detail

### B1 — `start_time` type annotation shadow bug 🔴 FIXED

**File:** `src/core/harness_gateway.py`
**Line:** ~159

**Problem:**
```python
# In __init__:
self.start_time: float = 0.0  # class-level annotation

# In start():
self.start_time: float = time.time()  # RE-DECLARES — shadows instance attr
```

The `self.start_time: float =` inside `start()` is a local variable declaration (type-annotated), not an attribute assignment. The instance attribute was never updated, so `status()` always returned `0` uptime.

**Fix:**
```python
self.start_time = time.time()  # Remove ": float" — correct attribute update
```

---

### B2 — `env_ovrides` typo in `AgentProcess.spawn()` 🔴 FIXED

**File:** `src/core/orchestration/spawn_manager.py`
**Lines:** ~63-71

**Problem:**
```python
def spawn(self, command: list, env_ovrides: Optional[dict] = None):  # typo
    ...
    if env_ovrides:          # typo propagates
        env.update(env_ovrides)  # caller never reaches this
```

The parameter was misspelled `env_ovrides` but the docstring and intended semantics were `env_overrides`. This means any caller passing `env_overrides=` would silently have no effect — a silent failure.

**Fix:**
```python
def spawn(self, command: list, env_overrides: Optional[dict] = None):
    """...
    Args:
        command: List of command arguments to execute.
        env_overrides: Optional dict of environment variables to override/extend.
    """
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
```

---

### B3 — Empty stub handlers: `_cmd_session`, `_cmd_node` 🟠 FIXED

**File:** `src/harness/cli/main.py`

**Problem:** Three command handlers printed a placeholder string and returned `0` without performing any action:
- `_cmd_session` → `print(f"Session command: ...")`
- `_cmd_node` → `print(f"Node command: ...")`
- `_cmd_system` → incomplete (partially implemented)

**Fix:** Implemented full handlers:
- `_cmd_session [list|show|delete]` → delegates to `SessionManager`
- `_cmd_node [list|describe|pair|remove]` → delegates to `NodePairingManager`
- `_cmd_system [info|memory|clean]` → already had `info` and `memory`; added `clean`

---

### B4 — Wrong data structure: List vs Dict in `orchestrate agents` 🟠 FIXED

**File:** `src/harness/cli/main.py` — `_cmd_orchestrate` sub-handler

**Problem:**
```python
for pid, proc in list(_ACTIVE_SUBAGENTS.items()):  # ERROR: List has no .items()
```

`_ACTIVE_SUBAGENTS` is declared as `List['AgentProcess']` in `spawn_manager.py`, but the CLI code iterated it as a `Dict` with `.items()`. This would raise `AttributeError: 'AgentProcess' object has no attribute 'items'`.

**Fix:**
```python
for proc in list(_ACTIVE_SUBAGENTS):  # correct: iterate list directly
    name = getattr(proc, "task_name", "?")
    aid  = getattr(proc, "agent_id", "?")
    status   = getattr(proc, "status", "?")
    progress = getattr(proc, "progress", 0)
    icon = "🟢" if status == "running" else "⚫"
    print(f"  {icon} [{aid}] {name} — {progress}% ({status})")
```

---

### B5 — URL parsing edge cases in `autocli_guard.py` 🟠 FIXED

**File:** `scripts/autocli_guard.py`

**Problem 1 — Bare host fallthrough:**
```python
domain = urlparse(url).netloc.lower()
if not domain:
    domain = url.split('/')[0].lower()  # naive: "api.github.com:443" → "api.github.com:443"
```
Works for simple hosts but breaks with port numbers.

**Problem 2 — Whitelist check used `in` instead of exact/subdomain match:**
`if allowed in domain` matches `evil.github.com.evil.com` against whitelist `github.com` → false positive.

**Fix:**
- Added `@`-stripping for `user:pass@host` fallback
- Added subdomain-aware whitelist matching: `allowed == domain or domain.endswith("." + allowed)`
- Added granular exception handling per logical block
- Added docstring documenting all three URL forms handled

---

### B6 — Empty `_init_service_module` stub 🟡 FIXED

**File:** `src/core/harness_gateway.py`

**Problem:** `_init_service_module()` was `pass` — all services initialized as no-ops, making the Gateway's service management completely non-functional.

**Fix:** Implemented router that dispatches to typed init methods:
| Service | Method | Action |
|---------|--------|--------|
| `security` | `_init_security()` | Log hooks auto-registered |
| `memory` | `_init_memory()` | Loads `MemoryPalace` |
| `vision` | `_init_vision()` | Loads `RVAEngine` |
| `mcp` | `_init_mcp()` | Loads `MCPHub` |
| `cron` | `_init_cron()` | Loads `CronScheduler` |

Each method logs its result; unavailable modules raise with graceful warning.

---

## ⚠️ Deferred Items

### B7 — `orchestrate tools` MCP tools listing not implemented
The `tools` subcommand dispatches correctly but the MCP tools enumeration logic was left incomplete. Requires `MCPClientManager.get_tools_for_agent()` to be wired to the coordinator. **Suggested fix:** call `MCPClientManager().get_tools()` and print formatted tool list.

### B8 — No unit tests for `src/harness/` modules
The `tests/` directory exists but has no coverage for `cli/main.py`, `spawner/`, `canvas/`, or `messages/`. **Recommended:** add `pytest` suite covering happy-path CLI dispatch, stub handlers, and mock agent spawning.

---

## 📁 Files Changed

```
src/core/harness_gateway.py           [FIX] B1, B6
src/core/orchestration/spawn_manager.py [FIX] B2
src/harness/cli/main.py              [FIX] B3, B4
scripts/autocli_guard.py              [FIX] B5
FIX-REPORT-BUGS-0425.md              [NEW] This report
FIX-REVIEW-0425.md                   [NEW] Code review report
```

---

## ✅ Verification

| Check | Result |
|-------|--------|
| `python -m py_compile src/core/harness_gateway.py` | ✅ Pass |
| `python -m py_compile src/core/orchestration/spawn_manager.py` | ✅ Pass |
| `python -m py_compile src/harness/cli/main.py` | ✅ Pass |
| `python scripts/autocli_guard.py https://github.com/test` | ✅ SAFE |
| `python scripts/autocli_guard.py https://evil.com` | ✅ BLOCKED |
| `python scripts/autocli_guard.py github.com/nashsu/autocli` | ✅ SAFE |

*Auto-verified via `aa-harness doctor --category core` → 🟢 PASS*
