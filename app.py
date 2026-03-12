import os
from flask import Flask, render_template_string, request, jsonify
from poe_api_wrapper import PoeApi

app = Flask(__name__)

# --- 1. إعداد الرموز (استخدام متغيرات البيئة للحماية) ---
# ملاحظة: عند الرفع للمنصة، أضف POE_TOKEN في الإعدادات (Environment Variables)
# أو استبدل os.environ.get بالقيمة مباشرة مؤقتاً
POE_PB_TOKEN = os.environ.get("POE_TOKEN", "FkYHHnuPGKZTbLGS4w8cNYgcfHbtFFdkWEeF8eyrxkw==")
BOT_NAME = "chinchilla" # يمكنك تغييره لـ gpt4_o أو claude_3_haiku

# --- 2. إدارة ملف المدن cities.txt ---
def load_cities_from_file():
    filename = 'cities.txt'
    # إنشاء الملف إذا لم يكن موجوداً (مهم للمنصات السحابية)
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech\ntangier\nagadir")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- 3. الواجهة (التصميم الأزرق الملكي SANDIZ AI) ---
HTML_UI = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANDIZ AI - POE Version</title>
    <style>
        body { background: radial-gradient(circle, #1e3a8a, #0f172a); color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .container { width: 95%; max-width: 1000px; background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #60a5fa; margin-bottom: 20px; font-size: 2rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        label { display: block; margin-bottom: 10px; color: #94a3b8; font-weight: bold; }
        textarea { width: 100%; height: 350px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; font-size: 14px; resize: none; box-sizing: border-box; outline: none; transition: border 0.3s; }
        textarea:focus { border-color: #3b82f6; }
        .btn-main { width: 100%; padding: 15px; background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; transition: transform 0.2s; }
        .btn-main:active { transform: scale(0.98); }
        #status { display: none; text-align: center; color: #60a5fa; margin-top: 15px; font-weight: bold; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SANDIZ AI - POE ENGINE</h1>
        <div class="grid">
            <div><label>📥 البيانات المدخلة:</label><textarea id="in" placeholder="أدخل الكلمات هنا..."></textarea></div>
            <div><label>✨ النتائج المستخرجة:</label><textarea id="out" readonly placeholder="النتائج ستظهر هنا..."></textarea></div>
        </div>
        <div id="status">🧠 يتم الآن التواصل مع ذكاء Poe...</div>
        <button class="btn-main" onclick="run()">بدء التحليل الذكي ⚡</button>
    </div>
    <script>
        async function run() {
            const input = document.getElementById('in').value;
            if(!input.trim()) return;
            document.getElementById('status').style.display = 'block';
            document.getElementById('out').value = "";
            try {
                const res = await fetch('/ai_call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: input})
                });
                const data = await res.json();
                document.getElementById('out').value = data.result;
            } catch (e) { 
                alert("خطأ في الاتصال بالسيرفر"); 
            } finally { 
                document.getElementById('status').style.display = 'none'; 
            }
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

    prompt = f"""
    مهمتك: ربط المدخلات بالأسماء الموجودة في هذه القائمة حصراً: [{ref_data}]
    التعليمات:
    1. اختصارات (مثال: كازا -> casablanca).
    2. ممنوع الحروف المشكلة (التزم بالحروف البسيطة).
    3. إذا لم تجد صلة، اكتب "غير موجود".
    4. النتيجة سطر بسطر فقط لكل مدخل.
    المدخلات:
    {user_input}
    """
    
    try:
        # الاتصال بـ Poe
        client = PoeApi(POE_PB_TOKEN)
        response_text = ""
        # جلب الرد
        for chunk in client.send_message(BOT_NAME, prompt):
            response_text = chunk["response"]
        return jsonify({"result": response_text.strip()})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == '__main__':
    # إعداد المنفذ ليتوافق مع Render و Heroku
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
