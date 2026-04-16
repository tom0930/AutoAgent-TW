# Phase 2: Versioning and Git Workflow Refinement
# Ref: /aa-discuss (User request)

## Design Decisions

### 1. Version System (Versioning)
- **Primary Source**: `.planning/config.json` will contain `"version": "x.y.z"`.
- **Secondary Display**: `README.md` and `version_list.md` must be updated.
- **Current Version**: 1.1.0 (Incrementing from 1.0.0 after yesterday's initial setup).
- **Changelog**: `version_list.md` to be created in the root directory.

### 2. Git Automation in Fix-Workflows
- **`aa-fixgit-issue`** and **`aa-fixgit-pr`** should now explicitly:
    1.  Perform `git add .` and `git commit` (with conventional commits).
    2.  Perform `git push` if a remote branch is established.
    3.  Report the commit SHA in comments if possible.

### 3. Documentation (version_list.md)
- **Format**:
    ```markdown
    # Version List (Changelog)
    
    ## [v1.1.0] - 2026-03-30
    ### Added
    - Multi-language support (i18n) for all `aa-` commands.
    - New `aa-fixgit-pr` and `aa-fixgit-issue` workflows.
    - Configuration file `.planning/config.json`.
    - `version_list.md` tracking.
    ```

## Technology Selection
- Standard Git CLI for commits/push.
- Markdown for documentation.

## Next Step
- Execute `/aa-plan 2` to detail the update logic for each workflow.
