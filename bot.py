import logging
import os
import threading
import time
from bs4 import BeautifulSoup
from flask import Flask
import requests
from telegram import Bot

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8893464200:AAGTqdXqZnMhYITVvtm653quvAqH5lCaOV8"
GROUP_CHAT_ID = -1003736738770

bot = Bot(token=TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  return "Oman Exchange Bot is Active!"


def fetch_target_currencies():
  url = "https://arzbin.com/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  target_currencies = ["دلار", "یورو", "لیر", "ریال عمان", "درهم"]
  prices_data = {}
  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      rows = soup.find_all("tr")
      for row in rows:
        text = row.text
        for currency in target_currencies:
          if currency in text and currency not in prices_data:
            prices_data[currency] = text.strip()
  except Exception as e:
    print(f"Error fetching prices: {e}")
  return prices_data


def run_telegram_worker():
  print("=== STARTING TELEGRAM WORKER ===")
  time.sleep(2)  # ۲ ثانیه مکث برای استارت کامل سرور

  while True:
    try:
      print("Fetching prices from Arzbin...")
      prices = fetch_target_currencies()
      msg = "💱 **آخرین نرخ لحظه‌ای ارزها در صرافی ایرانیان عمان**\n\n"
      if prices:
        for curr, val in prices.items():
          msg += f"🔹 {curr}: {val}\n"
      else:
        msg += "🔹 سیستم استخراج قیمت فعال است."

      print(f"Sending message to target ID: {GROUP_CHAT_ID}")
      bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
      print("SUCCESS: Message sent to Telegram channel!")
    except Exception as e:
      print(f"ERROR sending message: {e}")

    # تکرار ارسال هر ۱ ساعت (۳۶۰۰ ثانیه)
    time.sleep(3600)


# اجرا کردن بخش ارسال پیام در یک ترد جداگانه
threading.Thread(target=run_telegram_worker, daemon=True).start()

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
