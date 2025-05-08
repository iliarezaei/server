from flask import Flask, request, jsonify

app = Flask(__name__)

# ایجاد دیکشنری برای نگهداری کدهای یونیک و کاربران مربوطه
user_codes = {}  # {'unique_code': 'username'}
messages = {}  # {'username': [{"title": "title", "body": "body"}]}

@app.route('/register', methods=['POST'])
def register_user():
    """ثبت کاربر و کد یونیک مربوطه"""
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
    """ارسال پیام از طرف فرستنده به گیرنده بر اساس کد یونیک"""
    data = request.json
    unique_code = data.get('unique_code')
    title = data.get('title')
    body = data.get('body')

    if not unique_code or not title or not body:
        return jsonify({"status": "error", "message": "کد یونیک، عنوان و پیام لازم است"}), 400

    # پیدا کردن نام کاربری مربوط به کد یونیک
    username = user_codes.get(unique_code)
    if not username:
        return jsonify({"status": "error", "message": "کد یونیک نامعتبر است"}), 400

    # ذخیره پیام برای گیرنده
    if username not in messages:
        messages[username] = []
    messages[username].append({"title": title, "body": body})

    return jsonify({"status": "success", "message": "پیام با موفقیت ارسال شد"}), 200


@app.route('/get_message/<username>', methods=['GET'])
def get_message(username):
    """دریافت پیام‌ها برای یک کاربر خاص"""
    user_messages = messages.get(username, [])
    if user_messages:
        return jsonify(user_messages), 200
    else:
        return jsonify({"status": "error", "message": "پیامی برای این کاربر موجود نیست"}), 404


@app.route('/delete_message/<username>', methods=['DELETE'])
def delete_message(username):
    """حذف تمام پیام‌ها برای یک کاربر خاص"""
    if username in messages:
        del messages[username]
        return jsonify({"status": "success", "message": "تمام پیام‌ها حذف شدند"}), 200
    else:
        return jsonify({"status": "error", "message": "پیام‌ها برای این کاربر یافت نشد"}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
