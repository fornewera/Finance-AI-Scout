import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# We define the whitelisted sources for priority search
FINANCE_SOURCES = [
    "bloomberg.com", "reuters.com", "wsj.com", 
    "ft.com", "cnbc.com", "barrons.com"
]

AI_SOURCES = [
    "theverge.com", "techcrunch.com", "wired.com", "theinformation.com", 
    "technologyreview.com", "openai.com", "blog.google", "anthropic.com"
]

def fetch_category_news(category: str, query: str, include_domains: list) -> list:
    """
    Fetch news from Tavily with a strict 24-hour time range and advanced depth.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("TAVILY_API_KEY not found in environment!")
        return []
        
    client = TavilyClient(api_key=api_key)
    
    print(f"Fetching {category} news using Tavily...")
    try:
        # Time range 'd' strictly searches for the last 24 hours (if the API supports "day" or "d")
        # According to Tavily docs, time_range="day", "week", "month", "year", "d"
        response = client.search(
            query=query,
            search_depth="advanced",
            topic="news",
            days=1, # Also possible based on SDK version
            include_domains=include_domains,
            max_results=15  # Fetch slightly more, so AI can filter down to the top 10
        )
        
        results = response.get('results', [])
        print(f"Fetched {len(results)} items for {category}.")
        return results
    except Exception as e:
        print(f"Error fetching {category}: {e}")
        return []

def fetch_all_relevant_news():
    """
    Fetch both financial and AI news, returning a dictionary of the raw search results.
    """
    # Use a highly descriptive prompt for the search engine to understand our needs.
    finance_query = "latest major global macroeconomic news, central bank policies like fed rates, major stock market index movements S&P 500, geopolitical global impact, or top tier non-AI corporate earnings and shifts."
    finance_news = fetch_category_news(
        category="Global Financial News",
        query=finance_query,
        include_domains=FINANCE_SOURCES
    )
    
    ai_query = "latest breakthrough AI models releases, AI infrastructure NVIDIA AMD, major AI startup investments, tech giants AI mergers, high impact AI applications or major AI regulation news."
    ai_news = fetch_category_news(
        category="Global AI News",
        query=ai_query,
        include_domains=AI_SOURCES
    )
    
    return {
        "finance": finance_news,
        "ai": ai_news
    }

if __name__ == "__main__":
    news = fetch_all_relevant_news()
    for cat, items in news.items():
        print(f"\n--- {cat.upper()} ({len(items)}) ---")
        for item in items[:2]:
            print(f"- {item.get('title')} ({item.get('url')})")
