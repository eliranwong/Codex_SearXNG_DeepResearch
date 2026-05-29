# SearXNG API Reference

## Base URL

Default: `http://localhost:4000`

## Search Endpoint

`GET /search`

### Required Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query string |
| `format` | Must be `json` for API usage |

### Optional Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `categories` | `general`, `news`, `it`, `science`, `files`, `music`, `videos`, `images`, `social media` | `general` | Search category |
| `language` | `auto`, `en`, `fr`, `de`, `es`, `zh`, `ja`, etc. | `auto` | Result language |
| `pageno` | integer | `1` | Page number for pagination |
| `time_range` | `day`, `week`, `month`, `year`, or omit | none | Time filter |
| `safesearch` | `0` (None), `1` (Moderate), `2` (Strict) | `0` | Safe search level |
| `engines` | engine names (comma-separated) | all enabled | Restrict to specific engines |

### Response Format (JSON)

```json
{
  "query": "search terms",
  "number_of_results": 1234,
  "results": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "content": "Snippet text from the page...",
      "engine": "google",
      "engines": ["google", "bing"],
      "score": 1.5,
      "category": "general",
      "publishedDate": "2025-01-15T00:00:00+00:00"
    }
  ],
  "suggestions": ["related query 1", "related query 2"],
  "infoboxes": [
    {
      "infobox": "Topic Title",
      "content": "Summary text...",
      "id": "https://example.com/wiki/Topic",
      "urls": [
        {"title": "Wikipedia", "url": "https://..."}
      ]
    }
  ],
  "unresponsive_engines": []
}
```

### Categories

- `general` — General web search (default)
- `news` — News articles
- `it` — Information technology
- `science` — Scientific articles
- `files` — File search
- `music` — Music search
- `videos` — Video search
- `images` — Image search
- `social media` — Social media posts

### Multiple Categories

Pass comma-separated: `categories=general,news`

### Time Range Examples

- Recent 24 hours: `time_range=day`
- Past week: `time_range=week`
- Past month: `time_range=month`
- Past year: `time_range=year`

## Error Handling

- HTTP 429: Rate limited — wait and retry
- HTTP 403: Access denied — check `formats:` in settings.yml includes `json`
- Connection refused: SearXNG not running or wrong port
