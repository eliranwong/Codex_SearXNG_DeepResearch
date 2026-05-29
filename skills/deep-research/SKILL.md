---
name: deep-research
description: "Multi-phase deep web research using SearXNG for search and web fetch for detail extraction. Use when Codex needs to investigate a topic thoroughly, find current information, compare sources, or produce a research synthesis. Covers broad discovery, targeted subtopic drilling, and deep content extraction from authoritative sources. Triggers include: (1) researching a topic in depth, (2) finding current/real-time information beyond training data, (3) comparing multiple sources on a subject, (4) producing a literature review or research summary, (5) any task requiring up-to-date web information with citations, (6) investigating claims or fact-checking across sources."
---

# Deep Research Skill

Multi-phase web research using a local SearXNG instance for search and URL fetching for content extraction.

## Architecture

Three scripts work together:

- **`scripts/search.py`** — SearXNG search client. Queries the local SearXNG JSON API and returns structured results.
- **`scripts/fetch.py`** — Web page fetcher. Retrieves a URL, extracts clean readable text, handles HTML/PDF/JSON.
- **`scripts/research.py`** — Orchestrator. Runs a multi-phase research pipeline combining search + fetch automatically.

All scripts are pure Python 3 with no external dependencies (uses only `urllib`, `json`, `re`). `PyPDF2` is optional for PDF extraction.

## Prerequisites

1. **SearXNG** must be running locally on `http://localhost:4000` with JSON format enabled.
2. JSON format must be listed under `formats:` in SearXNG `settings.yml`:
   ```yaml
   formats:
     - html
     - json
     - csv
   ```
3. Verify: `curl -s "http://localhost:4000/search?q=test&format=json" | python3 -m json.tool | head -5`
4. If using a different host/port, pass `--base-url` to any script.

## Quick Start

### Simple Search
```bash
python3 scripts/search.py "quantum computing 2025"
python3 scripts/search.py "AI safety frameworks" --categories general,it --max-results 15
```

### Fetch a Page
```bash
python3 scripts/fetch.py "https://example.com/article"
python3 scripts/fetch.py "https://arxiv.org/abs/2401.0001" --max-length 12000 --headers
```

### Full Research Pipeline
```bash
python3 scripts/research.py "transformer architecture explained" --depth standard
python3 scripts/research.py "COVID vaccine efficacy studies" --depth deep --max-sources 8 --output markdown
python3 scripts/research.py "rust vs go performance" --depth quick --categories it
```

## Research Depth Levels

| Depth | Phases | Use When |
|-------|--------|----------|
| `quick` | 1 broad search + top-source fetch | Need a fast overview, limited time |
| `standard` | Broad search → subtopic search → deep fetch | Balanced research for most topics |
| `deep` | Multi-query broad search → subtopic search → extended deep fetch | Thorough investigation, academic research |

## Research Workflow

When conducting deep research, follow this workflow:

### Phase 1: Broad Discovery
1. Run `scripts/search.py` with the primary query.
2. Review result titles and snippets — identify key themes, authoritative sources, and knowledge gaps.
3. If `suggestions` are returned, note them for Phase 2.

### Phase 2: Targeted Drilling
1. Generate 2–5 subtopic queries based on Phase 1 findings.
2. Run `scripts/search.py` for each subtopic query.
3. Merge and deduplicate results by URL.
4. Prioritize `.gov`, `.edu`, `.org`, and well-known sources.

### Phase 3: Deep Content Extraction
1. Select the top 3–8 most relevant and authoritative URLs from Phases 1–2.
2. Run `scripts/fetch.py` on each URL to extract full text content.
3. Read the extracted content to understand nuance, data, and arguments.
4. If key claims reference other sources, consider fetching those too.

### Phase 4: Synthesis
1. Combine findings from all phases into a coherent response.
2. Cite sources using inline reference markers `[1]`, `[2]`, etc.
3. Note contradictions or disagreements between sources.
4. Include a "Sources" section with numbered links.
5. Flag information that could not be verified or where sources conflict.

## Script Reference

### search.py — SearXNG Search

```
python3 scripts/search.py QUERY [OPTIONS]

Options:
  --categories CATEGORIES   Search categories: general, news, it, science, files, music, videos, social media (default: general)
  --language LANGUAGE        Result language: en, fr, de, auto, etc. (default: auto)
  --pageno NUMBER            Result page number (default: 1)
  --time-range RANGE         Filter: day, week, month, year, or omit for all (default: none)
  --max-results NUMBER       Maximum results to return (default: 10)
  --base-url URL             SearXNG base URL (default: http://localhost:4000)
  --raw                      Output raw SearXNG JSON response
```

Output JSON structure:
```json
{
  "query": "search terms",
  "number_of_results": 1234,
  "results": [
    {"title": "...", "url": "...", "content": "snippet...", "engine": "...", "published_date": "..."}
  ],
  "suggestions": ["related query 1", "related query 2"],
  "infoboxes": [{"title": "...", "content": "...", "url": "..."}]
}
```

### fetch.py — Web Page Fetcher

```
python3 scripts/fetch.py URL [OPTIONS]

Options:
  --max-length NUMBER   Maximum characters of extracted text (default: 8000)
  --raw                 Output raw page content without extraction
  --headers             Include metadata: title, description, links
  --timeout SECONDS     Request timeout (default: 30)
```

Output JSON structure:
```json
{
  "url": "https://...",
  "type": "html|json|text|pdf",
  "title": "Page Title",
  "description": "Meta description",
  "content": "Extracted readable text...",
  "links": [{"text": "Link text", "url": "https://..."}],
  "truncated": false
}
```

### research.py — Full Research Pipeline

```
python3 scripts/research.py QUERY [OPTIONS]

Options:
  --depth quick|standard|deep   Research depth (default: standard)
  --categories CATEGORIES        SearXNG search categories (default: general)
  --language LANGUAGE             Result language (default: auto)
  --max-sources NUMBER            Max sources to deep-fetch (default: 5)
  --base-url URL                  SearXNG base URL (default: http://localhost:4000)
  --output json|markdown          Output format (default: json)
  --output-file PATH              Write output to file
```

Output includes all three phases with results and fetched content. Use `--output markdown` for a human-readable report.

## Effective Search Strategies

- **Start broad, then narrow**: Use general queries first, then drill into specifics.
- **Use categories**: `--categories news` for current events, `--categories it` for tech, `--categories science` for research papers.
- **Time filtering**: Use `--time-range day` for breaking news, `--time-range year` for recent developments.
- **Multiple queries**: Run separate searches for different aspects of a complex topic.
- **Verify across sources**: Cross-reference claims from at least 2–3 independent sources.
- **Respect rate limits**: SearXNG aggregates many engines; avoid rapid repeated queries. Space requests by 1–2 seconds.

## Error Handling

- If SearXNG is unreachable, check: `curl http://localhost:4000/` and verify the container is running.
- If search returns 0 results, try simplifying the query or changing `--categories`.
- If fetch fails for a URL, the script returns an error object; skip that source and continue.
- For timeouts on fetch, increase `--timeout` or use `--max-length` to limit content size.
- If JSON format is not enabled, add `json` to `formats:` in SearXNG `settings.yml` and restart the container.

## Reference Map

- `scripts/search.py`: SearXNG API search client
- `scripts/fetch.py`: Web page fetcher and content extractor
- `scripts/research.py`: Multi-phase research orchestrator
- `references/searxng-api.md`: SearXNG API parameters and response format reference
- `references/research-patterns.md`: Common research patterns and templates
