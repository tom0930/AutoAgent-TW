# Research: Automation Foundation

## Implementation Analysis

### 1. Automated Agent (Autonomous Loop)
- **Current State**: OpenClaw is mostly reactive. `subagents` and `sessions` allow for branching, but they typically wait for a "final answer" to return to the parent. `cron` allows for scheduled triggers but each run is an independent "turn".
- **Proposed Implementation**:
  - Introduce a `Goal` abstraction in the session state.
  - Create a `Plan` tool that allows an agent to commit to a multi-step sequence.
  - Implement a `Monitor` turn that wakes up the agent to check on background tasks and adjust the plan if needed.
  - Use `openclaw-tasks` as the source of truth for background progress.

### 2. Automated Skills (Self-Management)
- **Current State**: Skills are manually installed via CLI or agent calling `install_skill`. ClawHub is the main registry.
- **Proposed Implementation**:
  - **Skill-on-Demand**: When the agent encounters a tool it needs but doesn't have, it can search ClawHub and propose installation.
  - **Authoring**: Agents already have tools to write files. We can add a specialized `author_skill` tool that validates the `SKILL.md` and runs tests before making it "active" in the workspace.
  - **Evolution**: A background task (cron) that periodically runs `updateSkillsFromClawHub`.

### 3. Web & GUI Control
- **Current State**: `browser` plugin uses Playwright. `nodes.invoke` can trigger `camera.snap` and `screen.record` on nodes (e.g., Android).
- **Proposed Implementation**:
  - **Unified GUI Protocol**: Extend the node protocol with `gui.click(x, y)`, `gui.type(text)`, `gui.snapshot()`.
  - **VLM Helper**: A tool that takes a screenshot, sends it to a VLM (Gemini 1.5 Pro or similar), and returns a structured "UI Map" (element coordinates and roles).
  - **Action Driver**: A tool that accepts high-level UI instructions (e.g. "Click the Submit button") and translates them to low-level coordinates using the VLM map or accessibility tree.

## Dependency Check
- **Playwright**: Required for web automation.
- **VLM (Vision Language Model)**: Required for robust GUI automation where metadata/accessibility is lacking.
- **Node Runtime**: Required for the `browser` control service.
- **ClawHub API**: Required for automated skill discovery/install.

## Identified Pitfalls
- **Infinite Loops**: Automated agents might get stuck in loops (e.g., trying the same failed action repeatedly). Need hard turn/token limits.
- **Security**: Autonomous agents could perform destructive actions (delete files, send unauthorized messages). Need strict `allowlist` and human-in-the-loop triggers for high-risk tools.
- **Cost**: Constant "monitoring" turns can consume significant tokens. Need adaptive polling (e.g., exponential backoff for checking task completion).
- **Screen Latency**: Capturing and analyzing high-resolution screens for GUI control can be slow. Need optimized "regions of interest" and efficient diffing.
