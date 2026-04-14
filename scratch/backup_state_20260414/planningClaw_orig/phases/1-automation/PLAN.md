# Plan: Automation Foundation

## Wave 1: Enhanced Web/GUI Capabilities
This wave focuses on making OpenClaw better at controlling what it sees.

- **Task 1: Extended Browser Tool (Snaphost/Action Refinement)**
  - Objective: Improve `browser.snapshot` to include deep accessibility properties for better reasoning.
  - Steps:
    - Update `extensions/browser/src/browser/pw-tools-core.snapshot.ts` to include `role` and `aria-label` in the JSON output.
    - Add a `browser.multi_action` tool for batching actions (click-type-click) to reduce turns.
- **Task 2: Native GUI Protocol (Node Invoke)**
  - Objective: Add low-level GUI commands to the `node.invoke` protocol.
  - Steps:
    - Define `gui_click`, `gui_type`, `gui_press`, `gui_scroll` in the node protocol schema.
    - Implement a prototype `gui-control` plugin that uses `nut.js` or `robotjs` for local desktop automation.
- **Task 3: VLM UI Driver**
  - Objective: A tool that takes a screenshot and returns coordinates for elements.
  - Steps:
    - Create a `gui.mapping` tool that sends a screenshot and context to a VLM (Gemini 1.5 Pro).
    - Map high-level descriptions (e.g. "Submit button") to `(x, y)` coordinates.

## Wave 2: Automated Agent Loop (Autonomous Planning)
This wave enables agents to plan and execute multi-turn tasks.

- **Task 1: Goal/Plan Abstraction**
  - Objective: Allow agents to "commit" to a multi-step sequence.
  - Steps:
    - Add `planned_tasks` to the session state.
    - Implement a `set_goal` tool that updates the system prompt and initializes the task list.
- **Task 2: Autonomous Monitor & Resume**
  - Objective: Automatically wake up the agent when a background task finishes.
  - Steps:
    - Integrate `openclaw-tasks` with the session heartbeat.
    - If a task is complete, trigger a "Monitor" turn to let the agent decide the next step.
- **Task 3: Turn and Token Budgeting**
  - Objective: Prevent runaway autonomous loops.
  - Steps:
    - Implement a `budget.manager` that tracks `max_turns` and `max_tokens` per goal.
    - Prompt for human approval when a budget is nearing its limit.

## Wave 3: Automated Skills (Self-Management)
This wave makes skills a first-class citizen of agent autonomy.

- **Task 1: Skill Discovery (ClawHub On-Demand)**
  - Objective: Agent automatically searches ClawHub when a tool is requested but missing.
  - Steps:
    - Create a `search_clawhub` tool.
    - If a tool name matches a ClawHub skill, prompt the user: "I need the 'x' skill to do this. Should I install it?".
- **Task 2: Agent-Authored Skills (Sandbox & Install)**
  - Objective: Agent can write a script, test it, and install it as a skill.
  - Steps:
    - Create a `develop_skill` tool that creates a `SKILL.md` and a `tool.py/js` in a temp directory.
    - Use the existing `sandbox` to run tests on the new skill.
    - On success, use `install_package_dir` to move it to `workspace/skills`.

## Validation Standards (UAT Criteria)
1. **Web/GUI**: Agent can navigate a website, find a specific button using VLM (if DOM fails), and click it accurately.
2. **Autonomous**: Agent can take the goal "Research X and write a summary", spawn a research subagent, wait for it to finish, and produce the final summary without intermediate user prompts.
3. **Skills**: Agent can identify it lacks a "Currency Converter" skill, search for it, and install it to complete a conversion task.
