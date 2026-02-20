import os
import pytz
from datetime import datetime
import time

from scraper import fetch_all_relevant_news
from analyzer import analyze_and_format_news
from pdf_generator import generate_pdf_report

def job():
    taipei_tz = pytz.timezone('Asia/Taipei')
    now_taipei = datetime.now(taipei_tz)
    today_date = now_taipei.strftime('%Y-%m-%d')
    print(f"Starting job at {now_taipei.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    os.makedirs("reports", exist_ok=True)
    pdf_filename = f"daily_report_{today_date}.pdf"
    pdf_filepath = os.path.join("reports", pdf_filename)
    
    # 1. Scrape News (Tavily)
    print("Step 1/4: Fetching news...")
    raw_news = fetch_all_relevant_news()
    if not raw_news.get("finance") and not raw_news.get("ai"):
        print("No news fetched. Aborting.")
        return

    # 2. Analyze & Enrich (Gemini Pro + Tavily Social Sentiment)
    print("Step 2/4: Analyzing news and fetching sentiments...")
    report_data = analyze_and_format_news(raw_news.get("finance", []), raw_news.get("ai", []))
    
    # 3. Generate PDF
    print("Step 3/4: Generating PDF...")
    final_pdf_path = generate_pdf_report(report_data, pdf_filepath)
    if not final_pdf_path:
        print("PDF generation failed. Aborting.")
        return
        
    print("Job completed successfully. PDF is ready to be committed by GitHub Actions.")

import sys
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        job()
    else:
        print("Run with '--now' to execute the job.")
