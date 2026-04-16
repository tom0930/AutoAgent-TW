# Requirements: AutoAgent-TW i18n support
Issue: #1

## Req-ID-01: Multi-language Header
- Every workflow (`_agents/workflows/*.md`) must have a bilingual or language-selectable description in the header.
- The description should ideally show both languages or use a standard multi-language format if the IDE supports it (or just "English / Chinese").

## Req-ID-02: User-selectable Language
- A configuration (e.g., in `.planning/config.json` or globally) that determines the primary language for the agent's internal reporting/steps.
- For now, providing dual-language is more robust for the UI.

## Req-ID-03: English Descriptions for Skills
- Each `SKILL.md` in `C:\Users\TOM\.gemini\antigravity\skills\` should also have an English translation in the description header.
