# PLAN.md - Phase 118: Global Command & Installer Fix

## Wave 1: Installer Logic Correction
- [ ] **Task 1.1**: Update `aa_installer_logic.py` constants and directory lists.
    - Include `_agents` in `deploy_core_files`.
- [ ] **Task 1.2**: Fix `deploy_global_workflows` source path.
    - Change `src_wf_dir` to point to `_agents/workflows`.
- [ ] **Task 1.3**: Add validation logging.
    - Print the number of workflows registered to help the user confirm success.

## Wave 2: Deployment & Verification
- [ ] **Task 2.1**: Manual trigger of the script to verify file movement.
- [ ] **Task 2.2**: Verify that workflows appear in `~/.gemini/antigravity/global_workflows`.
- [ ] **Task 2.3**: Check if `/aa-` commands appear in the Antigravity command palette (slash commands).

## 🚀 UAT Criteria
1. Running the installer script successfully copies `scripts`, `.agents`, and `_agents` to the target.
2. The folder `~/.gemini/antigravity/global_workflows` contains 21 `aa-*.md` files.
3. Typing `/aa-` in the chat reveals the registered workflows.
