---
name: autocli
description: "AutoCLI: Lightweight, Rust-based CDP/Web extraction engine. Use when: (1) Fetching structured data from 55+ platforms (GitHub, Twitter, Reddit, etc.) with zero-token overhead, (2) Direct browser session reuse via CDP, (3) Stealth mode web scraping with <50MB RAM. NOT for: complex multi-step UI automation (use RVA Eye-0), or local file manipulation."
metadata:
  {
    "openclaw":
      {
        "emoji": "👁️",
        "requires": { "bins": ["autocli"] },
        "install":
          [
            {
              "id": "manual",
              "kind": "binary",
              "bins": ["autocli"],
              "label": "AutoCLI Rust Binary (v0.3.8+)",
            },
          ],
      },
  }
---

# AutoCLI Skill

AutoCLI is a high-performance Rust executable that extracts structured information from web pages using Chrome DevTools Protocol (CDP). It serves as the **Eye-2** layer for AutoAgent-TW.

## When to Use

✅ **USE this skill when:**

- Fetching data from supported platforms (GitHub, Twitter, Reddit, LinkedIn, etc.)
- Scraping structured content from URLs without downloading full HTML
- Reusing existing Chrome/Edge sessions to bypass 2FA/login
- Executing "Stealth Mode" scraping with minimal memory footprint (<50MB)

## Setup

AutoCLI is located in the `bin/` directory. Access it via the relative path:
```bash
./bin/autocli --version
```

## Common Commands

### Fetch Structured Content

```bash
# Basic fetch (returns structured JSON)
./bin/autocli read https://github.com/nashsu/AutoCLI --format json

# Fetch using existing browser profile (bypass login)
./bin/autocli read https://github.com/nashsu/AutoCLI --format json --profile "Default"
```

### Manage Adapters

```bash
# Search for existing AI Adapters
./bin/autocli search github.com

# Explore a website for adapter generation
./bin/autocli generate https://example.com
```

### Browser Control

```bash
# List active browser targets
./bin/autocli target list
```

## JSON Output

AutoCLI returns structured JSON by default. This is highly efficient for AI context:

```json
{
  "title": "nashsu/AutoCLI",
  "stars": "1.2k",
  "description": "The Eye-2 for AI Agents",
  ...
}
```

## Notes

- **Stealth Mode**: AutoCLI is optimized for resource-constrained environments.
- **Context Guard**: Access is restricted to whitelisted domains by the AutoAgent-TW router.
- **Headless**: Default mode is headless unless `--headful` is specified.
