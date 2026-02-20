import os
import glob
import time
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def send_native_pdf():
    """
    Sends a TextMessage containing the GitHub Raw URL to the new PDF report.
    (Note: LINE Messaging API does NOT support FileSendMessage from Bot to User)
    """
    if not LINE_ACCESS_TOKEN:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN not found.")
        return

    # Find the latest PDF in 'reports' directory
    list_of_files = glob.glob('reports/*.pdf')
    if not list_of_files:
        print("No PDF files found in reports/")
        return
        
    latest_file = max(list_of_files, key=os.path.getctime)
    filename = os.path.basename(latest_file)
    
    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
    taipei_tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(taipei_tz).strftime('%Y-%m-%d')
    
    github_user = os.getenv("GITHUB_USERNAME", "fornewera")
    github_repo = os.getenv("GITHUB_REPO_NAME", "Finance-AI-Scout")
    
    # Since the repository is Private, direct File/Blob URLs return 404 on mobile if not logged in.
    # Provide a link to the repository page, and explicitly instruct the user to log in.
    repo_url = f"https://github.com/{github_user}/{github_repo}/tree/main/reports"

    message_text = f"📊 Finance & AI Scout 每日深度快報 ({today_str})\n\n你的全球財經與 AI 動態報告來囉！\n\n🔒 由於您的專案是私密設定，請點擊下方連結，並確保在瀏覽器中 **【登入 GitHub】** 即可安全檢視：\n\n👉 {repo_url}"

    try:
        user_id = os.getenv("LINE_USER_ID")
        if user_id:
            line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
            print(f"Sent LINE message to user {user_id}")
        else:
            line_bot_api.broadcast(TextSendMessage(text=message_text))
            print("Broadcasted LINE message to all users.")
            
    except LineBotApiError as e:
        print(f"Error sending LINE message: {e}")

if __name__ == "__main__":
    send_native_pdf()
