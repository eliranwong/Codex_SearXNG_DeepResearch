#!/usr/bin/env python3
"""
Deep research orchestration script for the deep-research skill.

Performs multi-phase research:
  Phase 1: Broad search — discover top sources
  Phase 2: Targeted search — drill into subtopics from Phase 1
  Phase 3: Deep fetch — retrieve and extract full content from key sources
  Phase 4: Synthesis — produce a structured summary with citations

Usage:
  python3 research.py "your research query" [options]

Options:
  --depth quick|standard|deep     Research depth (default: standard)
  --categories general            SearXNG categories
  --language auto                 Result language
  --max-sources 5                 Max sources to deep-fetch (default: 5)
  --base-url http://localhost:4000  SearXNG base URL
  --output json|markdown          Output format (default: json)
  --output-file PATH              Write output to file instead of stdout
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
import re


def search_searxng(query, base_url="http://localhost:4000", categories="general",
                   language="auto", pageno=1, time_range="", max_results=10):
    """Search SearXNG and return parsed results."""
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

    return {
        "query": query,
        "number_of_results": data.get("number_of_results", 0),
        "results": results,
        "suggestions": data.get("suggestions", []),
        "infoboxes": data.get("infoboxes", []),
    }


def fetch_url(url, max_length=8000, timeout=30):
    """Fetch a URL and extract readable text content."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type", "")
        charset = "utf-8"
        ct_match = re.search(r"charset=([^\s;]+)", content_type, re.IGNORECASE)
        if ct_match:
            charset = ct_match.group(1).strip('"').strip("'")
        body = resp.read()

        # Skip non-text content
        if any(skip in content_type for skip in ["image/", "video/", "audio/", "application/octet-stream"]):
            return None

        try:
            text = body.decode(charset, errors="replace")
        except (LookupError, UnicodeDecodeError):
            text = body.decode("utf-8", errors="replace")

    # Extract from HTML
    if "text/html" in content_type or "<html" in text[:500].lower():
        # Title
        title = ""
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = re.sub(r"\s+", " ", title_match.group(1)).strip()

        # Clean HTML
        cleaned = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<nav[^>]*>.*?</nav>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<header[^>]*>.*?</header>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<footer[^>]*>.*?</footer>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<aside[^>]*>.*?</aside>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<br\s*/?\s*>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</?(?:p|div|h[1-6]|li|tr|blockquote|section|article)[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        cleaned = cleaned.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        cleaned = cleaned.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

        return {"title": title, "content": cleaned[:max_length], "truncated": len(cleaned) > max_length}

    # Plain text / JSON
    return {"title": "", "content": text[:max_length], "truncated": len(text) > max_length}


def generate_subtopic_queries(original_query, search_results):
    """Generate subtopic queries from initial search results."""
    subtopics = set()
    for r in search_results[:5]:
        snippet = r.get("content", "")
        # Extract key phrases from snippets (simple heuristic)
        words = snippet.split()
        for i in range(len(words) - 2):
            phrase = " ".join(words[i:i+3])
            if len(phrase) > 10 and original_query.lower().split()[0].lower() not in phrase.lower():
                subtopics.add(phrase)

    # Also use SearXNG suggestions
    return list(subtopics)[:3]  # Limit to 3 subtopic queries


def research(query, depth="standard", categories="general", language="auto",
             max_sources=5, base_url="http://localhost:4000"):
    """
    Execute a multi-phase deep research process.

    Returns a dict with all collected data for synthesis.
    """
    result = {
        "query": query,
        "depth": depth,
        "phases": {},
    }

    # Phase 1: Broad search
    phase1_queries = [query]
    if depth == "deep":
        # Add variation queries for deep research
        phase1_queries.append(f"what is {query}")
        phase1_queries.append(f"{query} overview guide")

    phase1_results = []
    for q in phase1_queries:
        try:
            search = search_searxng(q, base_url=base_url, categories=categories,
                                     language=language, max_results=10)
            phase1_results.extend(search["results"])
        except Exception as e:
            result.setdefault("errors", []).append(f"Phase 1 search error for '{q}': {e}")

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in phase1_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    phase1_results = unique_results[:15 if depth == "deep" else 10]
    result["phases"]["phase1_broad_search"] = {
        "description": "Broad search to discover top sources",
        "queries": phase1_queries,
        "result_count": len(phase1_results),
        "results": phase1_results,
    }

    # Phase 2: Targeted subtopic search (standard and deep only)
    if depth in ("standard", "deep"):
        subtopic_queries = generate_subtopic_queries(query, phase1_results)
        if depth == "deep" and not subtopic_queries:
            subtopic_queries = [f"{query} latest research", f"{query} analysis"]

        phase2_results = []
        for sq in subtopic_queries:
            try:
                search = search_searxng(sq, base_url=base_url, categories=categories,
                                         language=language, max_results=5)
                phase2_results.extend(search["results"])
            except Exception as e:
                result.setdefault("errors", []).append(f"Phase 2 search error for '{sq}': {e}")

        seen_urls_phase2 = seen_urls.copy()
        unique_p2 = []
        for r in phase2_results:
            if r["url"] not in seen_urls_phase2:
                seen_urls_phase2.add(r["url"])
                unique_p2.append(r)

        result["phases"]["phase2_targeted_search"] = {
            "description": "Targeted search for subtopics and deeper information",
            "queries": subtopic_queries,
            "result_count": len(unique_p2),
            "results": unique_p2[:10],
        }
        phase1_results.extend(unique_p2[:10])

    # Phase 3: Deep fetch content from top sources
    # Prioritize URLs from authoritative domains
    priority_patterns = [
        r"\.gov", r"\.edu", r"\.org", r" wikipedia\.org", r" arxiv\.org",
        r" nature\.com", r" science\.org", r" ieee\.org", r" mit\.edu",
    ]
    scored = []
    for r in phase1_results:
        score = 0
        url = r.get("url", "")
        for pat in priority_patterns:
            if re.search(pat, url):
                score += 2
        # Prefer results with content snippets
        if r.get("content") and len(r.get("content", "")) > 50:
            score += 1
        scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    sources_to_fetch = [r for _, r in scored[:max_sources]]

    fetched_content = []
    for source in sources_to_fetch:
        url = source.get("url", "")
        if not url:
            continue
        try:
            content = fetch_url(url)
            if content:
                fetched_content.append({
                    "url": url,
                    "title": content.get("title", source.get("title", "")),
                    "content": content.get("content", ""),
                    "truncated": content.get("truncated", False),
                })
        except Exception as e:
            fetched_content.append({
                "url": url,
                "error": str(e),
            })

    result["phases"]["phase3_deep_fetch"] = {
        "description": "Deep content extraction from authoritative sources",
        "source_count": len(fetched_content),
        "sources": fetched_content,
    }

    return result


def format_markdown(research_data):
    """Format research results as a structured markdown report."""
    lines = []
    lines.append(f"# Deep Research: {research_data['query']}")
    lines.append(f"**Depth:** {research_data['depth'].capitalize()}")
    lines.append("")

    for phase_name, phase_data in research_data.get("phases", {}).items():
        phase_label = phase_name.replace("_", " ").title()
        lines.append(f"## {phase_label}")
        lines.append(f"*{phase_data['description']}*")
        lines.append("")

        if "queries" in phase_data:
            lines.append(f"**Queries:** {', '.join(f'`{q}`' for q in phase_data['queries'])}")
            lines.append("")

        if "results" in phase_data:
            lines.append(f"**Results:** {phase_data.get('result_count', len(phase_data['results']))} sources found")
            lines.append("")
            for r in phase_data["results"][:8]:
                lines.append(f"- [{r.get('title', 'Untitled')}]({r.get('url', '')})")
                if r.get("content"):
                    lines.append(f"  > {r['content'][:150]}...")
            lines.append("")

        if "sources" in phase_data:
            lines.append(f"**Sources fetched:** {phase_data.get('source_count', len(phase_data['sources']))}")
            lines.append("")
            for s in phase_data["sources"]:
                lines.append(f"### [{s.get('title', 'Untitled')}]({s.get('url', '')})")
                if s.get("error"):
                    lines.append(f"*Error: {s['error']}*")
                elif s.get("content"):
                    content = s["content"][:2000]
                    lines.append(content)
                    if s.get("truncated"):
                        lines.append("\n*[Content truncated]*")
                lines.append("")

    if research_data.get("errors"):
        lines.append("## Errors")
        for err in research_data["errors"]:
            lines.append(f"- {err}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Deep research orchestration")
    parser.add_argument("query", help="Research query")
    parser.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard",
                       help="Research depth (default: standard)")
    parser.add_argument("--categories", default="general", help="SearXNG categories (default: general)")
    parser.add_argument("--language", default="auto", help="Result language (default: auto)")
    parser.add_argument("--max-sources", type=int, default=5, help="Max sources to deep-fetch (default: 5)")
    parser.add_argument("--base-url", default="http://localhost:4000", help="SearXNG base URL")
    parser.add_argument("--output", choices=["json", "markdown"], default="json", help="Output format (default: json)")
    parser.add_argument("--output-file", help="Write output to file instead of stdout")
    args = parser.parse_args()

    try:
        data = research(
            query=args.query,
            depth=args.depth,
            categories=args.categories,
            language=args.language,
            max_sources=args.max_sources,
            base_url=args.base_url,
        )

        if args.output == "markdown":
            output = format_markdown(data)
        else:
            output = json.dumps(data, indent=2, ensure_ascii=False)

        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output written to {args.output_file}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
