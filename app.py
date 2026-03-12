import os
import anthropic
from flask import Flask, render_template_string, request, jsonify

app = Flask(__namddddddde__)

# --- إعدادات الحماية والـ API ---
# يفضل وضع المفتاح في متغيرات البيئة Environment Variables
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "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")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# --- وظائف إدارة البيانات ---
def load_cities():
    filename = 'cities.txt'
    # إنشاء ملف افتراضي إذا لم يكن موجوداً
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech\nagadir\ntangier")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- واجهة المستخدم (HTML/CSS/JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANDIZ AI v11 - مطهر البيانات</title>
    <style>
        :root { --primary: #3b82f6; --bg: #0f172a; --card: rgba(30, 41, 59, 0.7); }
        body { 
            background: radial-gradient(circle at top, #1e3a8a, var(--bg)); 
            color: #f8fafc; font-family: 'Segoe UI', system-ui; 
            margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh;
        }
        .container { 
            width: 90%; max-width: 1100px; background: var(--card); 
            padding: 2rem; border-radius: 20px; backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        .header { text-align: center; margin-bottom: 2rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        textarea { 
            width: 100%; height: 400px; background: #020617; color: #38bdf8; 
            border: 1px solid #334155; border-radius: 12px; padding: 1rem; 
            font-family: monospace; font-size: 14px; resize: none; box-sizing: border-box;
        }
        .btn { 
            grid-column: span 2; padding: 1rem; background: var(--primary); 
            color: white; border: none; border-radius: 10px; font-weight: bold; 
            cursor: pointer; font-size: 1.1rem; transition: 0.3s; margin-top: 1rem;
        }
        .btn:hover { background: #2563eb; transform: translateY(-2px); }
        .btn:disabled { background: #64748b; cursor: not-allowed; }
        #loader { display: none; color: #fbbf24; text-align: center; margin-top: 10px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } .btn { grid-column: span 1; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SANDIZ AI <span style="color:var(--primary)">v11</span></h1>
            <p>نظام تصحيح ومطابقة المدن الذكي (Claude Haiku)</p>
        </div>
        <div class="grid">
            <div>
                <label>📥 البيانات الخام (Raw Data):</label>
                <textarea id="inputData" placeholder="أدخل المدن هنا... (مثلاً: kaza, rbatt, mrakch)"></textarea>
            </div>
            <div>
                <label>✨ النتائج المصححة (Matched):</label>
                <textarea id="outputData" readonly placeholder="ستظهر النتائج هنا..."></textarea>
            </div>
            <button id="runBtn" class="btn" onclick="processData()">تنفيذ المطابقة والتحليل ⚡</button>
        </div>
        <div id="loader">🧠 جاري تحليل البيانات عبر Claude AI...</div>
    </div>

    <script>
        async function processData() {
            const input = document.getElementById('inputData').value;
            const btn = document.getElementById('runBtn');
            const loader = document.getElementById('loader');
            const output = document.getElementById('outputData');

            if(!input.trim()) return;

            btn.disabled = true;
            loader.style.display = 'block';
            output.value = "جاري المعالجة...";

            try {
                const response = await fetch('/ai_call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: input})
                });
                const data = await response.json();
                output.value = data.result;
            } catch (err) {
                output.value = "حدث خطأ في الاتصال بالخادم.";
            } finally {
                btn.disabled = false;
                loader.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

# --- المسارات (Routes) ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ai_call', methods=['POST'])
def ai_call():
    user_input = request.json.get('text', '')
    cities_db = load_cities()
    ref_list = ", ".join(cities_db)

    # برومبت محسن لضمان استجابة دقيقة وصارمة من الموديل
    system_prompt = (
        f"You are a data validation expert. Your task is to match user inputs to this specific list: [{ref_list}].\n"
        "Instructions:\n"
        "1. For each line in input, find the most logical match from the list.\n"
        "2. If no clear match exists, write 'غير موجود'.\n"
        "3. Output ONLY the city names, one per line. No conversation or explanation.\n"
        "4. Standardize output to lowercase English characters as per the list."
    )

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            temperature=0, # تعيين الحرارة لصفر لضمان استجابة منطقية ومكررة
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}]
        )
        
        result = message.content[0].text.strip()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    # تشغيل التطبيق
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

