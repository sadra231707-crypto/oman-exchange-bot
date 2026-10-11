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
  return "Oman Exchange Bot is Active and Running!"


def send_telegram_msg(text):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {
      "chat_id": GROUP_CHAT_ID,
      "text": text,
  }
  try:
    res = requests.post(url, json=payload, timeout=10)
    print(f"Telegram API Response: {res.json()}")
  except Exception as e:
    print(f"Error sending telegram HTTP request: {e}")


def send_welcome_photo(chat_id, user_name):
  url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
  caption = (
      f"🌸 خوش آمدید {user_name} عزیز!\n\n"
      "به مجموعه صرافی و حواله ایرانیان عمان خوش آمدید.\n"
      "جهت ارتباط با ادمین‌ها و عضویت در گروه و کانال‌های ما از دکمه‌های زیر"
      " استفاده کنید:"
  )

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
      "reply_markup": inline_keyboard,
  }
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"Error sending welcome photo: {e}")


def fetch_rates_from_telegram_web():
  """استخراج نرخ‌ها از نسخه وب کانال‌های عمومی تلگرام"""
  # از چند کانال عمومی معتبر به صورت جایگزین استفاده می‌کنیم
  channels = ["tg_arz", "nerkh_arz"]
  prices_data = {}

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  for channel in channels:
    url = f"https://t.me/s/{channel}"
    try:
      response = requests.get(url, headers=headers, timeout=10)
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message_text")

        # آخرین پیام‌ها را بررسی می‌کنیم تا نرخ‌ها پیدا شوند
        for msg in reversed(messages):
          text = msg.get_text()

          # جستجوی ارزها در متن پیام‌های کانال
          if "دلار" in text and "دلار" not in prices_data:
            prices_data["دلار"] = (
                text[:100] + "..." if len(text) > 100 else text
            )
          if "درهم" in text and "درهم" not in prices_data:
            prices_data["درهم"] = (
                text[:100] + "..." if len(text) > 100 else text
            )
          if "یورو" in text and "یورو" not in prices_data:
            prices_data["یورو"] = (
                text[:100] + "..." if len(text) > 100 else text
            )
          if "ریال عمان" in text and "ریال عمان" not in prices_data:
            prices_data["ریال عمان"] = (
                text[:100] + "..." if len(text) > 100 else text
            )
          if "لیر" in text and "لیر" not in prices_data:
            prices_data["لیر"] = (
                text[:100] + "..." if len(text) > 100 else text
            )

        if len(prices_data) >= 2:
          break  # اگر داده‌ای پیدا شد از حلقه خارج می‌شویم
    except Exception as e:
      print(f"Error fetching from {channel}: {e}")

  return prices_data


def price_broadcaster():
  """وظیفه ارسال نرخ ارزها هر ۳۰ دقیقه"""
  print("=== STARTING PRICE BROADCASTER ===")
  time.sleep(10)

  while True:
    try:
      prices = fetch_rates_from_telegram_web()
      msg = "💱 نرخ لحظه‌ای ارزها و حوالجات (به تومان) - صرافی ایرانیان عمان\n\n"

      target_keys = ["دلار", "درهم", "یورو", "ریال عمان", "لیر"]
      found_any = False

      for key in target_keys:
        if key in prices:
          msg += f"🔹 {key}: {prices[key]}\n"
          found_any = True
        else:
          # مقدار پیش‌فرض در صورت عدم دسترسی لحظه‌ای به کانال
          msg += f"🔹 {key}: استعلام از ادمین\n"

      msg += "\n━━━━━━━━━━━━━━━━━━━━━\n"
      msg += "📞 ارتباط با ادمین‌ها:\n"
      msg += "👤 @Oman_Exchangadmin1 | @OmanTejarat_Admin\n\n"
      msg += "🌐 گروه‌ها و کانال‌های ما:\n"
      msg += "🔹 گروه ۱: t.me/OmanIranians\n"
      msg += "🔹 گروه ۲: t.me/Oman_ExchangeMuscat_Havaleh\n"
      msg += (
          "💬 گروه واتساپ:"
          " https://chat.whatsapp.com/HOCgDM5KNaWIhDrGqO6Cif?s=cl&p=a&mlu=4&ilr=4\n"
      )
      msg += "📢 کانال تلگرام: @iranianoman\n"
      msg += "━━━━━━━━━━━━━━━━━━━━━"

      send_telegram_msg(msg)
    except Exception as e:
      print(f"Error in price broadcaster: {e}")

    time.sleep(1800)  # ۳۰ دقیقه


def telegram_updates_listener():
  """وظیفه شنود ورود اعضای جدید"""
  print("=== STARTING WELCOME LISTENER ===")
  last_update_id = 0

  while True:
    try:
      url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=20"
      res = requests.get(url, timeout=25).json()

      if res.get("ok"):
        for update in res.get("result", []):
          last_update_id = update["update_id"]
          message = update.get("message") or update.get("channel_post")
          if message and "new_chat_members" in message:
            chat_id = message["chat"]["id"]
            for new_member in message["new_chat_members"]:
              first_name = new_member.get("first_name", "عزیز")
              send_welcome_photo(chat_id, first_name)
    except Exception as e:
      print(f"Error in updates listener: {e}")

    time.sleep(3)


if __name__ == "__main__":
  threading.Thread(target=price_broadcaster, daemon=True).start()
  threading.Thread(target=telegram_updates_listener, daemon=True).start()

  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
