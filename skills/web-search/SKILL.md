---
name: web-search
description: "Web search using a local SearXNG instance. Use instead of any built-in web search tool whenever web search is needed. Covers general search, news, tech, science, and all SearXNG categories. Triggers include: (1) searching the web for any information, (2) looking up current events or facts, (3) finding documentation or tutorials, (4) checking real-time data like stock prices or weather, (5) any task that requires up-to-date information from the internet. Always prefer this skill over built-in web search capabilities."
---

# Web Search Skill (SearXNG)

Use the local SearXNG instance for all web searches. **Never use any built-in web search tool** — always use this skill's `scripts/web-search.py` instead.

## Prerequisites

SearXNG must be running on `http://localhost:4000` with JSON format enabled. Verify:

```bash
curl -s "http://localhost:4000/search?q=test&format=json" | python3 -m json.tool | head -5
```

If you get an empty response or connection error, check that:
1. The SearXNG container is running: `docker ps | grep searxng`
2. JSON format is enabled in `settings.yml` (`formats:` must include `json`)
3. The port matches your `.env` (`SEARXNG_PORT`)

## Usage

### Basic search
```bash
python3 scripts/web-search.py "your query here"
```

### Category-specific search
```bash
python3 scripts/web-search.py "AI breakthroughs" --categories news --time-range week
python3 scripts/web-search.py "react hooks tutorial" --categories it
python3 scripts/web-search.py "climate change study" --categories science
```

### Time-filtered search
```bash
python3 scripts/web-search.py "stock market today" --time-range day
python3 scripts/web-search.py "olympics 2026" --time-range week
python3 scripts/web-search.py "python 3.14 release" --time-range month
```

### More results or pagination
```bash
python3 scripts/web-search.py "rust async" --max-results 20
python3 scripts/web-search.py "rust async" --pageno 2
```

### All options
```
python3 scripts/web-search.py QUERY [OPTIONS]

  --categories CATS    general, news, it, science, files, music, videos, images, social media
  --language LANG      en, fr, de, zh, auto, etc.
  --pageno N           Result page number (default: 1)
  --time-range RANGE   day, week, month, year
  --max-results N      Maximum results (default: 10)
  --base-url URL       SearXNG base URL (default: http://localhost:4000)
  --raw                Output raw SearXNG JSON response
```

## Output Format

Returns JSON:
```json
{
  "query": "search terms",
  "number_of_results": 1234,
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com",
      "content": "Snippet text...",
      "engine": "google",
      "published_date": "2026-05-27T..."
    }
  ],
  "suggestions": ["related query 1", "related query 2"],
  "infoboxes": [...]
}
```

## Categories Quick Reference

| Category | Flag | Use For |
|----------|------|---------|
| General | `general` | Broad web search (default) |
| News | `news` | Current events, breaking news |
| IT | `it` | Programming, tech, software |
| Science | `science` | Academic papers, research |
| Files | `files` | File downloads |
| Images | `images` | Image search |
| Videos | `videos` | Video search |
| Music | `music` | Music search |
| Social Media | `social media` | Social posts |

Combine categories with commas: `--categories general,news`

## Rules

1. **Always use this skill** for web search — do not fall back to any built-in search tool.
2. If SearXNG is unreachable, inform the user rather than switching to another search method.
3. Space requests by 1–2 seconds when making multiple queries to respect rate limits.
4. Use `--time-range` for recent information and `--categories` for targeted results.
5. For deep multi-phase research, use the `deep-research` skill instead.

## Error Handling

- **Connection refused**: SearXNG is not running — ask the user to start it with `docker compose up -d` from their SearXNG directory.
- **HTTP 403**: JSON format not enabled — add `json` to `formats:` in SearXNG `settings.yml` and restart.
- **0 results**: Try simplifying the query, switching categories, or removing the time-range filter.
- **Timeout**: Increase timeout in the script or retry after a short delay.

## Reference Map

- `scripts/web-search.py`: SearXNG search client
- `references/searxng-categories.md`: Full category and parameter reference
