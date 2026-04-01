window.AA_STATUS = {
    "version": "1.7.0",
    "current_task": "Progress Check",
    "next_goal": "None set",
    "phase_num": 6,
    "total_phases": 112,
    "status": "idle",
    "mermaid_code": "graph TD\n  classDef done fill:#238636,color:white,stroke:none\n  classDef running fill:#4ade80,color:black,stroke-width:3px,stroke:#fff\n  classDef pending fill:#21262d,color:#8b949e,stroke:#30363d\n  classDef fail fill:#f85149,color:white,stroke:none",
    "logs": [],
    "repair_round": 0,
    "scheduled_tasks": [
        {
            "id": "478d962a-9708-4f7e-ac9c-95e6030d6061",
            "name": "QA-Verification",
            "trigger_type": "interval",
            "params": {
                "minutes": 1
            },
            "command": "python .agents/skills/status-notifier/scripts/status_updater.py --task 'QA-Triggered' --status running",
            "last_run": "2026-04-01 10:38:50",
            "last_status": "success",
            "next_run": "2026-04-01 10:39:50"
        },
        {
            "id": "fa4f221c-e9c0-48b1-8a3f-480de31f3f38",
            "name": "系統心跳檢查",
            "trigger_type": "interval",
            "params": {
                "minutes": 2
            },
            "command": "aa-progress",
            "last_run": "2026-04-01 10:37:50",
            "last_status": "success",
            "next_run": "2026-04-01 10:39:50"
        },
        {
            "id": "28ef365d-793e-49c6-a630-53c0c96a740a",
            "name": "Regex Test",
            "trigger_type": "interval",
            "params": {
                "minutes": 2
            },
            "command": "aa-progress",
            "last_run": "2026-04-01 10:37:50",
            "last_status": "success",
            "next_run": "2026-04-01 10:39:50"
        },
        {
            "id": "8b062a0b-bd03-499b-9b26-a49f1f46f3ee",
            "name": "系統心跳檢查",
            "trigger_type": "interval",
            "params": {
                "minutes": 2
            },
            "command": "aa-progress",
            "last_run": "2026-04-01 10:37:51",
            "last_status": "success",
            "next_run": "2026-04-01 10:39:50"
        },
        {
            "id": "95ebc1f9-69dc-48fe-8ddf-7da2aa9e5aa1",
            "name": "Hourly-QA",
            "trigger_type": "interval",
            "params": {
                "hours": 1
            },
            "command": "aa-qa",
            "next_run": "2026-04-01 11:09:50",
            "last_run": "2026-04-01 10:09:50",
            "last_status": "fail"
        }
    ],
    "hooks": {
        "on": {
            "git.post-commit": [
                "python .agents/skills/status-notifier/scripts/status_updater.py --task 'Git Hook: Post-Commit' --status running",
                "aa-progress"
            ],
            "ci.failure": [
                "python .agents/skills/status-notifier/scripts/status_updater.py --task 'CI Recovery: Auto-Fixing' --status fail",
                "aa-fix --auto"
            ],
            "daily.scan": [
                "aa-guard --auto"
            ]
        }
    },
    "timestamp": "2026-04-01T10:39:50.717841"
};
};