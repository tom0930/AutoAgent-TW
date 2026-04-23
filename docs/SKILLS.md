# Skill Framework Guide — AI Harness v1.1

## Overview

The AI Harness Skill Framework provides discoverable, composable, and safely-executable skill modules
with OpenClaw-compatible SKILL.md format support.

## Skill Directory Structure

```
skills/
  <skill-name>/
    SKILL.md          # REQUIRED — skill metadata + documentation
    references/       # optional supporting files
      *.md, *.py, *.json
    scripts/           # optional helper scripts
    config/            # optional skill-specific config
```

## SKILL.md Format

Every skill MUST have a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name
description: "One-line description for AI intent routing."
metadata: {"openclaw": {"emoji": "🔧"}}
---

# Skill Title — One-Line Tagline

## Trigger Examples [AUTO]
- "帮我做 X"
- "X 怎么做"
- "有没有可以……的技能"

## Usage
... full documentation in Markdown ...
```

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique skill identifier (kebab-case) |
| `description` | string | Yes | 1-sentence description for AI intent routing |
| `metadata.openclaw.emoji` | string | Recommended | Visual icon for skill listings |
| `metadata.openclaw.category` | string | No | Category: `integration`, `utility`, `analysis`, `creation`, `automation` |
| `metadata.openclaw.version` | string | No | Skill version |

## Trigger Patterns

Skills are matched via three methods (evaluated in order):

1. **Exact** — trigger string == input string (case-insensitive)
2. **Contains** — trigger string appears anywhere in input
3. **Regex** — trigger matches as regex pattern

### Recommended Trigger Pattern Format

```markdown
## Triggers [AUTO]
- 安装 xxx / install xxx / setup xxx
- configure xxx / config xxx
- "帮我装" / "help me install" / "how to install"
```

### OpenClaw-compatible Trigger Examples

Based on patterns from `find-skills` SKILL.md:

```markdown
## Trigger Examples [AUTO]
- "我怎么做 X" / "how do I do X"
- "找一个能做 X 的技能" / "find a skill that can X"
- "有没有可以……的技能" / "is there a skill for X"
- "帮我做 X" / "help me X"
```

## Skill Execution Model

```
User Input
    ↓
Intent Router (SkillEngine.list_skills → trigger match)
    ↓
SkillSandboxTester.run_test_isolated (optional)
    ↓
Skill.execute() → SkillResult
    ↓
Result + optional retry / rollback on failure
```

## Security Levels

| Level | Description | Requires |
|-------|-------------|----------|
| `normal` | Standard operations, no elevation | — |
| `elevated` | System-level operations | explicit user approval |
| `critical` | Network I/O, external API calls | user confirmation |

## Skill Development Checklist

- [ ] `SKILL.md` with frontmatter (`name`, `description`)
- [ ] At least one trigger pattern in `## Triggers [AUTO]`
- [ ] `## Usage` section with examples
- [ ] `references/` directory with supporting docs
- [ ] Test in sandbox before enabling in production
- [ ] Add to `skills/` index in `AI_HARNESS.md`

## Phase 3 Skill Additions

| Skill | Status | Notes |
|-------|--------|-------|
| `mcp-builder` | TODO | Build MCP server from OpenAPI spec |
| `github-skill` | TODO | GitHub API integration (PRs, issues, repos) |
| `bdpan-storage` | TODO | PAN/Baidu Cloud storage upload |
| `skill-vetter` | TODO | Validate skill quality / SKILL.md compliance |

## References

- OpenClaw `qclaw-skill-creator` skill — skill authoring guide
- OpenClaw `find-skills` skill — skill discovery patterns
- OpenClaw `self-improving` skill — self-correction workflow
