import json
import re

log_path = r"C:\Users\TOM\.gemini\antigravity\brain\8b4ab0ca-2ae5-4530-88ef-2973d691e863\.system_generated\logs\overview.txt"

commits = []

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "PLANNER_RESPONSE":
                for call in data.get("tool_calls", []):
                    if call.get("name") == "run_command":
                        cmd = call.get("args", {}).get("CommandLine", "")
                        if "git commit" in cmd:
                            commits.append({
                                "step": data.get("step_index"),
                                "time": data.get("created_at"),
                                "cmd": cmd
                            })
            elif data.get("type") == "USER_INPUT":
                content = data.get("content", "")
                if "git commit" in content:
                     commits.append({
                                "step": data.get("step_index"),
                                "time": data.get("created_at"),
                                "cmd": f"USER: {content[:200]}..."
                            })
        except:
            continue

print(json.dumps(commits, indent=2))
