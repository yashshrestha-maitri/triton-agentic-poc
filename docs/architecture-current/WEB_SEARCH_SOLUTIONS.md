# Web Search Solutions for AI Agents

## Table of Contents
1. [Why Do You Need a Web Search Solution?](#why-do-you-need-a-web-search-solution)
2. [Tavily vs Alternatives](#tavily-vs-alternatives)
3. [Open Source Alternatives](#open-source-alternatives)
4. [Building Your Own Search Solution](#building-your-own-search-solution)
5. [Cost Comparison](#cost-comparison)
6. [Recommendation Matrix](#recommendation-matrix)

---

## Why Do You Need a Web Search Solution?

### The Problem

Your **WebSearchAgent** needs to research real companies from the internet to extract:
- Value propositions
- Clinical outcomes
- ROI frameworks
- Competitive positioning
- Target audiences

**Without real search capability:**
- ❌ Agent relies on LLM training data (outdated after Jan 2025)
- ❌ Cannot research new/unknown companies
- ❌ Cannot verify claims with current sources
- ❌ Returns plausible but potentially incorrect information
- ❌ No real URLs to cite as sources

**With real search capability:**
- ✅ Gets current, up-to-date information from the web
- ✅ Can research any company (even startups founded yesterday)
- ✅ Verifies claims across multiple real sources
- ✅ Returns accurate, verifiable information with real URLs
- ✅ Enables autonomous research workflows

### When You Actually Need It

| Use Case | Need Real Search? |
|----------|-------------------|
| **Testing agent logic/validation** | ❌ No (mock mode is fine) |
| **Researching well-known companies** | ⚠️ Maybe (LLM training data might suffice) |
| **Researching unknown/new companies** | ✅ Yes (LLM has no training data) |
| **Getting current 2025+ information** | ✅ Yes (LLM training ends Jan 2025) |
| **Production value proposition derivation** | ✅ Yes (accuracy critical) |
| **Demo/prototype** | ❌ No (mock mode works) |
| **Verifying quantitative claims** | ✅ Yes (need real sources) |

---

## Tavily vs Alternatives

### What is Tavily?

**Tavily** is a search API **designed specifically for AI agents**. It's not just a search engine wrapper—it's optimized for LLM consumption.

#### What Makes Tavily Special for AI?

1. **Clean, Structured Output**
   ```json
   {
     "results": [
       {
         "title": "Livongo Health - Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Livongo_Health",
         "content": "Clean, relevant text extracted from page...",
         "score": 0.98,
         "raw_content": "Full page content if needed"
       }
     ]
   }
   ```

2. **Automatic Content Extraction**
   - Removes ads, popups, navigation, footers
   - Extracts only relevant content
   - Returns clean markdown or text

3. **Relevance Scoring**
   - Each result has confidence score
   - LLM can prioritize high-scoring results

4. **Search Depth Options**
   - `basic`: Fast, fewer sources
   - `advanced`: Comprehensive, more sources

5. **Built for Agents**
   - No rate limiting issues
   - Handles concurrent requests
   - Optimized for batch searches

### Tavily Pros & Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| Built specifically for AI agents | Paid service ($50-200/month) |
| Clean, LLM-ready content | Dependency on third-party service |
| No scraping/parsing needed | Not open source |
| Relevance scoring included | Limited customization |
| Fast and reliable | US-only search results |
| Easy integration (3 lines of code) | Requires API key management |

---

## Open Source Alternatives

### Option 1: **SearXNG** (Self-Hosted Meta Search)

**What it is:** Open-source, self-hosted meta search engine that aggregates results from Google, Bing, DuckDuckGo, and more.

#### How It Works
```
Your Agent → SearXNG Instance → Google/Bing/DDG → SearXNG → Agent
             (self-hosted)        (aggregated)
```

#### Setup
```bash
# Docker deployment
docker pull searxng/searxng
docker run -d -p 8080:8080 searxng/searxng

# Configure in .env
SEARXNG_URL=http://localhost:8080
```

#### Integration Example
```python
import requests

def searxng_search(query: str, max_results: int = 5):
    """Search using self-hosted SearXNG."""
    response = requests.get(
        f"{SEARXNG_URL}/search",
        params={
            "q": query,
            "format": "json",
            "pageno": 1
        }
    )

    results = response.json()["results"][:max_results]
    return results
```

**Pros:**
- ✅ Completely free and open source
- ✅ Self-hosted (full control)
- ✅ Privacy-focused (no tracking)
- ✅ Aggregates multiple search engines
- ✅ JSON API available

**Cons:**
- ❌ Requires server infrastructure
- ❌ No built-in content extraction (you need to scrape)
- ❌ Less reliable than commercial APIs
- ❌ No relevance scoring
- ❌ Rate limiting from upstream sources

**Cost:** Free (but server hosting ~$5-20/month)

---

### Option 2: **DuckDuckGo Instant Answer API** (Free, Limited)

**What it is:** DuckDuckGo's free API for basic search results.

#### Integration Example
```python
from duckduckgo_search import DDGS

def ddg_search(query: str, max_results: int = 5):
    """Search using DuckDuckGo (no API key needed)."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results
```

#### Setup
```bash
pip install duckduckgo-search
```

**Pros:**
- ✅ Completely free (no API key)
- ✅ No rate limiting (reasonable use)
- ✅ Simple Python library
- ✅ Privacy-focused

**Cons:**
- ❌ Results quality lower than Google
- ❌ No official API (uses web scraping internally)
- ❌ Can break if DDG changes HTML
- ❌ No content extraction
- ❌ No relevance scoring

**Cost:** Free

---

### Option 3: **Jina AI Reader** (API for Web Content Extraction)

**What it is:** Free API that converts any URL into LLM-friendly text/markdown.

#### How It Works
```
Your Agent → Google Search (manual) → URLs → Jina Reader → Clean Content
```

#### Integration Example
```python
import requests

def jina_read(url: str):
    """Convert URL to LLM-friendly content."""
    response = requests.get(f"https://r.jina.ai/{url}")
    return response.text  # Returns clean markdown
```

**Pros:**
- ✅ Free tier (1000 requests/month)
- ✅ Excellent content extraction
- ✅ Returns markdown optimized for LLMs
- ✅ No scraping/parsing needed

**Cons:**
- ❌ Not a search engine (only content extraction)
- ❌ Need to combine with search solution
- ❌ Rate limited on free tier

**Cost:** Free (1K/month), $20/month (100K requests)

**Recommended Combo:**
```python
# Use DuckDuckGo for search + Jina for content
results = ddg_search("Livongo Health")
for result in results:
    content = jina_read(result["url"])
    # Now you have clean content!
```

---

## Building Your Own Search Solution

### Approach 1: **Google Custom Search API + BeautifulSoup**

#### Architecture
```
Agent → Google Custom Search API → URLs
     → BeautifulSoup Scraper → Clean Content
     → Return to Agent
```

#### Implementation
```python
import requests
from bs4 import BeautifulSoup

class CustomSearchTool:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    def search(self, query: str, max_results: int = 5):
        """Search using Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": max_results
        }

        response = requests.get(url, params=params)
        results = response.json().get("items", [])

        # Extract and clean content
        cleaned_results = []
        for item in results:
            content = self._scrape_and_clean(item["link"])
            cleaned_results.append({
                "title": item["title"],
                "url": item["link"],
                "snippet": item["snippet"],
                "content": content
            })

        return cleaned_results

    def _scrape_and_clean(self, url: str) -> str:
        """Scrape and clean content from URL."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script, style, nav, footer
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)[:5000]  # Limit length

        except Exception as e:
            return f"Failed to scrape: {e}"
```

#### Setup
```bash
# 1. Get Google Custom Search API key
# https://developers.google.com/custom-search/v1/overview

# 2. Create Custom Search Engine
# https://programmablesearchengine.google.com/

# 3. Install dependencies
pip install beautifulsoup4 requests lxml

# 4. Configure .env
GOOGLE_API_KEY=your-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

**Pros:**
- ✅ Real Google search results (best quality)
- ✅ You control scraping/cleaning logic
- ✅ No dependency on Tavily
- ✅ Flexible customization

**Cons:**
- ❌ Google API costs money (100 free searches/day, then $5/1000)
- ❌ You maintain scraping code
- ❌ Scraping can break when sites change
- ❌ Need to handle rate limiting, errors, timeouts
- ❌ No built-in relevance scoring

**Cost:** $5 per 1,000 searches after free tier

---

### Approach 2: **Bing Search API + Playwright**

Similar to Google but using Microsoft Bing:

```python
import requests
from playwright.sync_api import sync_playwright

class BingSearchTool:
    def __init__(self):
        self.api_key = os.getenv("BING_SEARCH_API_KEY")

    def search(self, query: str, max_results: int = 5):
        """Search using Bing Search API."""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "count": max_results}

        response = requests.get(url, headers=headers, params=params)
        results = response.json().get("webPages", {}).get("value", [])

        # Use Playwright for JavaScript-heavy pages
        cleaned_results = []
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            for item in results:
                content = self._scrape_with_playwright(page, item["url"])
                cleaned_results.append({
                    "title": item["name"],
                    "url": item["url"],
                    "snippet": item["snippet"],
                    "content": content
                })

            browser.close()

        return cleaned_results

    def _scrape_with_playwright(self, page, url: str) -> str:
        """Scrape JavaScript-rendered content."""
        try:
            page.goto(url, timeout=10000)
            page.wait_for_load_state("networkidle")
            return page.inner_text("body")[:5000]
        except:
            return ""
```

**Setup:**
```bash
# 1. Get Bing Search API key
# https://www.microsoft.com/en-us/bing/apis/bing-web-search-api

# 2. Install dependencies
pip install playwright
playwright install chromium

# 3. Configure .env
BING_SEARCH_API_KEY=your-api-key
```

**Pros:**
- ✅ Good search quality
- ✅ Free tier available (3000 transactions/month)
- ✅ Playwright handles JavaScript sites
- ✅ Official Microsoft API

**Cons:**
- ❌ Playwright is heavy (requires browser)
- ❌ Slower than simple HTTP requests
- ❌ More complex to maintain

**Cost:** Free (3K/month), then $7 per 1,000 searches

---

### Approach 3: **Fully Custom with Selenium/Scrapy**

**Don't do this unless absolutely necessary!**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class DirectGoogleScraper:
    """Scrape Google directly (against TOS!)."""

    def search(self, query: str):
        driver = webdriver.Chrome()
        driver.get(f"https://www.google.com/search?q={query}")

        # This will get you IP blocked quickly!
        results = driver.find_elements(By.CLASS_NAME, "g")
        # ... extract results ...

        driver.quit()
```

**Why NOT to do this:**
- ❌ Violates Google Terms of Service
- ❌ IP will be blocked quickly
- ❌ CAPTCHAs make it impractical
- ❌ Legal risks
- ❌ Unreliable and fragile

---

## Cost Comparison

### Monthly Cost Estimate (1,000 searches/month)

| Solution | Setup Cost | Monthly Cost | Maintenance |
|----------|-----------|--------------|-------------|
| **Tavily** | $0 | $50-200 | None |
| **Google Custom Search** | $0 | $45 | Low |
| **Bing Search API** | $0 | Free-$7 | Low |
| **SearXNG (self-hosted)** | $50 | $10 (server) | High |
| **DuckDuckGo (free)** | $0 | $0 | Medium |
| **DuckDuckGo + Jina Reader** | $0 | $0-20 | Medium |
| **Custom (Google + Scraping)** | 20 hrs dev | $45 + server | Very High |
| **Direct scraping** | 40 hrs dev | $0 (until blocked) | Impossible |

### Annual Cost Comparison (12,000 searches/year)

```
Tavily:              $600 - $2,400
Google Custom:       $540
Bing:                $0 - $84
SearXNG:             $120 (server) + dev time
DuckDuckGo:          $0
Custom Solution:     $540 + $5K dev time
```

---

## Recommendation Matrix

### Choose **Tavily** if:
- ✅ You want the easiest solution
- ✅ You need AI-optimized content extraction
- ✅ You value reliability over cost
- ✅ You're doing production-grade research
- ✅ You want to launch quickly

**Setup time:** 5 minutes
**Code:** 3 lines
**Reliability:** 99.9%

---

### Choose **DuckDuckGo + Jina Reader** if:
- ✅ You want free/low-cost solution
- ✅ You're okay with slightly lower search quality
- ✅ You need privacy-focused search
- ✅ You're prototyping or early-stage

**Setup time:** 30 minutes
**Code:** 50 lines
**Reliability:** 95%

---

### Choose **SearXNG (self-hosted)** if:
- ✅ You want complete control
- ✅ You have infrastructure team
- ✅ Privacy is critical
- ✅ You need to customize search behavior
- ✅ You're doing high-volume searches (>10K/month)

**Setup time:** 4-8 hours
**Code:** 100 lines
**Reliability:** 90% (depends on your infra)

---

### Choose **Google Custom Search** if:
- ✅ You need best search quality
- ✅ You're okay paying per search
- ✅ You want official API support
- ✅ You need reliable, fast results

**Setup time:** 2 hours
**Code:** 150 lines (with scraping)
**Reliability:** 99%

---

### Choose **Custom Solution** if:
- ✅ You have very specific requirements
- ✅ You have experienced engineers
- ✅ You need deep customization
- ✅ You're doing 100K+ searches/month (cost optimization)

**Setup time:** 2-4 weeks
**Code:** 1000+ lines
**Reliability:** 85-95% (depends on implementation)

---

## Practical Implementation Guide

### Quick Start: DuckDuckGo + Jina Reader (Free)

Replace your `google_search_tool.py`:

```python
"""Google Search Tool - DuckDuckGo + Jina Reader Implementation."""

from typing import List, Dict, Any
import requests
from duckduckgo_search import DDGS
from agno.tools import Toolkit
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class GoogleSearchTool(Toolkit):
    """Free search using DuckDuckGo + Jina Reader for content extraction."""

    def __init__(self):
        super().__init__(name="google_search")
        self.jina_enabled = True  # Free tier: 1000 requests/month

    def google_search(
        self,
        query: str,
        max_results: int = 5,
        include_raw_content: bool = False
    ) -> List[Dict[str, Any]]:
        """Perform web search using DuckDuckGo."""
        try:
            logger.info(f"Searching DDG: '{query}' (max_results={max_results})")

            # Search with DuckDuckGo
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            # Optionally enhance with Jina Reader for full content
            enhanced_results = []
            for result in results:
                item = {
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "score": 0.8  # DDG doesn't provide scores
                }

                # Use Jina Reader for full content if needed
                if include_raw_content and self.jina_enabled:
                    try:
                        content = self._jina_read(result["href"])
                        item["content"] = content
                    except:
                        item["content"] = ""
                else:
                    item["content"] = ""

                enhanced_results.append(item)

            logger.info(f"Found {len(enhanced_results)} results")
            return enhanced_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _jina_read(self, url: str) -> str:
        """Extract clean content using Jina Reader API."""
        try:
            response = requests.get(
                f"https://r.jina.ai/{url}",
                timeout=10,
                headers={"X-Return-Format": "markdown"}
            )
            return response.text[:10000]  # Limit to 10K chars
        except Exception as e:
            logger.error(f"Jina Reader failed for {url}: {e}")
            return ""

    def register_tools(self) -> List[Any]:
        return [self.google_search]


def create_google_search_tool() -> GoogleSearchTool:
    return GoogleSearchTool()
```

**Installation:**
```bash
pip install duckduckgo-search requests
```

**No API keys needed!**

---

### Production Setup: Tavily (Easiest)

Keep your existing code, just add API key:

```bash
# 1. Sign up at https://tavily.com
# 2. Get API key (1000 free searches/month)
# 3. Install library
pip install tavily-python

# 4. Add to .env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxx
```

**That's it!** Your existing code will automatically use real search.

---

## Decision Tree

```
Do you need web search at all?
│
├─ No → Use mock mode (current setup)
│
└─ Yes → What's your budget?
    │
    ├─ $0/month → DuckDuckGo + Jina Reader
    │
    ├─ $0-50/month → Bing Search API (3K free)
    │
    ├─ $50-200/month → Tavily (recommended for production)
    │
    ├─ Custom needs → SearXNG self-hosted
    │
    └─ Need best quality → Google Custom Search ($5/1K)
```

---

## Summary: The Real Answer

### For Your Triton Project

**Recommendation: Start with DuckDuckGo (Free), upgrade to Tavily later**

#### Phase 1: Development/Testing (Now)
- ✅ Keep mock mode
- ✅ Test agent logic and validation
- ✅ Cost: $0

#### Phase 2: Real Research Testing (Next)
- ✅ Add DuckDuckGo + Jina Reader
- ✅ Test with real companies
- ✅ Validate research quality
- ✅ Cost: $0

#### Phase 3: Production (When Ready)
- ✅ Upgrade to Tavily
- ✅ Get AI-optimized results
- ✅ Better reliability and quality
- ✅ Cost: $50-200/month

### Quick Answer

**Do you need Tavily?**
- No, but it's the easiest solution for production

**Best free alternative?**
- DuckDuckGo + Jina Reader (zero cost, good quality)

**Best open source?**
- SearXNG (self-hosted, full control)

**Can you build your own?**
- Yes, but costs $5K+ in dev time and $50/month in API costs

**What I recommend:**
1. **Now:** Keep mock mode for testing
2. **Next week:** Add DuckDuckGo (free) for real testing
3. **Production:** Upgrade to Tavily ($50/month) when you need reliability

---

## Implementation Timeline

```
Week 1: Mock Mode (Current)
  → Test agent logic
  → Validate JSON schema
  → Test retry mechanism

Week 2: DuckDuckGo Implementation
  → Replace google_search_tool.py
  → Test with real searches
  → Validate research quality

Week 4: Evaluate Results
  → Is DDG quality sufficient? → Keep it (save $50/month)
  → Need better quality? → Upgrade to Tavily

Production: Tavily (if needed)
  → Add API key
  → No code changes needed
  → Better results, reliability
```

**Total investment to try real search: 2 hours, $0**

---

## Next Steps

1. **Test mock mode thoroughly** (you just did this!)
2. **Implement DuckDuckGo** (2 hours, free)
3. **Compare results** with LLM training data
4. **Decide** if you need Tavily's premium features

You don't need Tavily right now, but it's nice to have when quality matters!
