# Phase 4 Research: Integrations & Commands

## LINE Notify API
- Endpoint: `https://notify-api.line.me/api/notify`
- Auth: Bearer Token (User provided).
- Library: `requests` in Python.

## Workflow Injection
- To avoid modifying hundreds of files, I will demonstrate the injection on `aa-progress.md` and define a pattern for other workflows.
- Pattern:
```markdown
// turbo
[COMMAND]: python .agents/skills/status-notifier/scripts/status_updater.py ...
```

## Progressive Reveal
- When `/aa-progress` is run, the agent should output: 
  "🌐 視覺化儀表板已啟動: http://localhost:9999/.agents/skills/status-notifier/templates/status.html"
