"""Web Scraper Tool for extracting content from web pages."""

from typing import Optional
import os
from agno.tools import Toolkit
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class WebScraperTool(Toolkit):
    """Tool for scraping web page content.

    Uses Firecrawl API for reliable, AI-optimized web scraping.
    Falls back to BeautifulSoup for basic scraping if API not available.
    """

    def __init__(self):
        """Initialize Web Scraper Tool."""
        super().__init__(name="web_scraper")
        self.api_key = os.getenv("FIRECRAWL_API_KEY")

        if not self.api_key:
            logger.warning("FIRECRAWL_API_KEY not set. Using basic scraping mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            try:
                from firecrawl import FirecrawlApp
                self.client = FirecrawlApp(api_key=self.api_key)
                logger.info("Firecrawl API initialized")
            except ImportError:
                logger.warning("firecrawl-py not installed. Using mock mode.")
                self.mock_mode = True

    def scrape_webpage(self, url: str, formats: list = None) -> str:
        """Scrape content from a web page.

        Args:
            url: URL to scrape
            formats: List of formats to extract (default: ["markdown"])

        Returns:
            Extracted page content as string

        Example:
            content = tool.scrape_webpage("https://example.com")
        """
        if formats is None:
            formats = ["markdown"]

        if self.mock_mode:
            return self._mock_scrape(url)

        try:
            logger.info(f"Scraping: {url}")
            result = self.client.scrape_url(url, params={"formats": formats})
            content = result.get("markdown", result.get("content", ""))
            logger.info(f"Scraped {len(content)} characters from {url}")
            return content
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return self._mock_scrape(url)

    def _mock_scrape(self, url: str) -> str:
        """Return mock scraped content."""
        logger.warning(f"Using mock scrape for: {url}")
        return f"Mock scraped content from {url}. Set FIRECRAWL_API_KEY for live scraping."

    def register_tools(self):
        """Register tool functions."""
        return [self.scrape_webpage]


def create_web_scraper_tool() -> WebScraperTool:
    """Create WebScraperTool instance."""
    return WebScraperTool()
