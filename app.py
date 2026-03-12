import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- الإعدادات (تأكد من وضع روابطك الصحيحة) ---
ID_INSTANCE = "7107544473"
API_TOKEN_INSTANCE = "c942533f2ff9410b973aea7c026a4e9c7d05bd55fb724619ba"
POE_API_KEY = "FkYHHnuPGKZTbLGS4w8cNYgcfHbtFFdkWEeF8eyrxkw"
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyuV_xRWtoDytI9n2bGCflu11B-2J52OPtuggRfjMRbkOGL_mxidtOkec9qZePAroJq/exec"

# عداد الطلبيات (مؤقت في الذاكرة)
order_count = 0

# --- وظيفة تصحيح المدن عبر Poe ---
def get_poe_correction(cities_list):
    if not cities_list: return []
    
    # قراءة المدن المرجعية من ملفك
    cities_db = ""
    if os.path.exists('cities.txt'):
        with open('cities.txt', 'r', encoding='utf-8') as f:
            cities_db = f.read().replace('\n', ', ')
    
    cities_str = "\n".join(cities_list)
    prompt = f"طابق هذه المدن بالقائمة: [{cities_db}]. أخرج مدينة واحدة لكل سطر فقط:\n{cities_str}"
    
    headers = {"Authorization": f"Bearer {POE_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "chinchilla", # أو gpt-3.5-turbo حسب المتاح بـ Poe
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post("https://api.poe.com/v1/chat/completions", json=payload, headers=headers)
        return [line.strip() for line in response.json()['choices'][0]['message']['content'].strip().split('\n') if line.strip()]
    except:
        return cities_list

# --- واجهة الهوست (التصميم الأزرق الملكي) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANDIZ AI - Control Panel</title>
    <style>
        body { background: radial-gradient(circle, #0f172a, #1e3a8a); color: white; font-family: sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); border-radius: 30px; padding: 30px; width: 90%; max-width: 450px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.5); }
        h1 { color: #60a5fa; font-size: 28px; }
        .counter-box { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 20px; margin: 20px 0; border: 1px solid #2563eb; }
        .counter-number { font-size: 50px; font-weight: bold; color: #34d399; }
        .btn { width: 100%; padding: 15px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; cursor: pointer; background: #2563eb; color: white; transition: 0.3s; }
        .btn:active { transform: scale(0.95); }
        .status { font-size: 14px; color: #94a3b8; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 SANDIZ HOST v12</h1>
        <div class="counter-box">
            <div style="font-size: 16px;">طلبيات اليوم</div>
            <div class="counter-number" id="count">{{ count }}</div>
        </div>
        <button class="btn" onclick="runFix()">⚡ تصحيح المدن (Poe AI)</button>
        <div class="status" id="status">جاهز للاستقبال..</div>
    </div>
    <script>
        async function runFix() {
            document.getElementById('status').innerText = "⏳ جاري التصحيح...";
            const res = await fetch('/manual_fix', {method: 'POST'});
            document.getElementById('status').innerText = "✅ اكتمل التصحيح!";
            setTimeout(() => { document.getElementById('status').innerText = "جاهز للاستقبال.."; }, 3000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    global order_count
    return render_template_string(HTML_UI, count=order_count)

@app.route('/manual_fix', methods=['POST'])
def manual_fix():
    res = requests.post(GOOGLE_SHEET_URL, json={"action": "get_cities"})
    try:
        all_rows = res.json()
        cities_to_fix = [str(r[1]) for r in all_rows[1:] if len(r) > 1]
        if cities_to_fix:
            fixed_list = get_poe_correction(cities_to_fix)
            requests.post(GOOGLE_SHEET_URL, json={"action": "update_fixed_cities", "fixed_list": fixed_list})
            return jsonify({"status": "success"})
    except: pass
    return jsonify({"status": "error"})

@app.route('/webhook', methods=['POST'])
def webhook():
    global order_count
    data = request.json
    if data.get('typeWebhook') == 'incomingMessageReceived':
        msg = data['messageData']['textMessageData']['textMessage']
        if "Go" in msg or "go" in msg:
            order_count += 1
            clean = msg.replace("Go","").replace("go","").strip()
            lines = [l.strip() for l in clean.split('\n') if l.strip()]
            if len(lines) >= 4:
                payload = {"action": "add_order", "name": lines[0], "city": lines[1], "address": lines[2], "phone": lines[3]}
                requests.post(GOOGLE_SHEET_URL, json=payload)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
