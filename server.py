import os
from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)
DB_PATH = "vacancy_bot.db"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VacancyBot</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh; color: #fff;
        }
        .container { max-width: 500px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px 0; }
        .header h1 {
            font-size: 28px;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header p { color: #8892b0; font-size: 14px; }
        .menu { display: flex; flex-direction: column; gap: 12px; }
        .menu-item {
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 18px 24px;
            display: flex; align-items: center; gap: 16px;
            cursor: pointer; transition: all 0.3s ease;
        }
        .menu-item:hover {
            transform: translateY(-3px);
            border-color: rgba(0, 217, 255, 0.5);
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.2);
        }
        .menu-item .icon {
            font-size: 28px; width: 50px; height: 50px;
            display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #00d9ff, #00ff88);
            border-radius: 14px;
        }
        .menu-item .content { flex: 1; }
        .menu-item .title { font-size: 16px; font-weight: 600; }
        .menu-item .subtitle { font-size: 12px; color: #8892b0; }
        .menu-item .arrow { color: #8892b0; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; }
        .stat-card {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(0, 255, 136, 0.05));
            border: 1px solid rgba(0, 217, 255, 0.2);
            border-radius: 14px; padding: 16px; text-align: center;
        }
        .stat-card .value {
            font-size: 28px; font-weight: bold;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stat-card .label { font-size: 12px; color: #8892b0; margin-top: 4px; }
        .page { display: none; }
        .page.active { display: block; }
        .back-btn {
            background: none; border: none; color: #8892b0;
            font-size: 14px; cursor: pointer; padding: 10px 0;
        }
        .back-btn:hover { color: #00d9ff; }
        .form { display: none; flex-direction: column; gap: 16px; }
        .form.active { display: flex; }
        .form-group label { display: block; font-size: 14px; color: #8892b0; margin-bottom: 8px; }
        .form-group input, .form-group select {
            width: 100%; padding: 14px 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px; color: #fff; font-size: 16px;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none; border-color: #00d9ff;
        }
        .btn {
            background: linear-gradient(135deg, #00d9ff, #00ff88);
            color: #1a1a2e; border: none; padding: 16px;
            border-radius: 12px; font-size: 16px; font-weight: 600;
            cursor: pointer; width: 100%;
        }
        .vacancy-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 20px; margin-bottom: 12px;
        }
        .vacancy-card h3 { color: #00d9ff; margin-bottom: 8px; }
        .vacancy-card .salary {
            font-size: 20px; font-weight: bold;
            background: linear-gradient(45deg, #00ff88, #00d9ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .nav-buttons { display: flex; gap: 10px; margin-top: 15px; }
        .nav-btn {
            flex: 1; background: rgba(255,255,255,0.1); color: #fff;
            border: 1px solid rgba(255,255,255,0.2); padding: 12px;
            border-radius: 10px; cursor: pointer;
        }
        .nav-btn:disabled { opacity: 0.3; }
        .notification {
            position: fixed; top: 20px; left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: linear-gradient(135deg, #00d9ff, #00ff88);
            color: #1a1a2e; padding: 14px 28px; border-radius: 12px;
            font-weight: 600; z-index: 1000;
            transition: transform 0.4s ease;
        }
        .notification.show { transform: translateX(-50%) translateY(0); }
    </style>
</head>
<body>
    <div class="notification" id="notification">✓ Успешно!</div>
    <div class="container">
        <div class="page active" id="home-page">
            <div class="header">
                <h1>🏗 VacancyBot</h1>
                <p>Ваш надёжный партнёр по вахтовой работе</p>
            </div>
            <div class="stats">
                <div class="stat-card">
                    <div class="value" id="total-candidates">0</div>
                    <div class="label">Кандидатов</div>
                </div>
                <div class="stat-card">
                    <div class="value" id="total-vacancies">0</div>
                    <div class="label">Вакансий</div>
                </div>
            </div>
            <div class="menu" style="margin-top: 24px;">
                <div class="menu-item" onclick="showPage('form-page')">
                    <div class="icon">📝</div>
                    <div class="content">
                        <div class="title">Заполнить анкету</div>
                        <div class="subtitle">Начните путь к новой работе</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="showPage('vacancies-page')">
                    <div class="icon">💼</div>
                    <div class="content">
                        <div class="title">Вакансии</div>
                        <div class="subtitle">Актуальные предложения</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="showPage('locations-page')">
                    <div class="icon">📍</div>
                    <div class="content">
                        <div class="title">Локации</div>
                        <div class="subtitle">Города и объекты</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="showPage('contacts-page')">
                    <div class="icon">📞</div>
                    <div class="content">
                        <div class="title">Контакты</div>
                        <div class="subtitle">Свяжитесь с нами</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="showPage('help-page')">
                    <div class="icon">❓</div>
                    <div class="content">
                        <div class="title">Как это работает</div>
                        <div class="subtitle">4 шага к трудоустройству</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
            </div>
        </div>
        <div class="page" id="form-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>📝 Анкета соискателя</h1>
                <p>Заполните форму для начала трудоустройства</p>
            </div>
            <form class="form active" id="anketa-form" onsubmit="submitForm(event)">
                <div class="form-group">
                    <label>Ваше имя (ФИО полностью)</label>
                    <input type="text" id="name" required placeholder="Иванов Иван Иванович">
                </div>
                <div class="form-group">
                    <label>Возраст</label>
                    <input type="number" id="age" required placeholder="25" min="18" max="70">
                </div>
                <div class="form-group">
                    <label>Гражданство</label>
                    <select id="citizenship" required>
                        <option value="">Выберите гражданство</option>
                        <option value="Россия">Россия</option>
                        <option value="Беларусь">Беларусь</option>
                        <option value="Казахстан">Казахстан</option>
                        <option value="Узбекистан">Узбекистан</option>
                        <option value="Кыргызстан">Кыргызстан</option>
                        <option value="Таджикистан">Таджикистан</option>
                        <option value="Другое">Другое</option>
                    </select>
                </div>
                <button type="submit" class="btn">Отправить анкету 🚀</button>
            </form>
        </div>
        <div class="page" id="vacancies-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>💼 Вакансии</h1>
                <p>Актуальные предложения работы</p>
            </div>
            <div id="vacancy-container"></div>
            <div class="nav-buttons" id="vacancy-nav" style="display: none;">
                <button class="nav-btn" id="prev-btn" onclick="prevVacancy()">← Назад</button>
                <span id="vacancy-counter" style="color: #8892b0; display: flex; align-items: center; justify-content: center;"></span>
                <button class="nav-btn" id="next-btn" onclick="nextVacancy()">Вперёд →</button>
            </div>
        </div>
        <div class="page" id="locations-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>📍 Локации работы</h1>
            </div>
            <div class="vacancy-card"><h3>🏙 Москва и МО</h3><p>Склады и логистика</p><div class="salary">💰 от 80 000 ₽</div></div>
            <div class="vacancy-card"><h3>🏙 Санкт-Петербург</h3><p>Портовые работы</p><div class="salary">💰 от 75 000 ₽</div></div>
            <div class="vacancy-card"><h3>🏔 Север</h3><p>Нефтегазовые объекты</p><div class="salary">💰 от 120 000 ₽</div></div>
            <div class="vacancy-card"><h3>🏖 Юг</h3><p>Сельское хозяйство</p><div class="salary">💰 от 60 000 ₽</div></div>
        </div>
        <div class="page" id="contacts-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>📞 Контакты</h1>
            </div>
            <div class="menu">
                <div class="menu-item" onclick="location.href='tel:+79990000000'">
                    <div class="icon">📱</div><div class="content"><div class="title">Позвонить</div><div class="subtitle">+7 (999) 000-00-00</div></div><div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="window.open('https://t.me/vakansiya_manager')">
                    <div class="icon">💬</div><div class="content"><div class="title">Telegram</div><div class="subtitle">@vakansiya_manager</div></div><div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="location.href='mailto:hr@vakansiya.ru'">
                    <div class="icon">📧</div><div class="content"><div class="title">Email</div><div class="subtitle">hr@vakansiya.ru</div></div><div class="arrow">→</div>
                </div>
            </div>
        </div>
        <div class="page" id="help-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>❓ Как это работает</h1>
            </div>
            <div class="menu">
                <div class="menu-item"><div class="icon">1️⃣</div><div class="content"><div class="title">Заполните анкету</div><div class="subtitle">Это займёт 1 минуту</div></div></div>
                <div class="menu-item"><div class="icon">2️⃣</div><div class="content"><div class="title">Дождитесь звонка</div><div class="subtitle">Менеджер свяжется в течение 24 часов</div></div></div>
                <div class="menu-item"><div class="icon">3️⃣</div><div class="content"><div class="title">Пройдите собеседование</div><div class="subtitle">Онлайн или в офисе</div></div></div>
                <div class="menu-item"><div class="icon">4️⃣</div><div class="content"><div class="title">Выезжайте на объект</div><div class="subtitle">Предоставим жильё</div></div></div>
            </div>
            <button class="btn" style="margin-top: 24px;" onclick="showPage('form-page')">Начать сейчас 🚀</button>
        </div>
    </div>
    <script>
        const tg = window.Telegram.WebApp;
        tg.ready();
        let vacancies = [];
        let currentVacancyIndex = 0;

        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            if (pageId === 'vacancies-page') loadVacancies();
            if (pageId === 'home-page') loadStats();
        }

        async function loadStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('total-candidates').textContent = data.candidates || 0;
                document.getElementById('total-vacancies').textContent = data.vacancies || 0;
            } catch (e) {}
        }

        async function loadVacancies() {
            const container = document.getElementById('vacancy-container');
            const nav = document.getElementById('vacancy-nav');
            try {
                const res = await fetch('/api/vacancies');
                vacancies = await res.json();
                if (vacancies.length === 0) {
                    container.innerHTML = '<div style="text-align:center;padding:40px;color:#8892b0;"><p>Вакансий пока нет</p></div>';
                    nav.style.display = 'none';
                    return;
                }
                currentVacancyIndex = 0;
                showVacancy(0);
                nav.style.display = 'flex';
            } catch (e) {
                container.innerHTML = '<div style="text-align:center;padding:40px;color:#8892b0;"><p>Ошибка загрузки</p></div>';
                nav.style.display = 'none';
            }
        }

        function showVacancy(i) {
            if (vacancies.length === 0) return;
            const v = vacancies[i];
            document.getElementById('vacancy-container').innerHTML = 
                '<div class="vacancy-card"><h3>' + v.title + '</h3><p>' + v.description + '</p><div class="salary">' + v.salary + '</div><div style="color:#8892b0;">📍 ' + v.location + '</div></div>';
            document.getElementById('vacancy-counter').textContent = (i + 1) + ' из ' + vacancies.length;
            document.getElementById('prev-btn').disabled = i === 0;
            document.getElementById('next-btn').disabled = i === vacancies.length - 1;
        }

        function prevVacancy() { if (currentVacancyIndex > 0) { currentVacancyIndex--; showVacancy(currentVacancyIndex); } }
        function nextVacancy() { if (currentVacancyIndex < vacancies.length - 1) { currentVacancyIndex++; showVacancy(currentVacancyIndex); } }

        async function submitForm(e) {
            e.preventDefault();
            const formData = {
                name: document.getElementById('name').value,
                age: document.getElementById('age').value,
                citizenship: document.getElementById('citizenship').value,
                telegram_id: tg.initDataUnsafe.user?.id,
                username: tg.initDataUnsafe.user?.username
            };
            try {
                await fetch('/api/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
                document.getElementById('anketa-form').style.display = 'none';
                document.getElementById('notification').textContent = '✓ Анкета отправлена!';
                document.getElementById('notification').classList.add('show');
                setTimeout(() => document.getElementById('notification').classList.remove('show'), 3000);
            } catch (e) {}
        }

        loadStats();
    </script>
</body>
</html>
'''

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM candidates")
    candidates = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM vacancies")
    vacancies = cur.fetchone()[0]
    conn.close()
    return jsonify({'candidates': candidates, 'vacancies': vacancies})

@app.route('/api/vacancies')
def vacancies():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT title, description, location, salary FROM vacancies ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{'title': r['title'], 'description': r['description'], 'location': r['location'], 'salary': r['salary']} for r in rows])

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO candidates (telegram_id, username, name, age, citizenship) VALUES (?, ?, ?, ?, ?)",
        (data.get('telegram_id'), data.get('username'), data.get('name'), data.get('age'), data.get('citizenship')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
