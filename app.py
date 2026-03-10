import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- 1. إعداد Gemini API ---
# من الأفضل وضع المفتاح في Environment Variables على Render باسم GEMINI_API_KEY
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBRWb1WjPZo-pVloT2JFZEmt1WNO_zIarg") 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') # تم تصحيح الموديل إلى إصدار مدعوم

# --- 2. إدارة ملف المدن cities.txt ---
def load_cities_from_file():
    filename = 'cities.txt'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- 3. الواجهة (HTML) ---
HTML_UI = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANDIZ AI - النسخة الاحترافية</title>
    <style>
        body { background: radial-gradient(circle, #1e3a8a, #0f172a); color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .container { width: 95%; max-width: 1000px; background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #60a5fa; margin-bottom: 20px; font-size: 2em; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #93c5fd; }
        textarea { width: 100%; height: 350px; background: rgba(0,0,0,0.4); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 15px; padding: 15px; font-size: 16px; resize: none; box-sizing: border-box; outline: none; transition: 0.3s; }
        textarea:focus { border-color: #60a5fa; box-shadow: 0 0 10px rgba(96, 165, 250, 0.3); }
        .btn-main { width: 100%; padding: 15px; background: linear-gradient(45deg, #2563eb, #1d4ed8); color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; transition: 0.3s; }
        .btn-main:hover { background: linear-gradient(45deg, #3b82f6, #2563eb); transform: translateY(-2px); }
        #status { display: none; text-align: center; color: #fbbf24; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SANDIZ AI v11</h1>
        <div class="grid">
            <div><label>📥 المدخلات (أسماء عشوائية أو مدن):</label><textarea id="in" placeholder="اكتب هنا..."></textarea></div>
            <div><label>✨ النتائج المصححة:</label><textarea id="out" readonly placeholder="النتائج ستظهر هنا..."></textarea></div>
        </div>
        <div id="status">🧠 جاري التحليل الذكي عبر Gemini...</div>
        <button class="btn-main" onclick="run()">تصحيح ومطابقة المدن ⚡</button>
    </div>
    <script>
        async function run() {
            const input = document.getElementById('in').value;
            if(!input.trim()) return;
            document.getElementById('status').style.display = 'block';
            document.getElementById('out').value = "جاري المعالجة...";
            
            try {
                const res = await fetch('/ai_call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: input})
                });
                const data = await res.json();
                document.getElementById('out').value = data.result;
            } catch (e) { 
                alert("خطأ في الاتصال بالخادم"); 
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
    1. ابحث عن المدينة الأقرب للمدخلات (مثال: كازا -> casablanca).
    2. التزم بالحروف البسيطة الإنجليزية (بدون é, à).
    3. إذا لم تجد مطابقة، اكتب "غير موجود".
    4. أخرج النتائج سطر بسطر فقط لكل مدينة مدخلة.

    المدخلات:
    {user_input}
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"result": response.text.strip()})
    except Exception as e:
        return jsonify({"result": f"خطأ: {str(e)}"})

# --- 4. التعديل الجوهري للتشغيل على Render ---
if __name__ == '__main__':
    # Render يمرر المنفذ عبر متغير PORT، ويجب الاستماع على 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

