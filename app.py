from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

user_codes = {}  # {'unique_code': 'username'}
messages = {}  # {'username': [{"title": ..., "body": ...}]}

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
          properties:
            username:
              type: string
            unique_code:
              type: string
    responses:
      200:
        description: کاربر ثبت شد
      400:
        description: نام کاربری و کد یونیک لازم است / کد یونیک قبلاً ثبت شده است
    """
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
            - receiver_code
            - title
            - body
          properties:
            unique_code:
              type: string
            receiver_code:
              type: string
            title:
              type: string
            body:
              type: string
    responses:
      200:
        description: پیام با موفقیت ارسال شد
      400:
        description: خطا در داده‌های ارسالی / گیرنده یافت نشد
    """
    data = request.json
    sender_code = data.get('unique_code')
    receiver_code = data.get('receiver_code')
    title = data.get('title')
    body = data.get('body')

    if not sender_code or not receiver_code or not title or not body:
        return jsonify({"status": "error", "message": "کد فرستنده، کد گیرنده، عنوان و پیام لازم است"}), 400

    receiver_username = user_codes.get(receiver_code)
    if not receiver_username:
        return jsonify({"status": "error", "message": "کد گیرنده نامعتبر است"}), 400

    if receiver_username not in messages:
        messages[receiver_username] = []
    messages[receiver_username].append({"title": title, "body": body})

    return jsonify({"status": "success", "message": "پیام با موفقیت ارسال شد"}), 200

@app.route('/get_message/<username>', methods=['GET'])
def get_message(username):
    """
    دریافت پیام‌ها برای یک کاربر خاص
    ---
    tags:
      - پیام
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: پیام‌ها با موفقیت بازیابی شدند
      404:
        description: پیامی برای این کاربر موجود نیست
    """
    user_messages = messages.get(username, [])
    if user_messages:
        return jsonify(user_messages), 200
    else:
        return jsonify({"status": "error", "message": "پیامی برای این کاربر موجود نیست"}), 404

@app.route('/delete_message/<username>', methods=['DELETE'])
def delete_message(username):
    """
    حذف تمام پیام‌ها برای یک کاربر خاص
    ---
    tags:
      - پیام
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: پیام‌ها حذف شدند
      404:
        description: پیام‌ها برای این کاربر یافت نشد
    """
    if username in messages:
        del messages[username]
        return jsonify({"status": "success", "message": "تمام پیام‌ها حذف شدند"}), 200
    else:
        return jsonify({"status": "error", "message": "پیام‌ها برای این کاربر یافت نشد"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
