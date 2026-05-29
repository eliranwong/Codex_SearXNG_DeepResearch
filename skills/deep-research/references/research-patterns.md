# Research Patterns

## Pattern: Fact Verification

1. Search the claim with `scripts/search.py`
2. Search counter-claims or opposing viewpoints
3. Fetch content from 2–3 authoritative sources on each side
4. Synthesize: note what sources agree on, what they dispute, and what's unverified

## Pattern: Literature Review

1. Broad search: `scripts/search.py "topic survey overview"`
2. Drill down: search for specific subtopics or methods
3. Fetch seminal papers/reviews: `scripts/fetch.py` on top `.edu`, `.org`, arxiv URLs
4. Organize by: methodology, findings, year, relevance

## Pattern: Current Events / Breaking News

1. Use `--categories news --time-range day` for the latest
2. Expand to `--time-range week` for context
3. Cross-reference with `--categories general` for analysis pieces
4. Fetch key articles for details beyond headlines

## Pattern: Technical Deep-Dive

1. Use `--categories it` for tech-focused results
2. Search for official documentation, GitHub repos, Stack Overflow answers
3. Fetch official docs pages and RFCs
4. Compare multiple implementations or approaches

## Pattern: Comparison Research

1. Search for each option separately
2. Search for direct comparisons: "A vs B"
3. Fetch detailed comparison articles
4. Synthesize a comparison table from multiple sources

## Pattern: How-To / Tutorial Research

1. Search for the topic with keywords: tutorial, guide, walkthrough, how to
2. Fetch top tutorial pages
3. Extract step-by-step instructions from fetched content
4. Cross-reference with official documentation

## Source Credibility Heuristics

When prioritizing sources for deep-fetch:

| Priority | Source Types | Examples |
|----------|-------------|----------|
| Highest | Official docs, government, academic | `.gov`, `.edu`, RFCs, W3C |
| High | Established organizations, standards bodies | `.org`, IEEE, ACM |
| Medium | Reputable publications, expert blogs | Major tech blogs, established news |
| Low | Forums, social media, personal blogs | Reddit, Twitter/X, Medium |

## Handling Conflicts

- If 2+ authoritative sources disagree, present both positions
- Note which sources support which position
- Check publication dates — newer sources may supersede older ones
- Consider source expertise: a domain specialist outranks a generalist

## Output Formatting

Always structure research output as:

```
## Summary
[Brief overview of findings]

## Key Findings
- Finding 1 [1]
- Finding 2 [2][3]

## Detailed Analysis
[In-depth discussion]

## Conflicting Information
[Any disagreements between sources]

## Limitations
[What couldn't be verified, data gaps]

## Sources
[1] Title — URL
[2] Title — URL
```
