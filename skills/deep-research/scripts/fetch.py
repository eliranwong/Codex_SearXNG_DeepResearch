#!/usr/bin/env python3
"""
Web page fetcher and content extractor for the deep-research skill.

Fetches a URL and extracts clean, readable text content. Handles:
- HTML pages: extracts article text, strips navigation/chrome
- PDFs: extracts text content (requires PyPDF2 if available)
- Plain text / JSON: returns as-is
- Error handling with informative messages

Usage:
  python3 fetch.py "https://example.com" [options]

Options:
  --max-length 8000    Maximum characters of extracted text (default: 8000)
  --raw                Output raw page content (no extraction)
  --headers            Include page metadata (title, description, links)
  --timeout 30         Request timeout in seconds (default: 30)
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error


def extract_text_from_html(html: str, url: str = "") -> dict:
    """Extract readable text content from HTML, stripping boilerplate."""
    title = ""
    description = ""
    links = []

    # Extract title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()

    # Extract meta description
    desc_match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
        html, re.IGNORECASE,
    )
    if desc_match:
        description = desc_match.group(1).strip()
    else:
        desc_match = re.search(
            r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',
            html, re.IGNORECASE,
        )
        if desc_match:
            description = desc_match.group(1).strip()

    # Remove unwanted tags
    cleaned = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<nav[^>]*>.*?</nav>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<header[^>]*>.*?</header>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<footer[^>]*>.*?</footer>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<aside[^>]*>.*?</aside>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Extract links before stripping tags
    link_matches = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', cleaned, re.DOTALL | re.IGNORECASE)
    seen = set()
    for href, text in link_matches[:50]:
        text = re.sub(r"<[^>]+>", "", text).strip()
        if text and href and not href.startswith(("#", "javascript:")):
            if href.startswith("/"):
                # Convert relative URLs
                if url:
                    base = re.match(r"(https?://[^/]+)", url)
                    if base:
                        href = base.group(1) + href
            if href not in seen:
                links.append({"text": text[:100], "url": href[:500]})
                seen.add(href)

    # Replace common block elements with newlines
    cleaned = re.sub(r"<br\s*/?\s*>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</?(?:p|div|h[1-6]|li|tr|blockquote|section|article)[^>]*>", "\n", cleaned, flags=re.IGNORECASE)

    # Remove remaining tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)

    # Decode HTML entities
    cleaned = cleaned.replace("&amp;", "&")
    cleaned = cleaned.replace("&lt;", "<")
    cleaned = cleaned.replace("&gt;", ">")
    cleaned = cleaned.replace("&quot;", '"')
    cleaned = cleaned.replace("&#39;", "'")
    cleaned = cleaned.replace("&nbsp;", " ")

    # Normalize whitespace
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()

    return {
        "title": title,
        "description": description,
        "content": cleaned,
        "links": links,
    }


def fetch_url(
    url: str,
    max_length: int = 8000,
    raw: bool = False,
    headers: bool = False,
    timeout: int = 30,
) -> dict:
    """Fetch a URL and extract its content."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            charset = "utf-8"

            # Extract charset from content-type
            ct_match = re.search(r"charset=([^\s;]+)", content_type, re.IGNORECASE)
            if ct_match:
                charset = ct_match.group(1).strip('"').strip("'")

            body = resp.read()

            # Check if PDF
            if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                try:
                    import PyPDF2
                    import io
                    reader = PyPDF2.PdfReader(io.BytesIO(body))
                    text_parts = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    pdf_text = "\n\n".join(text_parts)
                    if raw:
                        return {"content": pdf_text, "url": url, "type": "pdf"}
                    return {
                        "url": url,
                        "type": "pdf",
                        "pages": len(reader.pages),
                        "content": pdf_text[:max_length],
                        "truncated": len(pdf_text) > max_length,
                    }
                except ImportError:
                    return {
                        "url": url,
                        "type": "pdf",
                        "error": "PyPDF2 not installed; cannot extract PDF text. Install with: pip install PyPDF2",
                        "content_hint": f"Binary PDF file ({len(body)} bytes)",
                    }

            # Decode text content
            try:
                text = body.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                text = body.decode("utf-8", errors="replace")

            # Check if JSON
            if "application/json" in content_type or url.lower().endswith(".json"):
                try:
                    parsed = json.loads(text)
                    formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                    return {
                        "url": url,
                        "type": "json",
                        "content": formatted[:max_length],
                        "truncated": len(formatted) > max_length,
                    }
                except json.JSONDecodeError:
                    pass

            # Check if HTML
            if "text/html" in content_type or "<html" in text[:500].lower() or "<!doctype html" in text[:500].lower():
                extracted = extract_text_from_html(text, url)
                if raw:
                    return {"content": text, "url": url, "type": "html"}

                result = {
                    "url": url,
                    "type": "html",
                    "title": extracted["title"],
                    "content": extracted["content"][:max_length],
                    "truncated": len(extracted["content"]) > max_length,
                }
                if headers:
                    result["description"] = extracted["description"]
                    result["links"] = extracted["links"][:20]
                return result

            # Plain text or other
            return {
                "url": url,
                "type": "text",
                "content": text[:max_length],
                "truncated": len(text) > max_length,
            }

    except urllib.error.HTTPError as e:
        return {"url": url, "error": f"HTTP {e.code}: {e.reason}", "type": "error"}
    except urllib.error.URLError as e:
        return {"url": url, "error": f"Connection failed: {e.reason}", "type": "error"}
    except Exception as e:
        return {"url": url, "error": str(e), "type": "error"}


def main():
    parser = argparse.ArgumentParser(description="Web page fetcher and content extractor")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--max-length", type=int, default=8000, help="Max characters of extracted text (default: 8000)")
    parser.add_argument("--raw", action="store_true", help="Output raw page content")
    parser.add_argument("--headers", action="store_true", help="Include metadata (title, description, links)")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)")
    args = parser.parse_args()

    result = fetch_url(
        url=args.url,
        max_length=args.max_length,
        raw=args.raw,
        headers=args.headers,
        timeout=args.timeout,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
