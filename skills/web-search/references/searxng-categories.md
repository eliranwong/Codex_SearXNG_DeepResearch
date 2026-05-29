# SearXNG Categories and Parameters Reference

## Search Categories

| Category | Key | Description | Typical Engines |
|----------|-----|-------------|-----------------|
| General | `general` | Broad web search | Google, Bing, DuckDuckGo, Brave, Startpage |
| News | `news` | News articles | Google News, Bing News, DuckDuckGo News |
| IT | `it` | Information technology | Stack Overflow, GitHub, DevDocs |
| Science | `science` | Academic/research | Google Scholar, Semantic Scholar, PubMed |
| Files | `files` | File search | Various file search engines |
| Images | `images` | Image search | Google Images, Bing Images, DuckDuckGo Images |
| Videos | `videos` | Video search | YouTube, Dailymotion, Vimeo |
| Music | `music` | Music search | Various music search engines |
| Social Media | `social media` | Social posts | Reddit, Twitter/X, Mastodon |

Combine with commas: `--categories general,news`

## Parameter Reference

| Parameter | CLI Flag | Values | Default |
|-----------|----------|--------|---------|
| Query | (positional) | Any string | Required |
| Categories | `--categories` | Comma-separated category keys | `general` |
| Language | `--language` | `auto`, `en`, `fr`, `de`, `es`, `zh`, `ja`, etc. | `auto` |
| Page | `--pageno` | Integer ≥ 1 | `1` |
| Time Range | `--time-range` | `day`, `week`, `month`, `year`, or empty | None |
| Max Results | `--max-results` | Integer | `10` |
| Base URL | `--base-url` | URL string | `http://localhost:4000` |
| Raw Output | `--raw` | Flag (no value) | Off |

## Time Range Tips

- `day` — last 24 hours, use for breaking news, live events
- `week` — last 7 days, use for recent developments
- `month` — last 30 days, use for current trends
- `year` — last 12 months, use for recent historical context
- Empty/omitted — no time filter, broadest results

## Language Tips

- `auto` — detect from browser/system (recommended default)
- `en` — English results
- `en-US` — American English specifically
- `zh` — Chinese results
- Use specific language codes when you need results in a particular language
