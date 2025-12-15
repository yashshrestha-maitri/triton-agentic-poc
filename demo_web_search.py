#!/usr/bin/env python3
"""
Demo script to test web search functionality.

Shows how the tool automatically selects the best provider:
1. Tavily (if API key set)
2. DuckDuckGo (if installed)
3. Mock mode (fallback)
"""

from tools.google_search_tool import create_google_search_tool


def demo_search():
    """Demonstrate web search with automatic provider selection."""

    print("="*70)
    print(" "*20 + "WEB SEARCH DEMO")
    print("="*70)

    # Create tool (auto-selects best provider)
    print("\n1. Creating search tool...")
    tool = create_google_search_tool()

    print(f"\n✅ Active provider: {tool.search_provider.upper()}")
    print(f"   API key configured: {bool(tool.api_key)}")

    # Test search
    print("\n2. Performing test search...")
    query = "OpenAI GPT-4 artificial intelligence"
    print(f"   Query: '{query}'")

    results = tool.google_search(query, max_results=3)

    print(f"\n3. Results ({len(results)} found):")
    print("-"*70)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'][:100]}...")
        print(f"   Source: {result['source']}")
        print(f"   Score: {result['score']}")

    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70)

    # Show provider info
    print("\nProvider Information:")
    if tool.search_provider == 'tavily':
        print("  🌟 Using Tavily API (premium)")
        print("     - Highest quality AI-optimized results")
        print("     - Cost: Based on usage")
    elif tool.search_provider == 'duckduckgo':
        print("  🦆 Using DuckDuckGo (free)")
        print("     - Good quality results")
        print("     - Cost: $0")
        print("     - Upgrade to Tavily for better quality")
    else:
        print("  🎭 Using Mock Mode (testing)")
        print("     - Fake results for development")
        print("     - Cost: $0")
        print("     - Install ddgs for real search:")
        print("       pip install ddgs")

    print("\n" + "="*70)


if __name__ == "__main__":
    demo_search()
