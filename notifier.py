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
    
    # URL to the RAW PDF on GitHub
    raw_pdf_url = f"https://raw.githubusercontent.com/{github_user}/{github_repo}/main/reports/{filename}"
    
    print(f"Polling GitHub Raw URL until it goes live (checking {raw_pdf_url})...")
    # Wait for GitHub Raw cache to update (can take a short while after push)
    max_retries = 30
    for i in range(max_retries):
        try:
            resp = requests.head(raw_pdf_url)
            if resp.status_code == 200:
                print("GitHub Raw URL is ALIVE! Proceeding to send LINE message.")
                break
        except Exception:
            pass
        print(f"Waiting for GitHub Raw... ({i+1}/{max_retries})")
        time.sleep(5)
    else:
        print("WARNING: GitHub Raw URL did not return 200 OK in time.")

    message_text = f"📊 Finance & AI Scout 每日深度快報 ({today_str})\n\n你的全球財經與 AI 動態報告來囉！請直接點擊下方私密連結開啟 PDF 👇\n\n{raw_pdf_url}"

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
