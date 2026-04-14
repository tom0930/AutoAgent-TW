# Phase 3 Research: Live Logs & Monitors

## Timely Monitoring
- Javascript's `Date.now() - new Date(data.timestamp)` can be used for stagnation detection.
- UI: If `diff > 90s`, then `status = "stuck"`.

## Log Tailing (Python side)
- For simplicity, the `/aa-auto-build` can pass log snippets to `status_updater.py` via `--logs "[line 1, line 2]"`.
- Or `status_updater.py` can tail a `project.log` file if it exists.

## UI Presentation
- Log list: Monospaced font, fade-in animations on new entries.
- Stagnation warning: Yellow pulsate on the top banner.
