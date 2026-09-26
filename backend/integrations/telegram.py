import requests
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

def send_message(chat_id: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text})
    result = resp.json()
    print(f"[telegram.send_message] chat_id={chat_id} result={result}")
    return result