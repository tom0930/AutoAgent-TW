# ROADMAP.md: The Future of AutoAgent-TW Memory

## Phase 1: Foundation (Current - V2.4.0)
- ✅ **MemPalace Integration**: Cloned from GitHub and installed locally.
- ✅ **Installer Logic**: Automated `init` and `mine` during installation.
- ✅ **Project Palace**: Local SQLite/ChromaDB per workspace.
- ✅ **CLI Shim**: Project-local `mempalace.cmd` created.

## Phase 2: Automation (Next - V2.5.0)
- **Auto-Save Hooks**: Implement `mempal_save_hook.sh` for Windows as a `.bat` or `.py` background process.
- **Pre-Commit Mining**: Automatically mine every Git commit to update the knowledge graph.
- **Silent Update**: Run `mempalace mine` in the background after major task completions.

## Phase 3: Intelligence (V3.0.0)
- **Agentic Diaries**: Agents autonomously write and update their specialists' diaries.
- **Conflict Detection**: Wire `fact_checker.py` into the workflow to flag contradictions in user or agent assertions.
- **Entity Linking**: Automatic cross-referencing between code files and conversation sessions.

## Phase 4: Scaling (V4.0.0)
- **The Global Palace**: Securely sharing "Tunnels" across different projects.
- **Visual Memory Map**: A 2D/3D visualization of the palace (wings, rooms) to help users explore their own project's history.
- **Voice Integration**: Ask the AI "What did we decide?" via voice and have it search and narrate the answer.
- [X] Phase 152: Type Checker Orchestration (Ty & Pyrefly Shadow Check) [DONE]
- [X] Phase 138: Windows GUI Automation (RVA & Vision Integration) [DONE]
- [X] Phase 153: Human-in-the-loop Verification Contracts [DONE]
- [X] Phase 160: AutoCLI Integration (v3.3.2) [DONE]
- [ ] Phase 129: Headless Mode + CI/CD Integration [BACKLOG]

## Feedback & Ideas
- **User Preference Mining**: Auto-detect habits and coding style to tailor future suggestions.
- **Collaborative Palace**: Real-time memory sync for teams working on the same repository.
- **AAAK Dialect v3**: Improved lossless compression to fit even more context into tiny windows.
