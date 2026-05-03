# AI_PRODUCT.md: Value Proposal & Product Strategy

## The Problem: The Evaporation of Context
In modern AI-assisted development, 95% of the data (decisions made in chat) disappears when the session ends. This results in:
- Repeated "Why did we do this?" questions.
- Loss of technical reasoning for complex trade-offs.
- Inconsistent architecture across multiple sessions.
- High manual effort to "remind" the AI of project goals.

## The Solution: The Persistent Brain (MemPalace)
MemPalace is the foundational "Brain" for AutoAgent-TW. By storing everything and making it semantic-findable, we turn a "stateless" AI into a "stateful" Project Assistant.

## Key Value Propositions (MVP)
1. **Verbatim Recall (96.6% accuracy)**: Search verbatim text from any past conversation.
2. **Local & Free**: No monthly subscriptions, no data leaks, no API costs for memory.
3. **Structured Context**: Wings and Rooms provide 34% better retrieval performance than flat search.
4. **Temporal Intelligence**: The Knowledge Graph knows what was true *last month* vs. *today*.

## User Experience Design
- **One-Click Setup**: The `AutoAgent-TW` installer handles everything. Only `git clone` and `pip install mempalace` required.
- **Invisible Execution**: Workflows (`/aa-memory`) and future auto-save hooks (`mempal_save_hook.sh`) ensure the user never has to "save" manually.
- **Natural Language Query**: Users ask "What did we decide about the installer last week?" and the AI uses `mempalace_search` to answer.

## Roadmap towards V3.0
- **Phase 1 (Integrated)**: Manual search and automated installer integration.
- **Phase 2 (Automated)**: Auto-save hooks on session end; background mining of every code edit.
- **Phase 3 (Agentic)**: Autonomous agents writing their own diaries and building expertise.
- **Phase 4 (Scaling)**: Support for cross-project "tunnels" allowing the user's AI to carry knowledge from Project A to Project B.

## Cost & Token Optimization
| Approach | Token Load | Estimated Annual Cost |
|----------|------------|-----------------------|
| Paste all history | ~20M | Impossible (Context limit) |
| LLM summary | ~650K | ~$500/year (GPT-4o) |
| **MemPalace Retrieval** | **~13K** | **~$10/year** |

MemPalace isn't just a memory tool; it's a cost-saving mechanism for high-frequency AI development.

---

## Phase 170: Industrial Resilience & Efficiency
Phase 170 moves AutoAgent-TW from a "smart tool" to a "production-ready agent system".

### 1. The "Zero-Latency" User Experience
By implementing **Async Shadow Mode** and **Async Compression**, we ensure that the user never waits for the system to "think about its memory". The agent responds instantly, while the background threads optimize the context.

### 2. The "Hard Gate" Quality Assurance
In industrial contexts, "Wrong Memory" is worse than "No Memory". The **Compression Quality Gate** provides a mathematical guarantee that the AI's summary is accurate and concise, reducing the risk of hallucination in complex projects.

### 3. Business Continuity (HMAC & Checkpoints)
For professional teams, losing a session due to a crash or a Ctrl+C interruption is a loss of billable hours. Our **Interruptible Checkpointing** system ensures that every minute of AI work is persisted and verifiable via HMAC.

### 4. Cost Optimization Matrix (Updated)
| Feature | Efficiency Gain | UX Impact |
|---------|-----------------|-----------|
| **Auto-Compression** | 60-85% Token reduction | Zero (Background) |
| **Shadow Mode** | 100% Resilience | Zero (Background) |
| **Input Sanitizer** | Prevents wasted tokens on malformed queries | High (Safety) |
