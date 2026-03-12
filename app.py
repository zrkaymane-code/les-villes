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

# --- واجهة الهوست (التصميم الأزرق الملكي) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANDIZ AI - Control Panel</title>
    <style>
        body { background: radial-gradient(circle, #0f172a, #1e3a8a); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); border-radius: 30px; padding: 30px; width: 90%; max-width: 450px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.5); }
        h1 { color: #60a5fa; font-size: 28px; margin-bottom: 10px; }
        .counter-box { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 20px; margin: 20px 0; border: 1px border: 1px solid #2563eb; }
        .counter-number { font-size: 48px; font-weight: bold; color: #34d399; }
        .btn { width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-fix { background: #2563eb; color: white; }
        .btn-fix:hover { background: #1d4ed8; transform: scale(1.02); }
        .status { font-size: 14px; color: #94a3b8; margin-top: 15px; }
        .pulse { animation: pulse-animation 2s infinite; }
        @keyframes pulse-animation { 0% { box-shadow: 0 0 0 0px rgba(52, 211, 153, 0.4); } 100% { box-shadow: 0 0 0 20px rgba(52, 211, 153, 0); } }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 SANDIZ HOST v12</h1>
        <p>نظام أتمتة الطلبيات والمدن</p>
        
        <div class="counter-box pulse">
            <div style="font-size: 16px; color: #94a3b8;">إجمالي طلبيات اليوم</div>
            <div class="counter-number" id="count">{{ count }}</div>
        </div>

        <button class="btn btn-fix" onclick="runFix()">⚡ تصحيح المدن الآن (Poe AI)</button>
        
        <div class="status" id="status">النظام يعمل وجاهز لاستقبال "Go"</div>
    </div>

    <script>
        async function runFix() {
            const status = document.getElementById('status');
            status.innerText = "⏳ جاري الاتصال بـ Poe AI...";
            try {
                const res = await fetch('/manual_fix', {method: 'POST'});
                const data = await res.json();
                status.innerText = "✅ تم تصحيح المدن بنجاح!";
                setTimeout(() => { status.innerText = "النظام يعمل وجاهز"; }, 3000);
            } catch (e) {
                status.innerText = "❌ خطأ في الاتصال";
            }
        }
    </script>
</body>
</html>
"""

# --- الوظائف الخلفية ---

@app.route('/')
def index():
    global order_count
    return render_template_string(HTML_UI, count=order_count)

@app.route('/manual_fix', methods=['POST'])
def manual_fix():
    # استدعاء كود التصحيح (Poe API)
    res = requests.post(GOOGLE_SHEET_URL, json={"action": "get_cities"})
    rows = res.json()
    cities = [str(r[1]) for r in rows[1:] if len(r) > 1]
    if cities:
        # هنا تضع دالة get_poe_correction التي شرحناها سابقاً
        # ... (كود التصحيح) ...
        return jsonify({"status": "success"})
    return jsonify({"status": "empty"})

@app.route('/webhook', methods=['POST'])
def webhook():
    global order_count
    data = request.json
    if data.get('typeWebhook') == 'incomingMessageReceived':
        msg = data['messageData']['textMessageData']['textMessage']
        if "Go" in msg or "go" in msg:
            # معالجة الطلبية
            order_count += 1
            # ... (كود إرسال البيانات لجوجل شيت) ...
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
