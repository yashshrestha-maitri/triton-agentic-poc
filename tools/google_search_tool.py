"""Google Search Tool for WebSearchAgent.

Provides web search capabilities with automatic fallback:
1. Tavily Search API (if TAVILY_API_KEY is set) - Best quality, AI-optimized
2. DuckDuckGo (free fallback) - No API key needed
3. Mock mode (development) - Returns fake data

This provides seamless degradation: premium → free → mock
"""

from typing import List, Dict, Any, Optional
import os
from agno.tools import Toolkit
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class GoogleSearchTool(Toolkit):
    """Tool for performing Google-style web searches.

    Search provider priority:
    1. Tavily API (if TAVILY_API_KEY set) - Best for production
    2. DuckDuckGo (free, no key) - Good for development/testing
    3. Mock mode - Fallback if nothing works

    Configuration:
        TAVILY_API_KEY: Optional. If set, uses Tavily (premium)
                        If not set, uses DuckDuckGo (free)
    """

    def __init__(self):
        """Initialize Google Search Tool with automatic provider selection."""
        super().__init__(name="google_search")
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.search_provider = None  # Will be: 'tavily', 'duckduckgo', or 'mock'

        # Try Tavily first (premium)
        if self.api_key:
            if self._init_tavily():
                return

        # Fallback to DuckDuckGo (free)
        if self._init_duckduckgo():
            return

        # Final fallback to mock mode
        logger.warning(
            "No search provider available. Using mock mode. "
            "For real search: pip install ddgs OR set TAVILY_API_KEY"
        )
        self.search_provider = 'mock'

    def _init_tavily(self) -> bool:
        """Try to initialize Tavily Search API.

        Returns:
            True if Tavily initialized successfully
        """
        try:
            from tavily import TavilyClient
            self.tavily_client = TavilyClient(api_key=self.api_key)
            self.search_provider = 'tavily'
            logger.info("✅ Tavily Search API initialized (premium mode)")
            return True
        except ImportError:
            logger.warning(
                "TAVILY_API_KEY is set but tavily-python not installed. "
                "Install with: pip install tavily-python"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
            return False

    def _init_duckduckgo(self) -> bool:
        """Try to initialize DuckDuckGo search.

        Returns:
            True if DuckDuckGo initialized successfully
        """
        try:
            from ddgs import DDGS
            # Test that it works
            self.ddgs = DDGS
            self.search_provider = 'duckduckgo'
            logger.info("✅ DuckDuckGo Search initialized (free mode)")
            return True
        except ImportError:
            logger.warning(
                "ddgs not installed. "
                "Install with: pip install ddgs"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize DuckDuckGo: {e}")
            return False

    def google_search(
        self,
        query: str,
        max_results: int = 5,
        include_raw_content: bool = False
    ) -> List[Dict[str, Any]]:
        """Perform a Google-style web search.

        Automatically uses best available search provider:
        - Tavily (if API key configured)
        - DuckDuckGo (free fallback)
        - Mock (development fallback)

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            include_raw_content: Include raw page content in results (default: False)

        Returns:
            List of search results with structure:
            [
                {
                    "title": "Page title",
                    "url": "https://example.com",
                    "snippet": "Brief description...",
                    "content": "Full page content (if include_raw_content=True)",
                    "score": 0.95
                },
                ...
            ]

        Example:
            results = tool.google_search("Livongo diabetes management", max_results=10)
            for result in results:
                print(f"{result['title']}: {result['url']}")
        """
        logger.info(f"Searching with {self.search_provider}: '{query}' (max_results={max_results})")

        if self.search_provider == 'tavily':
            return self._search_tavily(query, max_results, include_raw_content)
        elif self.search_provider == 'duckduckgo':
            return self._search_duckduckgo(query, max_results, include_raw_content)
        else:
            return self._search_mock(query, max_results)

    def _search_tavily(
        self,
        query: str,
        max_results: int,
        include_raw_content: bool
    ) -> List[Dict[str, Any]]:
        """Search using Tavily API (premium).

        Args:
            query: Search query
            max_results: Max results to return
            include_raw_content: Include full page content

        Returns:
            List of search results
        """
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                include_raw_content=include_raw_content,
                search_depth="advanced"  # Use advanced mode for better results
            )

            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:500],  # Limit snippet length
                    "content": item.get("raw_content", "") if include_raw_content else "",
                    "score": item.get("score", 0.0),
                    "source": "tavily"
                })

            logger.info(f"Tavily found {len(results)} results for: '{query}'")
            return results

        except Exception as e:
            logger.error(f"Tavily search failed for '{query}': {e}")
            logger.info("Falling back to DuckDuckGo...")
            return self._search_duckduckgo(query, max_results, include_raw_content)

    def _search_duckduckgo(
        self,
        query: str,
        max_results: int,
        include_raw_content: bool
    ) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (free).

        Args:
            query: Search query
            max_results: Max results to return
            include_raw_content: Include full page content (via Jina Reader)

        Returns:
            List of search results
        """
        try:
            with self.ddgs() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results))

            results = []
            for item in raw_results:
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", "")[:500],
                    "score": 0.8,  # DDG doesn't provide scores
                    "source": "duckduckgo"
                }

                # Optionally fetch full content via Jina Reader (free)
                if include_raw_content:
                    result["content"] = self._fetch_content_jina(item.get("href", ""))
                else:
                    result["content"] = ""

                results.append(result)

            logger.info(f"DuckDuckGo found {len(results)} results for: '{query}'")
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed for '{query}': {e}")
            logger.info("Falling back to mock mode...")
            return self._search_mock(query, max_results)

    def _fetch_content_jina(self, url: str) -> str:
        """Fetch full page content using Jina AI Reader (free).

        Jina Reader converts any URL to clean markdown optimized for LLMs.
        Free tier: 1000 requests/month

        Args:
            url: URL to fetch

        Returns:
            Clean markdown content
        """
        try:
            import requests
            response = requests.get(
                f"https://r.jina.ai/{url}",
                timeout=10,
                headers={"X-Return-Format": "markdown"}
            )
            content = response.text[:10000]  # Limit to 10K chars
            logger.debug(f"Jina Reader fetched {len(content)} chars from {url}")
            return content
        except Exception as e:
            logger.warning(f"Jina Reader failed for {url}: {e}")
            return ""

    def _search_mock(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Return mock search results for testing.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Mock search results
        """
        logger.warning(f"Using mock search results for query: '{query}'")

        mock_results = [
            {
                "title": f"Mock Result 1 for '{query}'",
                "url": f"https://example.com/mock1?q={query.replace(' ', '+')}",
                "snippet": f"This is a mock search result for testing. Query: {query}. "
                          "This simulates what would be returned from a real search API.",
                "content": "",
                "score": 0.95,
                "source": "mock"
            },
            {
                "title": f"Mock Result 2 for '{query}'",
                "url": f"https://example.com/mock2?q={query.replace(' ', '+')}",
                "snippet": "Another mock result with sample content. "
                          "Install ddgs for free real search, or set TAVILY_API_KEY for premium.",
                "content": "",
                "score": 0.87,
                "source": "mock"
            },
            {
                "title": f"Mock Result 3 for '{query}'",
                "url": f"https://example.com/mock3?q={query.replace(' ', '+')}",
                "snippet": "Third mock result for completeness. "
                          "pip install ddgs OR pip install tavily-python",
                "content": "",
                "score": 0.75,
                "source": "mock"
            }
        ]

        return mock_results[:max_results]

    def register_tools(self) -> List[Any]:
        """Register tool functions with Agno.

        Returns:
            List of tool functions available to the agent
        """
        return [self.google_search]


# Convenience function for direct usage
def create_google_search_tool() -> GoogleSearchTool:
    """Create and return a GoogleSearchTool instance.

    Automatically selects best available search provider:
    1. Tavily (if TAVILY_API_KEY set)
    2. DuckDuckGo (if duckduckgo-search installed)
    3. Mock mode (fallback)

    Returns:
        Configured GoogleSearchTool

    Example:
        tool = create_google_search_tool()
        results = tool.google_search("healthcare ROI analysis")
    """
    return GoogleSearchTool()
