import schedule
import time
import pytz
from datetime import datetime
from scraper import fetch_headlines
from analyzer import analyze_news
from notifier import send_daily_digest
from storage import save_report


def job():
    taipei_tz = pytz.timezone('Asia/Taipei')
    now_taipei = datetime.now(taipei_tz)
    print(f"Starting job at {now_taipei.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 1. Scrape
    print("Fetching headlines...")
    headlines = fetch_headlines()
    if not headlines:
        print("No headlines fetched.")
        return

    # 2. Analyze
    print("Analyzing news...")
    analysis = analyze_news(headlines)
    if not analysis:
        print("Analysis failed.")
        return

    # 3. Notify & Store
    print("Sending notifications and saving report...")
    send_daily_digest(analysis)
    save_report(analysis)
    
    print("Job completed successfully.")

def run_scheduler():
    # Set timezone to Taipei
    taipei_tz = pytz.timezone('Asia/Taipei')
    
    # Schedule daily at 08:00 Taipei time
    # Note: 'schedule' library uses system time. If system time != Taipei time, need conversion.
    # A robust way is to check the current time in Taipei loop.
    # But usually servers are UTC. 08:00 Taipei is 00:00 UTC.
    # Let's just schedule it based on system time assuming user runs it locally in Taipei or configure it properly.
    # The prompt says "Must execute at 08:00 Taipei Time".
    # Best practice is to run every minute and check if it's 08:00 in Taipei.
    
    print("Scheduler started. Waiting for 08:00 Taipei Time...")
    
    while True:
        now_taipei = datetime.now(taipei_tz)
        current_time = now_taipei.strftime("%H:%M")
        
        # Simple check logic (this might run multiple times in the same minute if loop is fast, so adding a flag or sleep)
        if current_time == "08:00":
            job()
            time.sleep(61) # Wait a minute so it doesn't run again immediately
            
        time.sleep(30) # Check every 30 seconds

import sys

if __name__ == "__main__":
    # If run with --now argument, execute job immediately and exit (for GitHub Actions)
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        job()
    else:
        # Otherwise run as a persistent scheduler
        run_scheduler()
