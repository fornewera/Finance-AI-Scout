import os
from dotenv import load_dotenv

load_dotenv()

line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_id = os.getenv("LINE_CHANNEL_ID")

print(f"LINE_CHANNEL_ACCESS_TOKEN present: {bool(line_token)}")
print(f"LINE_CHANNEL_ID present: {bool(line_id)}")

if line_token:
    print(f"Token length: {len(line_token)}")
if line_id:
    print(f"ID length: {len(line_id)}")

with open(".env", "r") as f:
    print("File content check (variable names only):")
    for line in f:
        if "=" in line:
            key = line.split("=")[0]
            val = line.split("=")[1].strip()
            print(f"{key} is {'SET' if val else 'EMPTY'}")
