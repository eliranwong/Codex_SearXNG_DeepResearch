#!/usr/bin/env python3
"""
SearXNG search client for the deep-research skill.

Usage:
  python3 search.py "your query" [options]

Options:
  --categories general,it,news   Search categories (default: general)
  --language en                  Result language (default: auto)
  --pageno 1                    Page number (default: 1)
  --max-results 10              Maximum results to return (default: 10)
  --time-range ""               Time range: day, week, month, year, or "" for none
  --format json                 Output format: json (default)
  --base-url http://localhost:4000  SearXNG base URL
  --raw                         Print raw JSON response (no formatting)

Examples:
  python3 search.py "python async asyncio"
  python3 search.py "latest AI news" --categories news --time-range day
  python3 search.py "rust programming" --max-results 20
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


def search_searxng(
    query: str,
    base_url: str = "http://localhost:4000",
    categories: str = "general",
    language: str = "auto",
    pageno: int = 1,
    time_range: str = "",
    max_results: int = 10,
    raw: bool = False,
) -> dict:
    """Perform a SearXNG search and return parsed JSON results."""
    params = {
        "q": query,
        "format": "json",
        "categories": categories,
        "language": language,
        "pageno": pageno,
    }
    if time_range:
        params["time_range"] = time_range

    url = f"{base_url}/search?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"User-Agent": "deep-research-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if raw:
        return data

    results = data.get("results", [])[:max_results]
    suggestions = data.get("suggestions", [])
    infoboxes = data.get("infoboxes", [])

    output = {
        "query": query,
        "number_of_results": data.get("number_of_results", 0),
        "results": [],
        "suggestions": suggestions,
    }

    for r in results:
        entry = {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
            "engine": r.get("engine", ""),
        }
        if r.get("publishedDate"):
            entry["published_date"] = r.get("publishedDate")
        output["results"].append(entry)

    if infoboxes:
        for ib in infoboxes:
            output.setdefault("infoboxes", []).append({
                "title": ib.get("infobox", ""),
                "content": ib.get("content", ""),
                "url": ib.get("id", ""),
            })

    return output


def main():
    parser = argparse.ArgumentParser(description="SearXNG search client")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--categories", default="general", help="Search categories (default: general)")
    parser.add_argument("--language", default="auto", help="Result language (default: auto)")
    parser.add_argument("--pageno", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument("--time-range", default="", help="Time range: day, week, month, year")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results (default: 10)")
    parser.add_argument("--base-url", default="http://localhost:4000", help="SearXNG base URL")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON response")
    args = parser.parse_args()

    try:
        result = search_searxng(
            query=args.query,
            base_url=args.base_url,
            categories=args.categories,
            language=args.language,
            pageno=args.pageno,
            time_range=args.time_range,
            max_results=args.max_results,
            raw=args.raw,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}: {e.reason}", "url": e.url}, indent=2), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Connection failed: {e.reason}"}, indent=2), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
