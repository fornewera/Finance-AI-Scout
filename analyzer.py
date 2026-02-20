import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# Define the Pydantic schema for structured output
class NewsItem(BaseModel):
    title: str = Field(description="新聞標題 (Title)")
    date_time: str = Field(description="新聞日期/時間 (Date/Time)")
    source: str = Field(description="新聞來源媒體 (Source)")
    summary: str = Field(description="新聞內容摘要 (Summary)：客觀的事件陳述")
    social_sentiment: str = Field(description="社群評論摘要 (Social Sentiment)：X (Twitter)、Reddit 等社群對此事件的網民討論與情緒反應")
    url: str = Field(description="新聞連結 (URL)")

class CategoryReport(BaseModel):
    items: list[NewsItem] = Field(description="List of exactly 10 most critical news items")

class DailyReport(BaseModel):
    financial_news: CategoryReport
    ai_news: CategoryReport

def get_social_sentiment(article_title: str) -> str:
    """
    Fetch social media sentiments for a specific news title using Tavily.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "無法獲取 API Key"
        
    client = TavilyClient(api_key=api_key)
    query = f"Reddit AND Twitter (X) AND Hacker News reaction and comments to: {article_title}"
    sentiment_sources = ["reddit.com", "twitter.com", "x.com", "news.ycombinator.com"]
    
    try:
        # Search specifically in social media domains
        response = client.search(
            query=query,
            search_depth="advanced",
            include_domains=sentiment_sources,
            max_results=3
        )
        results = response.get('results', [])
        if not results:
            return "目前無顯著社群討論"
            
        # Combine the context into a single string for Gemini to digest
        context = "\n".join([f"- {r['content']}" for r in results])
        return context
    except Exception as e:
        print(f"Error fetching sentiment for {article_title}: {e}")
        return "無法取得社群討論"

def analyze_and_format_news(finance_raw: list, ai_raw: list) -> dict:
    """
    Uses Gemini 3.1 Pro to select the top 10 news, summarize them, and fetch social sentiments.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found!")
        return {}
        
    client = genai.Client(api_key=api_key)
    
    # We will process each category separately to maintain manageable context and schema
    reports = {}
    
    print("Analyzing Financial News with Gemini...")
    finance_report = process_category(client, "全球重要財經新聞", finance_raw)
    
    print("Analyzing AI News with Gemini...")
    ai_report = process_category(client, "全球重要AI相關新聞", ai_raw)
    
    return {
        "global_financial_news": finance_report,
        "global_ai_news": ai_report
    }

def process_category(client, category_name: str, raw_items: list) -> list:
    # First, let's ask Gemini to pick the top 10 and format the basic info (without sentiment)
    # We pass the raw Tavily results to Gemini
    context_str = json.dumps(raw_items, indent=2, ensure_ascii=False)
    
    prompt = f"""
    你是一位華爾街頂級的分析師。請從以下提供的 Tavily 搜尋結果中，挑選出最重要、最具全球市場/產業影響力的 10 則【{category_name}】。
    
    篩選標準：
    - 財經新聞：只關注宏觀經濟、大盤、重大地緣政治、重量級巨頭動態。排除農場預測、中小型股。
    - AI 新聞：關注模型突破、算力基礎建設、重大併購、實質應用落地。排除小工具更新、農場教學文。
    - 必須是過去 24 小時內發生的時效性事件。
    - 嚴格遵守提供的 JSON Schema 輸出。對於 social_sentiment 欄位，請先填入「待補」。
    
    原始新聞資料：
    {context_str}
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-pro-preview',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CategoryReport,
            temperature=0.2, # Low temp for factual picking
        ),
    )
    
    try:
        report_data = json.loads(response.text)
        items = report_data.get("items", [])
        
        # Now we enhance each item with social sentiment
        for item in items:
            title = item.get("title", "")
            print(f"Fetching sentiment for: {title}")
            raw_sentiment = get_social_sentiment(title)
            
            # Use Gemini flash (cheaper/faster) to summarize the raw sentiment
            sentiment_summary = summarize_sentiment(client, title, raw_sentiment)
            item["social_sentiment"] = sentiment_summary
            
        return items
    except Exception as e:
        print(f"Error parsing Gemini response or fetching sentiment: {e}")
        return []

def summarize_sentiment(client, title: str, raw_sentiment: str) -> str:
    if raw_sentiment in ["目前無顯著社群討論", "無法取得社群討論", "無法獲取 API Key"]:
         return raw_sentiment
         
    prompt = f"""
    新聞事件：「{title}」
    以下是從 X (Twitter)、Reddit、Hacker News 爬取到的原始網民討論片段：
    {raw_sentiment}
    
    請用一句話 (繁體中文，約 30 字內) 總結社群的整體情緒反應與主要爭議點 (例如看多、看空、或某個特定擔憂)。
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview', # Use flash for quick sentiment summary
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error in sentiment summary: {e}")
        return "社群情緒總結失敗"

if __name__ == "__main__":
    # For testing logic
    pass
