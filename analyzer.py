import random
from datetime import datetime
from deep_translator import GoogleTranslator

def translate_to_tc(text):
    """
    Translates text to Traditional Chinese using Google Translator.
    """
    try:
        # 'zh-TW' is standard for Traditional Chinese
        return GoogleTranslator(source='auto', target='zh-TW').translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

def calculate_score(text):
    """
     heuristic scoring based on keywords.
    """
    text = text.lower()
    scores = {
        "policy": 0,
        "systemic": 0,
        "ai": 0,
        "social": 0
    }
    
    # Keyword Lists (Expanded for better coverage)
    keywords = {
        "policy": ["fed", "rate", "tax", "biden", "trump", "powell", "sec", "regulation", "law", "sanction", "trade", "china", "congress", "senate", "policy"],
        "systemic": ["crash", "crisis", "debt", "bankrupt", "recession", "inflation", "collapse", "risk", "bubble", "volatility", "liquidity", "default", "market"],
        "ai": ["ai", "artificial intelligence", "gpt", "gemini", "nvidia", "sam altman", "open-source", "neural", "robot", "compute", "algorithm", "llm", "tech"],
        "social": ["viral", "trend", "breaking", "community", "reddit", "twitter", "rumor", "leak", "controversy", "scandal", "opinion"]
    }
    
    # Calculate Component Scores
    for word in keywords["policy"]:
        if word in text: scores["policy"] += 15
    scores["policy"] = min(scores["policy"], 30)
    
    for word in keywords["systemic"]:
        if word in text: scores["systemic"] += 12
    scores["systemic"] = min(scores["systemic"], 25)
    
    for word in keywords["ai"]:
        if word in text: scores["ai"] += 12
    scores["ai"] = min(scores["ai"], 25)

    base_social = random.randint(5, 15)
    for word in keywords["social"]:
        if word in text: base_social += 5
    scores["social"] = min(base_social, 20)
    
    total_score = scores["policy"] + scores["systemic"] + scores["ai"] + scores["social"]
    return total_score, scores

def analyze_news(news_items):
    """
    Analyzes news items using a keyword-based heuristic model.
    Translates relevant fields to Traditional Chinese.
    """
    if not news_items:
        return []

    print(f"Analyzing {len(news_items)} items with Heuristic Scorer & Translation...")
    
    analyzed_items = []
    
    for item in news_items:
        # Combine title and description for analysis
        full_text = f"{item['title']} {item.get('description', '')}"
        score, components = calculate_score(full_text)
        
        # Generate Social Comment Summary (Heuristic)
        social_comment = "社群討論熱度高。" if components['social'] > 15 else "社群關注度中等。"
        if components['ai'] > 10: social_comment += " 科技圈與投資人高度聚焦 AI 發展。"
        if components['policy'] > 20: social_comment += " 市場密切關注政策變動風險。"
        if components['systemic'] > 15: social_comment += " 投資人擔憂潛在金融風險。"
        if score > 70: social_comment += " 此議題極具影響力，建議密切追蹤。"
        
        # Translate Title and Summary
        # Note: Summary uses 'description' from RSS
        tc_title = translate_to_tc(item['title'])
        tc_summary = translate_to_tc(item.get('description', item['title'])) # Fallback to title if no desc

        item['score'] = score
        item['tc_title'] = tc_title
        item['tc_summary'] = tc_summary
        item['social_comment'] = social_comment
        
        # Formatting Date (Simple string or parse)
        # RSS 'publishedAt' is usually a string.
        
        analyzed_items.append(item)

    # Sort by score descending and take top 15
    analyzed_items.sort(key=lambda x: x['score'], reverse=True)
    return analyzed_items[:15]

if __name__ == "__main__":
    pass
