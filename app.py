import os
from flask import Flask, render_template_string, request, jsonify
import openai

app = Flask(__name__)

# --- 1. إعداد Poe API الرسمي (OpenAI SDK) ---
# ضع هنا مفتاح الـ API الذي حصلت عليه من موقع Poe
POE_API_KEY = "FkYHHnuPGKZTbLGS4w8cNYgcfHbtFFdkWEeF8eyrxkw" 

client = openai.OpenAI(
    api_key=POE_API_KEY,
    base_url="https://api.poe.com/v1",
)

# اسم الموديل الذي تريد استخدامه (كما في المثال الخاص بك)
MODEL_NAME = "gpt-5.3-codex"

# --- 2. إدارة ملف المدن ---
def load_cities_from_file():
    filename = 'cities.txt'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech\ntangier")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- 3. الواجهة (التصميم الملكي SANDIZ AI) ---
HTML_UI = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>SANDIZ AI - Official Poe API</title>
    <style>
        body { background: radial-gradient(circle, #1e3a8a, #0f172a); color: #f1f5f9; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .container { width: 90%; max-width: 1000px; background: rgba(255, 255, 255, 0.05); padding: 40px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #60a5fa; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
        textarea { width: 100%; height: 400px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; font-size: 15px; resize: none; box-sizing: border-box; outline: none; }
        .btn-main { width: 100%; padding: 15px; background: #2563eb; color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        #status { display: none; text-align: center; color: #60a5fa; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SANDIZ AI v12 (OFFICIAL API)</h1>
        <div class="grid">
            <div><label>📥 المدخلات:</label><textarea id="in"></textarea></div>
            <div><label>✨ النتائج:</label><textarea id="out" readonly></textarea></div>
        </div>
        <div id="status">🧠 جاري التحليل عبر Poe API الرسمي...</div>
        <button class="btn-main" onclick="run()">بدء التصحيح الذكي ⚡</button>
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
            } catch (e) { alert("خطأ في الاتصال بالسيرفر"); }
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

    prompt = f"ربط المدخلات بالقائمة التالية حصراً: [{ref_data}]. النتيجة سطر بسطر فقط. المدخلات:\n{user_input}"
    
    try:
        # استخدام OpenAI SDK للاتصال بـ Poe
        chat = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = chat.choices[0].message.content
        return jsonify({"result": result_text.strip()})
    
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
