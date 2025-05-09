from flask import Flask, request, jsonify
from flasgger import Swagger
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
swagger = Swagger(app)

user_codes = {}  # {'unique_code': 'username'}
messages = {}  # {'username': [{'title': ..., 'body': ..., 'timestamp': datetime}]}


def cleanup_old_messages():
    while True:
        now = datetime.now()
        for username in list(messages):
            filtered = [msg for msg in messages[username] if now - msg['timestamp'] < timedelta(hours=24)]
            if filtered:
                messages[username] = filtered
            else:
                del messages[username]
        time.sleep(3600)  # Check every hour

threading.Thread(target=cleanup_old_messages, daemon=True).start()


@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    unique_code = data.get('unique_code')

    if not username or not unique_code:
        return jsonify({"status": "error", "message": "نام کاربری و کد یونیک لازم است"}), 400

    if unique_code in user_codes:
        return jsonify({"status": "error", "message": "کد یونیک قبلاً ثبت شده است"}), 400

    user_codes[unique_code] = username
    return jsonify({"status": "success", "message": "کاربر ثبت شد"}), 200


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender_code = data.get('unique_code')
    sender_name = data.get('name')
    receiver_code = data.get('receiver_code')
    title = data.get('title')
    body = data.get('body')

    if not sender_code or not sender_name or not receiver_code or not title or not body:
        return jsonify({"status": "error", "message": "اطلاعات ناقص است"}), 400

    # ثبت خودکار کاربر فرستنده اگر ثبت نشده بود
    if sender_code not in user_codes:
        user_codes[sender_code] = sender_name

    receiver_username = user_codes.get(receiver_code)
    if not receiver_username:
        return jsonify({"status": "error", "message": "کد گیرنده نامعتبر است"}), 400

    if receiver_username not in messages:
        messages[receiver_username] = []

    messages[receiver_username].append({"title": title, "body": body, "timestamp": datetime.now()})

    return jsonify({"status": "success", "message": "پیام با موفقیت ارسال شد"}), 200


@app.route('/get_message/<username>', methods=['GET'])
def get_message(username):
    user_messages = messages.get(username, [])
    if user_messages:
        result = [{"title": m['title'], "body": m['body']} for m in user_messages]
        return jsonify(result), 200
    else:
        return jsonify({"status": "error", "message": "پیامی برای این کاربر موجود نیست"}), 404


@app.route('/delete_message/<username>', methods=['DELETE'])
def delete_message(username):
    if username in messages:
        del messages[username]
        return jsonify({"status": "success", "message": "تمام پیام‌ها حذف شدند"}), 200
    else:
        return jsonify({"status": "error", "message": "پیام‌ها برای این کاربر یافت نشد"}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
