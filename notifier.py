import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from dotenv import load_dotenv
from datetime import datetime
import pytz

# Load environment variables
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN") or os.getenv("LINE_CHANNEL_ID")

def send_daily_digest(report_items):
    """
    Sends the top news items as a formatted message to LINE.
    """
    if not LINE_ACCESS_TOKEN:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN (or LINE_CHANNEL_ID) not found.")
        return

    if not report_items:
        print("No report items to send.")
        return

    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
    
    taipei_tz = pytz.timezone('Asia/Taipei')
    header = f"📊 Finance-AI-Scout 每日財經快報 ({datetime.now(taipei_tz).strftime('%Y-%m-%d')})\n\n"
    body = ""
    
    for i, item in enumerate(report_items[:15], 1):
        score_emoji = "🔴" if item['score'] > 80 else "🟡" if item['score'] > 50 else "🟢"
        
        # Format:
        # 1. 🔴 [Score] TC_Title
        #    原始媒體: Source | 時間: Date
        #    摘要: TC_Summary
        #    社群: Social_Comment
        #    URL
        
        body += f"{i}. {score_emoji} [{item['score']}] {item['tc_title']}\n"
        body += f"   📰 原始媒體: {item['source']}\n"
        body += f"   📅 發布時間: {item['publishedAt']}\n"
        body += f"   📝 摘要: {item['tc_summary'][:100]}...\n"
        body += f"   💬 社群評論: {item['social_comment']}\n"
        body += f"   🔗 {item['url']}\n\n"

    full_message = header + body
    
    if len(full_message) > 5000:
        full_message = full_message[:4990] + "..."

    try:
        user_id = os.getenv("LINE_USER_ID")
        if user_id:
            line_bot_api.push_message(user_id, TextSendMessage(text=full_message))
            print(f"Sent LINE message to user {user_id}")
        else:
            line_bot_api.broadcast(TextSendMessage(text=full_message))
            print("Broadcasted LINE message to all users.")
            
    except LineBotApiError as e:
        print(f"Error sending LINE message: {e}")

if __name__ == "__main__":
    pass
