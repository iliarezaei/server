import tkinter as tk
import json
import os
import requests

SERVER_URL = "https://your-render-url.onrender.com"  # ← آدرس سرور Flask

CONFIG_FILE = "config.json"
MESSAGES_FILE = "messages.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        name = input("نام کاربر را وارد کنید: ")
        response = requests.post(SERVER_URL + "/register_sender", json={"name": name})
        data = response.json()
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        return data

def send_message(message):
    sender_code = config["sender_code"]
    payload = {
        "sender_code": sender_code,
        "message": message
    }
    try:
        r = requests.post(SERVER_URL + "/send_message", json=payload)
        status_label.config(text=f"✅ ارسال شد: {message}")
    except Exception as e:
        status_label.config(text=f"❌ خطا در ارسال")

# بارگذاری
config = load_config()

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
