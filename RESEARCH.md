# 🔍 Research: biggoALL Multi-Source Engine

## 1. BigGo (Main Source)
- **Site**: `https://biggo.com.tw`
- **Pattern**: `https://biggo.com.tw/s/[QUERY]/?sort=lp` (Low Price)
- **API (Potential)**: `https://biggo.com.tw/api/v1/search?q=[QUERY]`
- **DOM Strategy**: BigGo uses client-side rendering. Using Python `requests` might hit a blank page. Need to check if a simple `headers` set can trigger JSON response or if we need `Playwright` as a fallback.
- **Update**: BigGo actually supports a fairly simple URL query for low-to-high price: `https://biggo.com.tw/s/[QUERY]/?sort=lp`.

## 2. PChome (Existing)
- **API**: `https://ecshweb.pchome.com.tw/search/v3.3/all/results`
- **Status**: Already working well. Just need to modularize.

## 3. MOMO
- **Site**: `https://m.momoshop.com.tw`
- **Pattern**: Much more aggressive anti-scraping.
- **Strategy**: Try mobile API or simplified search URLs.

## 4. CP Analysis Regex Enhancements
- Current: `(\d+)\s*(GB|G|TB|T)`
- Add: `(\d+)\s*吋` (Inches for screens)
- Add: `(\d+)\s*系列` (Generation)

## 5. Security - Prompt Injection Defense
- Ensure user input `--query` is sanitized before being passed to `urllib.parse.quote`.
- Prevent command injection if we ever use `os.system` (which we won't, using `subprocess` or `requests` instead).
