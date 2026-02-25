from flask import Flask, jsonify, request, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'vacancy_bot.db')

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VacancyBot</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);min-height:100vh;color:#fff}
.container{max-width:500px;margin:0 auto;padding:20px}
h1{text-align:center;padding:30px 0;background:linear-gradient(45deg,#00d9ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.menu{display:flex;flex-direction:column;gap:12px}
.menu-item{background:linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05));border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:18px 24px;display:flex;align-items:center;gap:16px;cursor:pointer;transition:all 0.3s}
.menu-item:hover{transform:translateY(-3px);border-color:rgba(0,217,255,0.5);box-shadow:0 10px 30px rgba(0,217,255,0.2)}
.icon{font-size:28px;width:50px;height:50px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#00d9ff,#00ff88);border-radius:14px}
.title{font-size:16px;font-weight:600}
.subtitle{font-size:12px;color:#8892b0}
.arrow{color:#8892b0}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:20px 0}
.stat-card{background:linear-gradient(135deg,rgba(0,217,255,0.1),rgba(0,255,136,0.05));border:1px solid rgba(0,217,255,0.2);border-radius:14px;padding:16px;text-align:center}
.stat-value{font-size:28px;font-weight:bold;background:linear-gradient(45deg,#00d9ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-label{font-size:12px;color:#8892b0;margin-top:4px}
.page{display:none}
.page.active{display:block}
.back-btn{background:none;border:none;color:#8892b0;font-size:14px;cursor:pointer;padding:10px 0}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:14px;color:#8892b0;margin-bottom:8px}
.form-group input,.form-group select{width:100%;padding:14px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;color:#fff;font-size:16px}
.btn{background:linear-gradient(135deg,#00d9ff,#00ff88);color:#1a1a2e;border:none;padding:16px;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;width:100%;margin-top:16px}
.vacancy-card{background:linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05));border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:20px;margin-bottom:12px}
.vacancy-card h3{color:#00d9ff;margin-bottom:8px}
.salary{font-size:20px;font-weight:bold;background:linear-gradient(45deg,#00ff88,#00d9ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:10px 0}
.nav{display:flex;gap:10px;margin-top:15px}
.nav-btn{flex:1;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.2);padding:12px;border-radius:10px;cursor:pointer}
.nav-btn:disabled{opacity:0.3}
.notification{position:fixed;top:20px;left:50%;transform:translateX(-50%) translateY(-100px);background:linear-gradient(135deg,#00d9ff,#00ff88);color:#1a1a2e;padding:14px 28px;border-radius:12px;font-weight:600;z-index:1000;transition:transform 0.4s}
.notification.show{transform:translateX(-50%) translateY(0)}
</style></head>
<body>
<div class="notification" id="notif">✓ Успешно!</div>
<div class="container">
<div class="page active" id="home">
<h1>🏗 VacancyBot</h1>
<p style="text-align:center;color:#8892b0;margin-bottom:20px;">Ваш надёжный партнёр по вахтовой работе</p>
<div class="stats">
<div class="stat-card"><div class="stat-value" id="cnt1">0</div><div class="stat-label">Кандидатов</div></div>
<div class="stat-card"><div class="stat-value" id="cnt2">0</div><div class="stat-label">Вакансий</div></div>
</div>
<div class="menu">
<div class="menu-item" onclick="show('form')"><div class="icon">📝</div><div style="flex:1"><div class="title">Заполнить анкету</div><div class="subtitle">Начните путь к работе</div></div><div class="arrow">→</div></div>
<div class="menu-item" onclick="show('vac')"><div class="icon">💼</div><div style="flex:1"><div class="title">Вакансии</div><div class="subtitle">Актуальные предложения</div></div><div class="arrow">→</div></div>
<div class="menu-item" onclick="show('loc')"><div class="icon">📍</div><div style="flex:1"><div class="title">Локации</div><div class="subtitle">Города работы</div></div><div class="arrow">→</div></div>
<div class="menu-item" onclick="show('contact')"><div class="icon">📞</div><div style="flex:1"><div class="title">Контакты</div><div class="subtitle">Свяжитесь с нами</div></div><div class="arrow">→</div></div>
<div class="menu-item" onclick="show('help')"><div class="icon">❓</div><div style="flex:1"><div class="title">Как это работает</div><div class="subtitle">4 шага</div></div><div class="arrow">→</div></div>
</div></div>
<div class="page" id="form">
<button class="back-btn" onclick="show('home')">← Назад</button>
<h1>📝 Анкета</h1>
<form onsubmit="submit(event)" style="margin-top:20px">
<div class="form-group"><label>ФИО</label><input type="text" id="name" required></div>
<div class="form-group"><label>Возраст</label><input type="number" id="age" min="18" max="70" required></div>
<div class="form-group"><label>Гражданство</label><select id="cit" required><option value="">Выберите</option><option>Россия</option><option>Беларусь</option><option>Казахстан</option><option>Узбекистан</option><option>Кыргызстан</option><option>Таджикистан</option><option>Другое</option></select></div>
<button type="submit" class="btn">Отправить 🚀</button>
</form></div>
<div class="page" id="vac">
<button class="back-btn" onclick="show('home')">← Назад</button>
<h1>💼 Вакансии</h1>
<div id="vac-list"></div>
<div class="nav" id="vac-nav" style="display:none"><button class="nav-btn" id="prev" onclick="prev()">←</button><span id="vac-cnt" style="color:#8892b0;display:flex;align-items:center"></span><button class="nav-btn" id="next" onclick="next()">→</button></div></div>
<div class="page" id="loc">
<button class="back-btn" onclick="show('home')">← Назад</button>
<h1>📍 Локации</h1>
<div class="vacancy-card"><h3>🏙 Москва</h3><p>Склады, строительство</p><div class="salary">от 80 000 ₽</div></div>
<div class="vacancy-card"><h3>🏙 СПб</h3><p>Порт, производство</p><div class="salary">от 75 000 ₽</div></div>
<div class="vacancy-card"><h3>🏔 Север</h3><p>Нефтегаз</p><div class="salary">от 120 000 ₽</div></div>
<div class="vacancy-card"><h3>🏖 Юг</h3><p>Сельхоз, курорты</p><div class="salary">от 60 000 ₽</div></div></div>
<div class="page" id="contact">
<button class="back-btn" onclick="show('home')">← Назад</button>
<h1>📞 Контакты</h1>
<div class="menu" style="margin-top:20px">
<div class="menu-item" onclick="location.href='tel:+79990000000'"><div class="icon">📱</div><div style="flex:1"><div class="title">Позвонить</div><div class="subtitle">+7 (999) 000-00-00</div></div><div class="arrow">→</div></div>
<div class="menu-item" onclick="window.open('https://t.me/vakansiya_manager')"><div class="icon">💬</div><div style="flex:1"><div class="title">Telegram</div><div class="subtitle">@vakansiya_manager</div></div><div class="arrow">→</div></div>
<div class="menu-item" onclick="location.href='mailto:hr@vakansiya.ru'"><div class="icon">📧</div><div style="flex:1"><div class="title">Email</div><div class="subtitle">hr@vakansiya.ru</div></div><div class="arrow">→</div></div>
</div></div>
<div class="page" id="help">
<button class="back-btn" onclick="show('home')">← Назад</button>
<h1>❓ Как это работает</h1>
<div class="menu" style="margin-top:20px">
<div class="menu-item"><div class="icon">1️⃣</div><div style="flex:1"><div class="title">Анкета</div><div class="subtitle">1 минута</div></div></div>
<div class="menu-item"><div class="icon">2️⃣</div><div style="flex:1"><div class="title">Звонок</div><div class="subtitle">24 часа</div></div></div>
<div class="menu-item"><div class="icon">3️⃣</div><div style="flex:1"><div class="title">Собеседование</div><div class="subtitle">Онлайн/офис</div></div></div>
<div class="menu-item"><div class="icon">4️⃣</div><div style="flex:1"><div class="title">Выезд</div><div class="subtitle">Жильё предоставляем</div></div></div>
</div><button class="btn" onclick="show('form')" style="margin-top:24px">Начать 🚀</button></div>
</div>
<script>
let vac=[],idx=0;
function show(p){document.querySelectorAll('.page').forEach(e=>e.classList.remove('active'));document.getElementById(p).classList.add('active');if(p==='vac')loadVac();if(p==='home')loadStats();}
async function loadStats(){try{const r=await fetch('/api/stats');const d=await r.json();document.getElementById('cnt1').textContent=d.candidates||0;document.getElementById('cnt2').textContent=d.vacancies||0;}catch(e){}}
async function loadVac(){const c=document.getElementById('vac-list');const n=document.getElementById('vac-nav');try{const r=await fetch('/api/vacancies');vac=await r.json();if(!vac.length){c.innerHTML='<p style="text-align:center;padding:40px;color:#8892b0">Нет вакансий</p>';n.style.display='none';return}idx=0;showVac();n.style.display='flex'}catch(e){c.innerHTML='<p style="text-align:center;padding:40px;color:#8892b0">Ошибка</p>';n.style.display='none'}}
function showVac(i){if(!vac.length)return;const v=vac[i];document.getElementById('vac-list').innerHTML='<div class="vacancy-card"><h3>'+v.title+'</h3><p>'+v.description+'</p><div class="salary">'+v.salary+'</div><div style="color:#8892b0">📍 '+v.location+'</div></div>';document.getElementById('vac-cnt').textContent=(i+1)+' из '+vac.length;document.getElementById('prev').disabled=i===0;document.getElementById('next').disabled=i===vac.length-1}
function prev(){if(idx>0){idx--;showVac(idx)}}
function next(){if(idx<vac.length-1){idx++;showVac(idx)}}
async function submit(e){e.preventDefault();const d={name:document.getElementById('name').value,age:document.getElementById('age').value,citizenship:document.getElementById('cit').value};try{await fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});document.getElementById('notif').textContent='✓ Отправлено!';document.getElementById('notif').classList.add('show');setTimeout(()=>document.getElementById('notif').classList.remove('show'),3000);}catch(err){}}
loadStats();
</script>
</body></html>'''

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/stats')
def stats():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM candidates")
        c = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM vacancies")
        v = cur.fetchone()[0]
        conn.close()
        return jsonify({'candidates': c, 'vacancies': v})
    except Exception as e:
        return jsonify({'candidates': 0, 'vacancies': 0})

@app.route('/api/vacancies')
def vacancies():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT title, description, location, salary FROM vacancies ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return jsonify([{'title': r['title'], 'description': r['description'], 'location': r['location'], 'salary': r['salary']} for r in rows])
    except:
        return jsonify([])

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO candidates (name, age, citizenship) VALUES (?, ?, ?)",
            (data.get('name'), data.get('age'), data.get('citizenship')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
