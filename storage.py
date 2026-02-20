import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import pytz

def save_report(report_items):
    """
    Saves the report to a markdown file and pushes to GitHub.
    """
    taipei_tz = pytz.timezone('Asia/Taipei')
    date_str = datetime.now(taipei_tz).strftime("%Y-%m-%d")
    filename = f"daily_reports/{date_str}.md"
    
    os.makedirs("daily_reports", exist_ok=True)
    
    content = f"# Finance-AI-Scout 每日報告: {date_str}\n\n"
    
    # Using a list format instead of table for better readability with long summaries
    for i, item in enumerate(report_items[:15], 1):
        content += f"## {i}. {item['tc_title']} (得分: {item['score']})\n\n"
        content += f"- **原始媒體**: {item['source']}\n"
        content += f"- **發布時間**: {item['publishedAt']}\n"
        content += f"- **新聞摘要**: {item['tc_summary']}\n"
        content += f"- **社群評論**: {item['social_comment']}\n"
        content += f"- **連結**: [{item['url']}]({item['url']})\n\n"
        content += "---\n\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Report saved to {filename}")
    
    # Git Operations
    try:
        # Check if git exists
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        # Git Init if not exists
        if not os.path.exists(".git"):
            print("Initializing Git repository...")
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)
        
        # Configure Remote
        github_user = os.getenv("GITHUB_USERNAME")
        github_token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO_NAME", "Finance-AI-Scout")
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Check status
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", f"Report {date_str}"], check=True)
        else:
            print("No new changes to commit.")
            
        # Push (Always try if configured, to sync previous failures)
        if github_user and github_token:
            # Use authenticated URL for push
            # In GitHub Actions, GITHUB_TOKEN is provided. 
            # We construct the URL with the token for authentication.
            remote_url = f"https://x-access-token:{github_token}@github.com/{github_user}/{repo_name}.git"
            
            # Check/Update URL
            remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout
            if "origin" in remotes:
                subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
            else:
                subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
            
            print(f"Pushing to GitHub ({github_user}/{repo_name})...")
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
            print("[SUCCESS] Automatically pushed to GitHub.")
        else:
            print("[WARNING] GitHub credentials not found in .env. Committed locally only.")
            
    except FileNotFoundError:
        print("[ERROR] Git not found. Only local files saved.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")

if __name__ == "__main__":
    pass
