import os
from flask import Flask, render_template_string, request, jsonify
from poe_api_wrapper import PoeApi

app = Flask(__name__)

# --- إعداد الرموز المستخرجة من السجل الذي أرسلته ---
# ملاحظة: تم تعديل p-b بناءً على آخر سطر أرسلته
TOKENS = {
    "p-b": "Xq3ligs1biXZz0Zm-s9mjg==",
    "p-lat": "None" # جرب None إذا لم تجد p-lat، المكتبة ستحاول العمل بـ p-b وحده أولاً
}

BOT_NAME = "chinchilla" # أو "gpt4_o" إذا كان حسابك يدعمه

# --- إدارة ملف المدن ---
def load_cities_from_file():
    filename = 'cities.txt'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech\ntangier\nagadir")
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- الواجهة الاحترافية (Royal Blue) ---
HTML_UI = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>SANDIZ AI - POE Fixed</title>
    <style>
        body { background: radial-gradient(circle, #1e3a8a, #0f172a); color: #f1f5f9; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .container { width: 90%; max-width: 900px; background: rgba(255, 255, 255, 0.05); padding: 35px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); }
        h1 { text-align: center; color: #60a5fa; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        textarea { width: 100%; height: 350px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; resize: none; outline: none; }
        .btn-main { width: 100%; padding: 15px; background: #2563eb; color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        #status { display: none; text-align: center; color: #60a5fa; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SANDIZ AI - محرك POE الجديد</h1>
        <div class="grid">
            <div><label>📥 المدخلات:</label><textarea id="in"></textarea></div>
            <div><label>✨ النتائج:</label><textarea id="out" readonly></textarea></div>
        </div>
        <div id="status">🧠 جاري معالجة البيانات عبر Poe...</div>
        <button class="btn-main" onclick="run()">تصحيح ومطابقة ⚡</button>
    </div>
    <script>
        async function run() {
            const input = document.getElementById('in').value;
            if(!input.trim()) return;
            document.getElementById('status').style.display = 'block';
            try {
                const res = await fetch('/ai_call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: input})
                });
                const data = await res.json();
                document.getElementById('out').value = data.result;
            } catch (e) { alert("خطأ في الاتصال"); }
            finally { document.getElementById('status').style.display = 'none'; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/ai_call', methods=['POST'])
def ai_call():
    user_input = request.json.get('text', '')
    cities_db = load_cities_from_file()
    ref_data = ", ".join(cities_db)

    prompt = f"ربط المدخلات بالقائمة التالية حصراً: [{ref_data}]. النتيجة سطر بسطر. المدخلات:\n{user_input}"
    
    try:
        # استخدام الرموز الجديدة هنا
        client = PoeApi(tokens=TOKENS)
        response_text = ""
        # إرسال الرسالة
        for chunk in client.send_message(BOT_NAME, prompt):
            response_text = chunk["response"]
            
        return jsonify({"result": response_text.strip()})
    except Exception as e:
        # في حال استمرار الخطأ، سنعرض رسالة واضحة
        return jsonify({"result": f"خطأ في الجلسة: {str(e)}\nتأكد من تحديث p-b و p-lat من المتصفح."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
