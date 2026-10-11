import logging
import os
import threading
import time
from bs4 import BeautifulSoup
from flask import Flask
import requests

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8893464200:AAGTqdXqZnMhYITVvtm653quvAqH5lCaOV8"
GROUP_CHAT_ID = "-1003736738770"

app = Flask(__name__)


@app.route("/")
def home():
  return "Oman Exchange Bot is Active!"


def send_telegram_msg(text):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {
      "chat_id": GROUP_CHAT_ID,
      "text": text,
      "parse_mode": "Markdown",
  }
  try:
    res = requests.post(url, json=payload, timeout=10)
    print(f"Telegram API Response: {res.json()}")
  except Exception as e:
    print(f"Error sending telegram HTTP request: {e}")


def fetch_target_currencies():
  url = "https://arzbin.com/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }
  target_currencies = ["دلار", "یورو", "لیر", "ریال عمان", "درهم"]
  prices_data = {}
  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      # جستجوی عمومی در تمام تگ‌ها برای پیدا کردن نام ارز و متن اطراف آن
      for text_item in soup.stripped_strings:
        for currency in target_currencies:
          if currency in text_item and currency not in prices_data:
            # سعی می‌کنیم بلوک والد یا متن خط را پیدا کنیم
            prices_data[currency] = text_item
  except Exception as e:
    print(f"Error fetching prices: {e}")
  return prices_data


def run_telegram_worker():
  print("=== STARTING TELEGRAM WORKER ===")
  time.sleep(3)

  while True:
    try:
      print("Fetching prices from Arzbin...")
      prices = fetch_target_currencies()
      msg = "💱 *آخرین نرخ لحظه‌ای ارزها در صرافی ایرانیان عمان*\n\n"
      if prices:
        for curr, val in prices.items():
          msg += f"🔹 *{curr}*: {val}\n"
      else:
        msg += "🔹 نرخ‌ها در حال به‌روزرسانی هستند."

      print("Sending message via Telegram API...")
      send_telegram_msg(msg)
      print("SUCCESS: Request sent!")
    except Exception as e:
      print(f"ERROR in loop: {e}")

    # ارسال مجدد هر ۱ ساعت
    time.sleep(3600)


# شروع ارسال پیام
threading.Thread(target=run_telegram_worker, daemon=True).start()

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
