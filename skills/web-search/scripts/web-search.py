#!/usr/bin/env python3
"""
SearXNG web search client.

Usage:
  python3 web-search.py "your query" [options]

Options:
  --categories general,it,news,science   Search categories (default: general)
  --language en                          Result language (default: auto)
  --pageno 1                            Page number (default: 1)
  --time-range day|week|month|year       Time filter (default: none)
  --max-results 10                       Max results to return (default: 10)
  --base-url http://localhost:4000       SearXNG base URL
  --raw                                  Print raw SearXNG JSON
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


def search(query, base_url="http://localhost:4000", categories="general",
           language="auto", pageno=1, time_range="", max_results=10, raw=False):
    """Perform a SearXNG search and return structured results."""
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
    req = urllib.request.Request(url, headers={"User-Agent": "web-search-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if raw:
        return data

    results = []
    for r in data.get("results", [])[:max_results]:
        entry = {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
            "engine": r.get("engine", ""),
        }
        if r.get("publishedDate"):
            entry["published_date"] = r.get("publishedDate")
        results.append(entry)

    output = {
        "query": query,
        "number_of_results": data.get("number_of_results", 0),
        "results": results,
        "suggestions": data.get("suggestions", []),
    }

    infoboxes = data.get("infoboxes", [])
    if infoboxes:
        output["infoboxes"] = [
            {"title": ib.get("infobox", ""), "content": ib.get("content", ""), "url": ib.get("id", "")}
            for ib in infoboxes
        ]

    return output


def main():
    parser = argparse.ArgumentParser(description="SearXNG web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--categories", default="general", help="Categories: general,news,it,science,files,music,videos,images,social media (default: general)")
    parser.add_argument("--language", default="auto", help="Result language (default: auto)")
    parser.add_argument("--pageno", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument("--time-range", default="", help="Time filter: day, week, month, year")
    parser.add_argument("--max-results", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--base-url", default="http://localhost:4000", help="SearXNG URL (default: http://localhost:4000)")
    parser.add_argument("--raw", action="store_true", help="Print raw SearXNG JSON")
    args = parser.parse_args()

    try:
        result = search(
            query=args.query, base_url=args.base_url, categories=args.categories,
            language=args.language, pageno=args.pageno, time_range=args.time_range,
            max_results=args.max_results, raw=args.raw,
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
