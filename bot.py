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

# بنر خوش‌آمدگویی صرافی ایرانیان عمان
WELCOME_IMAGE_URL = (
    "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?q=80&w=1200"
)

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


def send_welcome_photo(chat_id, user_name):
  url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
  caption = (
      f"🌸 **خوش آمدید {user_name} عزیز!** 🌸\n\n"
      "به مجموعه **صرافی و حواله ایرانیان عمان** خوش آمدید.\n"
      "جهت ارتباط با ادمین‌ها و عضویت در گروه و کانال‌های ما از دکمه‌های زیر"
      " استفاده کنید:"
  )

  # دکمه‌های شیشه‌ای (Inline Keyboard) با تمام لینک‌ها
  inline_keyboard = {
      "inline_keyboard": [
          [
              {
                  "text": "👤 پشتیبانی اول",
                  "url": "https://t.me/Oman_Exchangadmin1",
              },
              {
                  "text": "👤 پشتیبانی دوم",
                  "url": "https://t.me/OmanTejarat_Admin",
              },
          ],
          [
              {
                  "text": "👥 گروه ایرانیان عمان",
                  "url": "https://t.me/OmanIranians",
              },
              {
                  "text": "👥 گروه حواله مسقط",
                  "url": "https://t.me/Oman_ExchangeMuscat_Havaleh",
              },
          ],
          [
              {
                  "text": "💬 گروه واتساپ صرافی",
                  "url": (
                      "https://chat.whatsapp.com/HOCgDM5KNaWIhDrGqO6Cif?s=cl&p=a&mlu=4&ilr=4"
                  ),
              }
          ],
          [
              {
                  "text": "📢 کانال رسمی صرافی",
                  "url": "https://t.me/iranianoman",
              }
          ],
      ]
  }

  payload = {
      "chat_id": chat_id,
      "photo": WELCOME_IMAGE_URL,
      "caption": caption,
      "parse_mode": "Markdown",
      "reply_markup": inline_keyboard,
  }
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f
