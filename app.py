import tkinter as tk
import json
import os
import requests

SERVER_URL = "https://your-render-url.onrender.com"  # ← آدرس سرور Flask
CONFIG_FILE = "config.json"
MESSAGES_FILE = "messages.json"

def load_config():
    """ بارگذاری تنظیمات از فایل یا ثبت کاربر جدید. """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        name = input("نام کاربر را وارد کنید: ")
        response = requests.post(SERVER_URL + "/register_sender", json={"name": name})
        
        if response.status_code == 200:
            data = response.json()
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            return data
        else:
            print("خطا در ثبت نام کاربر!")
            return None

def send_message(message):
    """ ارسال پیام به سرور و نمایش وضعیت ارسال. """
    sender_code = config.get("sender_code")
    if not sender_code:
        status_label.config(text="❌ خطا: کد فرستنده موجود نیست.")
        return

    payload = {
        "sender_code": sender_code,
        "message": message
    }

    try:
        r = requests.post(SERVER_URL + "/send_message", json=payload)
        
        if r.status_code == 200:
            status_label.config(text=f"✅ ارسال شد: {message}")
        else:
            status_label.config(text=f"❌ خطا در ارسال: {r.text}")
    except Exception as e:
        status_label.config(text=f"❌ خطا در ارسال: {str(e)}")

# بارگذاری تنظیمات
config = load_config()

if config is None:
    exit(1)  # اگر تنظیمات بارگذاری نشد، برنامه را تمام کن

# GUI
root = tk.Tk()
root.title("ارسال هشدار")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# بارگذاری پیام‌ها
if os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = ["هشدار ۱", "هشدار ۲", "هشدار ۳"]

for msg in messages:
    btn = tk.Button(frame, text=msg, width=30, command=lambda m=msg: send_message(m))
    btn.pack(pady=5)

status_label = tk.Label(root, text="")
status_label.pack(pady=10)

root.mainloop()
