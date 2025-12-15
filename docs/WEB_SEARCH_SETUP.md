# Web Search Setup Guide

Quick guide to enable real web search for your WebSearchAgent.

---

## TL;DR - Quick Setup

### Option 1: Free Search (DuckDuckGo) - Recommended for Testing

```bash
# Install DuckDuckGo search (no API key needed)
pip install duckduckgo-search

# That's it! No configuration needed.
```

### Option 2: Premium Search (Tavily) - Recommended for Production

```bash
# 1. Sign up at https://tavily.com
# 2. Get API key (1000 free searches/month)
# 3. Install package
pip install tavily-python

# 4. Add to .env
echo "TAVILY_API_KEY=tvly-your-key-here" >> .env
```

---

## How It Works

Your `google_search_tool.py` automatically uses the **best available provider**:

```
Priority:
1. Tavily (if TAVILY_API_KEY is set) → Premium quality
2. DuckDuckGo (if installed) → Free, good quality
3. Mock mode (fallback) → Fake data for testing
```

**No code changes needed!** The tool automatically detects what's available.

---

## Current Status Check

Run this to see what search provider you're using:

```bash
source venv/bin/activate
python -c "
from tools.google_search_tool import create_google_search_tool
tool = create_google_search_tool()
print(f'Search provider: {tool.search_provider}')
"
```

**Output will show:**
- `tavily` - Using premium Tavily API ✅
- `duckduckgo` - Using free DuckDuckGo ✅
- `mock` - Using fake data (install one of the above!)

---

## Detailed Setup Instructions

### Option 1: DuckDuckGo (Free)

#### Installation

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install DuckDuckGo search
pip install duckduckgo-search

# 3. Test it works
python -c "from duckduckgo_search import DDGS; print('✅ DuckDuckGo ready!')"
```

#### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Completely free | ❌ Lower quality than Tavily |
| ✅ No API key needed | ❌ No relevance scoring |
| ✅ No rate limits | ❌ Can break if DDG changes |
| ✅ Privacy-focused | ❌ No official API support |

#### Good For:
- Development and testing
- Budget-conscious projects
- Privacy-focused applications
- Prototyping

---

### Option 2: Tavily (Premium)

#### Installation

```bash
# 1. Sign up at https://tavily.com
# 2. Get API key from dashboard
# 3. Activate virtual environment
source venv/bin/activate

# 4. Install Tavily
pip install tavily-python

# 5. Add API key to .env
echo "TAVILY_API_KEY=tvly-xxxxxxxxxxxxx" >> .env

# 6. Test it works
python -c "
import os
from tavily import TavilyClient
client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
print('✅ Tavily ready!')
"
```

#### Pricing

| Tier | Monthly Cost | Searches/Month | Best For |
|------|--------------|----------------|----------|
| **Free** | $0 | 1,000 | Testing |
| **Starter** | $50 | 10,000 | Small projects |
| **Pro** | $200 | 50,000 | Production |

#### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Built for AI agents | ❌ Paid service |
| ✅ Clean, LLM-optimized content | ❌ Requires API key |
| ✅ Relevance scoring | ❌ Monthly cost |
| ✅ High reliability | |
| ✅ Advanced search modes | |

#### Good For:
- Production applications
- High-quality research requirements
- When accuracy matters
- Commercial projects

---

## Testing Your Setup

### Quick Test

```bash
source venv/bin/activate
python test_research_agents.py
```

**What to look for in logs:**

✅ **DuckDuckGo mode:**
```
✅ DuckDuckGo Search initialized (free mode)
Searching with duckduckgo: 'Livongo Health overview' (max_results=5)
DuckDuckGo found 5 results for: 'Livongo Health overview'
```

✅ **Tavily mode:**
```
✅ Tavily Search API initialized (premium mode)
Searching with tavily: 'Livongo Health overview' (max_results=5)
Tavily found 5 results for: 'Livongo Health overview'
```

❌ **Mock mode (no real search):**
```
No search provider available. Using mock mode.
Using mock search results for query: 'Livongo Health overview'
```

---

### Compare Search Results

Test both providers side-by-side:

```python
from tools.google_search_tool import create_google_search_tool

tool = create_google_search_tool()
results = tool.google_search("Livongo Health diabetes", max_results=3)

for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['title']}")
    print(f"   URL: {result['url']}")
    print(f"   Snippet: {result['snippet'][:100]}...")
    print(f"   Source: {result['source']}")
    print(f"   Score: {result['score']}")
```

---

## Advanced Configuration

### Bonus: Full Content Extraction with Jina Reader

When using DuckDuckGo, you can optionally fetch full page content using Jina AI Reader (free):

```python
# Fetch search results WITH full page content
results = tool.google_search(
    "Livongo ROI case study",
    max_results=5,
    include_raw_content=True  # ← Fetches full content via Jina Reader
)

# Now each result has clean markdown content
for result in results:
    print(f"Title: {result['title']}")
    print(f"Full content: {result['content'][:500]}...")  # First 500 chars
```

**Jina Reader:**
- Free tier: 1,000 requests/month
- Converts any URL to clean markdown
- Perfect for LLM consumption
- No API key needed for basic use

---

## Fallback Behavior

The tool has **smart fallback logic**:

```
┌─────────────────────────────────┐
│ Try Tavily (if API key set)    │
└─────────────────────────────────┘
            ↓ (fail)
┌─────────────────────────────────┐
│ Try DuckDuckGo (if installed)  │
└─────────────────────────────────┘
            ↓ (fail)
┌─────────────────────────────────┐
│ Use Mock Mode (always works)   │
└─────────────────────────────────┘
```

**Even Tavily can fall back to DuckDuckGo** if:
- API quota exceeded
- Network error
- Tavily service down

This ensures your agent **always works**, even if premium services fail!

---

## Troubleshooting

### Issue: "No search provider available. Using mock mode."

**Solution:**
```bash
# Install DuckDuckGo for free search
pip install duckduckgo-search

# OR install Tavily for premium search
pip install tavily-python
export TAVILY_API_KEY=tvly-your-key
```

---

### Issue: "duckduckgo-search not installed"

**Solution:**
```bash
source venv/bin/activate
pip install duckduckgo-search
```

---

### Issue: "TAVILY_API_KEY is set but tavily-python not installed"

**Solution:**
```bash
source venv/bin/activate
pip install tavily-python
```

---

### Issue: DuckDuckGo returns no results

**Cause:** DuckDuckGo may rate-limit or block requests if you search too frequently.

**Solutions:**
1. Add delays between searches
2. Use a VPN
3. Switch to Tavily (more reliable)
4. Use mock mode for testing

---

### Issue: "Jina Reader failed for URL"

**Cause:** Some websites block Jina Reader or the URL is invalid.

**Solution:** This is expected and handled gracefully. The result will have an empty `content` field but still include `snippet`.

---

## Cost Optimization Tips

### For Development (Free)
```bash
# Use DuckDuckGo - zero cost
pip install duckduckgo-search
```

### For Testing (Low Cost)
```bash
# Use Tavily free tier - 1000 searches/month
pip install tavily-python
# Sign up at tavily.com for free key
```

### For Production (Best Quality)
```bash
# Use Tavily paid tier
# $50/month for 10K searches
# OR
# $200/month for 50K searches
```

### Hybrid Approach (Smart)
```bash
# Install both!
pip install duckduckgo-search tavily-python

# Use Tavily for important production searches
# Falls back to DuckDuckGo if quota exceeded
# Zero downtime!
```

---

## Recommended Path

### Week 1: Development
```bash
# Use mock mode (current state)
# No installation needed
# Focus on agent logic
```

### Week 2: Real Search Testing
```bash
# Install DuckDuckGo
pip install duckduckgo-search

# Test with real searches
# Validate research quality
# Cost: $0
```

### Week 3: Evaluation
```bash
# Is DuckDuckGo good enough?
# Yes → Keep it (save $50/month)
# No → Get Tavily free trial
```

### Week 4+: Production
```bash
# If quality matters → Tavily
# If budget matters → DuckDuckGo
# If reliability critical → Tavily with DDG fallback
```

---

## Summary

| Setup | Command | Cost | Quality | Speed |
|-------|---------|------|---------|-------|
| **Mock** | (default) | Free | Fake | Instant |
| **DuckDuckGo** | `pip install duckduckgo-search` | Free | Good | Fast |
| **Tavily** | `pip install tavily-python` + API key | $0-200/mo | Excellent | Very Fast |
| **Both** | Install both packages | $0-200/mo | Excellent | Very Fast |

---

## Next Steps

1. **Choose your provider** (DuckDuckGo or Tavily)
2. **Install package** (see commands above)
3. **Test it** (`python test_research_agents.py`)
4. **Monitor logs** to confirm provider is active
5. **Compare results** against mock mode

Your agent will automatically use the best available provider! 🎯
