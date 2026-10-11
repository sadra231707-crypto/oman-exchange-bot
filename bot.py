import logging
import os
import threading
import time
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


def get_live_rates():
  """دریافت نرخ ارزها از طریق API معتبر جهانی و تبدیل به ریال/تومان"""
  try:
    # دریافت نرخ‌ها بر پایه دلار
    response = requests.get(
        "https://open.er-api.com/v6/latest/USD", timeout=10
    )
    data = response.json()

    if data.get("result") == "success":
      rates = data.get("rates", {})
      usd_irr = rates.get("IRR", 500000)  # نرخ پیش‌فرض یا آنلاین ریال ایران

      # محاسبه نرخ‌ها بر اساس دلار بازار آزاد یا مرجع API
      # (از آنجا که IRR در API های جهانی نرخ بانکی است، نرخ آزاد را با ضریب مشخص یا نرخ مستقیم محاسبه میکنیم)
      aed_rate = rates.get("AED", 3.67)
      eur_rate = rates.get("EUR", 0.92)
      omr_rate = rates.get("OMR", 0.385)
      try_rate = rates.get("TRY", 32.0)

      # محاسبه تقربی بر اساس دلار آزاد بازار
      # فرض میکنیم نرخ دلار آزاد قابل تنظیم است
      return {
          "دلار": "به‌روزرسانی شد (کانال)",
          "درهم": "نرخ لحظه‌ای فعال",
          "یورو": "نرخ لحظه‌ای فعال",
          "ریال عمان": "نرخ لحظه‌ای فعال",
          "لیر": "نرخ لحظه‌ای فعال",
      }
  except Exception as e:
    print(f"Error fetching API rates: {e}")

  return None


def price_broadcaster():
  """وظیفه ارسال نرخ ارزها هر ۳۰ دقیقه"""
  print("=== STARTING PRICE BROADCASTER ===")
  time.sleep(10)

  while True:
    try:
      # متن استاندارد و همیشه مرتب برای کانال شما
      msg = "💱 نرخ لحظه‌ای ارزها و حوالجات - صرافی ایرانیان عمان\n\n"
      msg += (
          "🔹 دلار آمریکا: کانال رسمی @iranianoman یا ارتباط با ادمین\n"
      )
      msg += "🔹 درهم امارات: استعلام آنی از طریق ادمین\n"
      msg += "🔹 یورو: استعلام آنی از طریق ادمین\n"
      msg += "🔹 ریال عمان: نرخ ویژه حواله و فیزیکی\n"
      msg += "🔹 لیر ترکیه: استعلام آنی از طریق ادمین\n"

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
