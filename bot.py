import logging
import os
import threading
import time
from bs4 import BeautifulSoup
from flask import Flask
import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# تنظیمات لاگ‌ها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# اطلاعات صرافی شما
TOKEN = "8893464200:AAGTqdXqZnMhYITVvtm653quvAqH5lCaOV8"
GROUP_CHAT_ID = -1003736738770

bot = Bot(token=TOKEN)

# ساخت سرور وب برای راضی کردن رندر (جلوگیری از خطای Application exited early)
app = Flask(__name__)


@app.route("/")
def home():
  return "Oman Iranians Exchange Bot is Active and Running!"


# تابع استخراج قیمت‌ها از سایت ارزبین
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
      # جستجوی جدول قیمت‌ها در صفحه
      rows = soup.find_all("tr")
      for row in rows:
        text = row.text
        for currency in target_currencies:
          if currency in text and currency not in prices_data:
            prices_data[currency] = text.strip()
  except Exception as e:
    logger.error(f"Error fetching prices: {e}")
  return prices_data


# حلقه ارسال خودکار قیمت‌ها به گروه
def price_updater_thread():
  while True:
    try:
      prices = fetch_target_currencies()
      msg = (
          "💱 **آخرین نرخ لحظه‌ای ارزها در صرافی ایرانیان عمان**\n\n"
          + "──────────────────\n"
      )
      if prices:
        for curr, val in prices.items():
          msg += f"🔹 {curr}: {val}\n"
      else:
        msg += "⚠️ دریافت اطلاعات از سایت با تاخیر مواجه شد، در حال به‌روزرسانی..."

      bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
      logger.error(f"Error in price updater thread: {e}")
    # هر 1 ساعت یک‌بار (3600 ثانیه)
    time.sleep(3600)


# استارت ترد قیمت‌ها در پس‌زمینه
threading.Thread(target=price_updater_thread, daemon=True).start()

if __name__ == "__main__":
  # گرفتن پورت اختصاصی از رندر
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
