import requests
import os
import sys
from dotenv import load_dotenv

def set_webhook(url):
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return
        
    webhook_url = f"{url.rstrip('/')}/telegram"
    api_url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
    
    print(f"Setting webhook to: {webhook_url}...")
    r = requests.get(api_url)
    print(f"Telegram Response: {r.json()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_webhook.py https://unknotty-ava-subsuperficially.ngrok-free.dev")
        sys.exit(1)
        
    set_webhook(sys.argv[1])
