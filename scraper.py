import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# RSS Feeds or Main Pages for target sources
# Note: Bloomberg and FT are hard to scrape due to paywalls/anti-bot. 
# We use RSS where available or fallback to a known feed URL.
SOURCES = {
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", 
    "CNN": "http://rss.cnn.com/rss/money_latest.rss",
    "Wall Street Journal": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
    "Barron's": "https://www.barrons.com/feed/rss",  # Generic Barron's feed
    "Financial Times": "https://www.ft.com/?format=rss", # Often just titles
    "Bloomberg": "https://feeds.bloomberg.com/business/news.xml" # Unofficial/Often changes or redirects. 
    # Alternative: Use query params matching source for cleaner results if parsing main page.
}

def fetch_headlines():
    """
    Fetches headlines from specific RSS feeds or pages.
    Returns a list of news items.
    """
    all_articles = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Fetching news from RSS feeds...")

    for source, url in SOURCES.items():
        try:
            # Try parsing as RSS first
            feed = feedparser.parse(url)
            
            if feed.entries:
                print(f"Fetched {len(feed.entries)} items from {source}")
                for entry in feed.entries[:10]: # Top 10
                    # Standardize fields
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    summary = entry.get('summary', '') or entry.get('description', '')
                    pub_date = entry.get('published', '') or entry.get('updated', str(datetime.now()))
                    
                    # Basic cleaning
                    soup = BeautifulSoup(summary, "html.parser")
                    clean_summary = soup.get_text()[:200]
                    
                    all_articles.append({
                        "source": source,
                        "title": title,
                        "url": link,
                        "publishedAt": pub_date,
                        "description": clean_summary
                    })
            else:
                # Fallback: simple requests + BS4 if RSS fails (Not implemented for all due to complexity, ignoring for now)
                print(f"No RSS entries found for {source} at {url}")
                
        except Exception as e:
            print(f"Error fetching {source}: {e}")

    print(f"Total articles fetched: {len(all_articles)}")
    return all_articles

if __name__ == "__main__":
    headlines = fetch_headlines()
    for h in headlines:
        print(f"[{h['source']}] {h['title']}")
