# Phase 118: Installer & Global Workflow Fix

## 📋 Problem Analysis
- **Target File**: `z:\autoagent-TW\scripts\aa_installer_logic.py`
- **Issue 1**: Line 78 - `src_wf_dir` is set to `target_dir/.agents/workflows`. 
    - *Correction*: Should check both `.agents/workflows` and `_agents/workflows`. 
- **Issue 2**: Line 107 - `dirs = ["scripts", ".agents"]`.
    - *Correction*: Need to include `_agents` or consolidate them during deployment.
- **Issue 3**: Antigravity workflow discovery mechanism requires files in `~/.gemini/antigravity/global_workflows` to have proper YAML frontmatter and `.md` extension.

## 🛠️ Proposed Solution
1. Update `deploy_core_files` to include `_agents`.
2. Update `deploy_global_workflows` to source from `_agents/workflows`.
3. Add a check to verify if the global directory is correctly populated.
4. Update `register_global_command` to ensure the `autoagent` CLI shim is correctly linked.

## ⚠️ Potential Pitfalls
- **Path Separation**: Windows vs Unix paths (already handled with `os.path.join`).
- **Permissions**: Writing to `~/.gemini/antigravity/` might require permission checks if the directory doesn't exist.
