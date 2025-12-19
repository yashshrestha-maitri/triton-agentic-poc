# Web Search Quick Start

**TL;DR:** Your search tool now automatically uses the best available provider!

---

## Current Status

Run this to check what you're using:

```bash
source venv/bin/activate
python -c "
from tools.google_search_tool import create_google_search_tool
tool = create_google_search_tool()
print(f'Search provider: {tool.search_provider}')
"
```

**Output will show:**
- `tavily` → Premium Tavily API (if TAVILY_API_KEY set)
- `duckduckgo` → Free DuckDuckGo (if ddgs installed)
- `mock` → Fake data (no real search)

---

## Quick Setup Options

### Option 1: Free Search (DuckDuckGo) ✅ RECOMMENDED

```bash
pip install ddgs
```

That's it! No API key needed. Already installed if you ran `pip install -r requirements.txt`.

### Option 2: Premium Search (Tavily)

```bash
# 1. Sign up at https://tavily.com (1000 free searches/month)
# 2. Get API key
# 3. Install and configure:
pip install tavily-python
echo "TAVILY_API_KEY=tvly-your-key" >> .env
```

---

## How It Works

Your tool automatically selects providers in this order:

```
1. Tavily (if TAVILY_API_KEY set) → Best quality
   ↓ (not available)
2. DuckDuckGo (if ddgs installed) → Good quality, free
   ↓ (not available)
3. Mock mode → Fake data for testing
```

**No code changes needed!** The tool auto-detects and uses the best option.

---

## Test Your Setup

```bash
source venv/bin/activate
python test_research_agents.py
```

Look for this in the logs:

✅ **With DuckDuckGo:**
```
✅ DuckDuckGo Search initialized (free mode)
Searching with duckduckgo: 'Livongo Health overview'
DuckDuckGo found 5 results for: 'Livongo Health overview'
```

✅ **With Tavily:**
```
✅ Tavily Search API initialized (premium mode)
Searching with tavily: 'Livongo Health overview'
Tavily found 5 results for: 'Livongo Health overview'
```

---

## Quick Comparison

| Provider | Setup | Cost | Quality |
|----------|-------|------|---------|
| **Mock** | None | Free | Fake |
| **DuckDuckGo** | `pip install ddgs` | Free | Good |
| **Tavily** | API key + `pip install tavily-python` | $0-200/mo | Excellent |

---

## Next Steps

1. **For testing:** Use DuckDuckGo (already installed!)
2. **For production:** Consider Tavily when quality matters
3. **For development:** Mock mode is fine

See [WEB_SEARCH_SETUP.md](./WEB_SEARCH_SETUP.md) for detailed instructions.
