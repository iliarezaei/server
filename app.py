from flask import Flask, request, jsonify
from flasgger import Swagger
from datetime import datetime, timedelta
import threading
import time
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

user_codes = {}  # {'unique_code': {'username': '...', 'receiver_code': '...'}}
messages = {}  # {'receiver_code': [{'title': ..., 'body': ..., 'timestamp': ...}]}

@app.route('/register', methods=['POST'])
def register_user():
    """
    ثبت کاربر و کد یونیک مربوطه
    ---
    tags:
      - کاربران
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - unique_code
            - receiver_code
          properties:
            username:
              type: string
            unique_code:
              type: string
            receiver_code:
              type: string
    responses:
      200:
        description: کاربر ثبت شد
      400:
        description: نام کاربری، کد یونیک و کد گیرنده لازم است / کد یونیک قبلاً ثبت شده است
    """
    data = request.json
    username = data.get('username')
    unique_code = data.get('unique_code')
    receiver_code = data.get('receiver_code')

    if not username or not unique_code or not receiver_code:
        return jsonify({"status": "error", "message": "نام کاربری، کد یونیک و کد گیرنده لازم است"}), 400

    if unique_code in user_codes:
        return jsonify({"status": "error", "message": "کد یونیک قبلاً ثبت شده است"}), 400

    user_codes[unique_code] = {"username": username, "receiver_code": receiver_code}
    return jsonify({"status": "success", "message": "کاربر ثبت شد"}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    """
    ارسال پیام از طرف فرستنده به گیرنده
    ---
    tags:
      - پیام
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - unique_code
            - title
            - body
          properties:
            unique_code:
              type: string
            title:
              type: string
            body:
              type: string
    responses:
      200:
        description: پیام با موفقیت ارسال شد
      400:
        description: خطا در داده‌های ارسالی / فرستنده یافت نشد
    """
    data = request.json
    sender_code = data.get('unique_code')
    title = data.get('title')
    body = data.get('body')

    if not sender_code or not title or not body:
        return jsonify({"status": "error", "message": "کد فرستنده، عنوان و پیام لازم است"}), 400

    sender_data = user_codes.get(sender_code)
    if not sender_data:
        return jsonify({"status": "error", "message": "کد فرستنده نامعتبر است"}), 400

    receiver_code = sender_data['receiver_code']

    if receiver_code not in messages:
        messages[receiver_code] = []
    messages[receiver_code].append({"title": title, "body": body, "timestamp": datetime.utcnow()})

    return jsonify({"status": "success", "message": "پیام با موفقیت ارسال شد"}), 200

@app.route('/get_message/<receiver_code>', methods=['GET'])
def get_message(receiver_code):
    """
    دریافت پیام‌ها برای یک گیرنده خاص بر اساس کد گیرنده
    ---
    tags:
      - پیام
    parameters:
      - name: receiver_code
        in: path
        type: string
        required: true
    responses:
      200:
        description: پیام‌ها با موفقیت بازیابی شدند
      404:
        description: پیامی برای این کاربر موجود نیست
    """
    user_messages = messages.get(receiver_code, [])
    if user_messages:
        return jsonify(user_messages), 200
    else:
        return jsonify({"status": "error", "message": "پیامی برای این کاربر موجود نیست"}), 404

@app.route('/delete_message/<receiver_code>', methods=['DELETE'])
def delete_message(receiver_code):
    """
    حذف تمام پیام‌ها برای یک گیرنده خاص
    ---
    tags:
      - پیام
    parameters:
      - name: receiver_code
        in: path
        type: string
        required: true
    responses:
      200:
        description: پیام‌ها حذف شدند
      404:
        description: پیام‌ها برای این کاربر یافت نشد
    """
    if receiver_code in messages:
        del messages[receiver_code]
        return jsonify({"status": "success", "message": "تمام پیام‌ها حذف شدند"}), 200
    else:
        return jsonify({"status": "error", "message": "پیام‌ها برای این کاربر یافت نشد"}), 404

# حذف پیام‌های قدیمی‌تر از 24 ساعت

def cleanup_messages():
    while True:
        now = datetime.utcnow()
        for key in list(messages.keys()):
            messages[key] = [msg for msg in messages[key] if now - msg['timestamp'] < timedelta(hours=24)]
            if not messages[key]:
                del messages[key]
        time.sleep(3600)  # هر ساعت یکبار بررسی شود

cleanup_thread = threading.Thread(target=cleanup_messages, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
