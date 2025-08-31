"""
Minimal MCP server exposing a web_search tool via DuckDuckGo (no API key).

Protocol: Model Context Protocol (MCP)
Transport: stdio (default)

Run locally (example):
  python web_search_server.py

Client usage (via langchain-mcp-adapters): connect as command "python" with args ["/abs/path/to/web_search_server.py"].
"""

import json
import sys
from typing import List

from mcp.server import FastMCP


def duckduckgo_search(query: str, count: int = 5) -> List[dict]:
    """Simple, unauthenticated search using DuckDuckGo's HTML endpoint via ddg API wrapper.

    If ddg is not available, returns empty results gracefully.
    """
    try:
        from ddgs import DDGS  # lightweight, no API key
    except Exception:
        return []

    results: List[dict] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=count):
            results.append({
                "title": r.get("title"),
                "href": r.get("href"),
                "body": r.get("body"),
            })
    return results


# Create FastMCP server
server = FastMCP(name="job-agent-web-search")


@server.tool()
def web_search(query: str, count: int = 5) -> str:
    """Perform a web search and return top results as JSON.

    Args:
        query: Search query string
        count: Number of results to return (default 5)

    Returns:
        JSON string of [{title, href, body}]
    """
    results = duckduckgo_search(query, count=count)
    return json.dumps(results, ensure_ascii=False)


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    # Allow running as `python web_search_server.py`
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


