import os
from dotenv import load_dotenv

print(f"Current CWD: {os.getcwd()}")
print(f"Files in CWD: {os.listdir()}")

loaded = load_dotenv(verbose=True)
print(f"load_dotenv() returned: {loaded}")

api_key = os.getenv("NEWS_API_KEY")
print(f"NEWS_API_KEY from env: {api_key}")

if not api_key:
    print("Trying to read .env directly...")
    try:
        with open(".env", "r") as f:
            content = f.read()
            print("First 50 chars of .env:", content[:50])
            for line in content.splitlines():
                if line.startswith("NEWS_API_KEY"):
                    print(f"Found line in .env: {line}")
    except Exception as e:
        print(f"Error reading .env: {e}")
