from flask import Flask, send_from_directory, request, jsonify, render_template_string
import aiosqlite
import asyncio
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DB_PATH = "vacancy_bot.db"

# HTML шаблон Web App
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>VacancyBot</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
            overflow-x: hidden;
        }
        .container { max-width: 500px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px 0; animation: fadeInDown 0.8s ease; }
        .header h1 {
            font-size: 28px;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        .header p { color: #8892b0; font-size: 14px; }
        .menu { display: flex; flex-direction: column; gap: 12px; }
        .menu-item {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 18px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease backwards;
            position: relative;
            overflow: hidden;
        }
        .menu-item::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s ease;
        }
        .menu-item:hover::before { left: 100%; }
        .menu-item:hover {
            transform: translateY(-3px);
            border-color: rgba(0, 217, 255, 0.5);
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.2);
        }
        .menu-item:active { transform: scale(0.98); }
        .menu-item .icon {
            font-size: 28px;
            width: 50px; height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #00d9ff, #00ff88);
            border-radius: 14px;
            flex-shrink: 0;
        }
        .menu-item .content { flex: 1; }
        .menu-item .title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
        .menu-item .subtitle { font-size: 12px; color: #8892b0; }
        .menu-item .arrow { font-size: 20px; color: #8892b0; transition: transform 0.3s ease; }
        .menu-item:hover .arrow { transform: translateX(5px); color: #00d9ff; }
        .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 20px; }
        .stat-card {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 255, 136, 0.05) 100%);
            border: 1px solid rgba(0, 217, 255, 0.2);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-card .label { font-size: 12px; color: #8892b0; margin-top: 4px; }
        .form { display: none; flex-direction: column; gap: 16px; }
        .form.active { display: flex; }
        .form-group { animation: fadeInUp 0.5s ease backwards; }
        .form-group label { display: block; font-size: 14px; color: #8892b0; margin-bottom: 8px; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            color: #fff;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #00d9ff;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
        }
        .form-group select option { background: #1a1a2e; color: #fff; }
        .btn {
            background: linear-gradient(135deg, #00d9ff 0%, #00ff88 100%);
            color: #1a1a2e;
            border: none;
            padding: 16px 32px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.4);
        }
        .btn:active { transform: scale(0.98); }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .back-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            background: transparent;
            border: none;
            color: #8892b0;
            font-size: 14px;
            cursor: pointer;
            padding: 10px 0;
            transition: color 0.3s ease;
        }
        .back-btn:hover { color: #00d9ff; }
        .page { display: none; }
        .page.active { display: block; }
        .vacancy-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 12px;
            animation: fadeInUp 0.5s ease backwards;
        }
        .vacancy-card h3 { color: #00d9ff; margin-bottom: 8px; }
        .vacancy-card .salary {
            font-size: 20px;
            font-weight: bold;
            background: linear-gradient(45deg, #00ff88, #00d9ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        .vacancy-card .info { display: flex; gap: 16px; color: #8892b0; font-size: 13px; margin-top: 10px; }
        .success-animation { text-align: center; padding: 40px 0; }
        .success-icon { font-size: 80px; animation: bounce 1s ease infinite; }
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        .notification {
            position: fixed;
            top: 20px; left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: linear-gradient(135deg, #00d9ff, #00ff88);
            color: #1a1a2e;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            z-index: 1000;
            transition: transform 0.4s ease;
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.4);
        }
        .notification.show { transform: translateX(-50%) translateY(0); }
        .nav-buttons { display: flex; gap: 10px; margin-top: 15px; }
        .nav-btn {
            flex: 1;
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
            padding: 12px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .nav-btn:hover { background: rgba(0, 217, 255, 0.2); border-color: #00d9ff; }
        .nav-btn:disabled { opacity: 0.3; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="notification" id="notification">✓ Успешно!</div>
    <div class="container">
        <!-- Главная -->
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
                        <div class="subtitle">Простые шаги к трудоустройству</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
            </div>
        </div>
        <!-- Анкета -->
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
            <div class="success-animation" id="success-message" style="display: none;">
                <div class="success-icon">✅</div>
                <h2 style="margin: 20px 0;">Анкета отправлена!</h2>
                <p style="color: #8892b0;">Менеджер свяжется с вами в течение 24 часов</p>
                <button class="btn btn-secondary" style="margin-top: 20px;" onclick="showPage('home-page')">Вернуться в меню</button>
            </div>
        </div>
        <!-- Вакансии -->
        <div class="page" id="vacancies-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>💼 Вакансии</h1>
                <p>Актуальные предложения работы</p>
            </div>
            <div id="vacancy-container"></div>
            <div class="nav-buttons" id="vacancy-nav" style="display: none;">
                <button class="nav-btn" id="prev-btn" onclick="prevVacancy()">← Назад</button>
                <span id="vacancy-counter" style="color: #8892b0; display: flex; align-items: center;"></span>
                <button class="nav-btn" id="next-btn" onclick="nextVacancy()">Вперёд →</button>
            </div>
        </div>
        <!-- Локации -->
        <div class="page" id="locations-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>📍 Локации работы</h1>
                <p>Города и объекты трудоустройства</p>
            </div>
            <div class="vacancy-card">
                <h3>🏙 Москва и МО</h3>
                <p>Склады и логистика, Строительство</p>
                <div class="salary">💰 от 80 000 ₽</div>
            </div>
            <div class="vacancy-card">
                <h3>🏙 Санкт-Петербург</h3>
                <p>Портовые работы, Производство</p>
                <div class="salary">💰 от 75 000 ₽</div>
            </div>
            <div class="vacancy-card">
                <h3>🏔 Север (Вахта)</h3>
                <p>Нефтегазовые объекты, Строительство</p>
                <div class="salary">💰 от 120 000 ₽</div>
            </div>
            <div class="vacancy-card">
                <h3>🏖 Юг (Сезон)</h3>
                <p>Сельское хозяйство, Курорты</p>
                <div class="salary">💰 от 60 000 ₽</div>
            </div>
        </div>
        <!-- Контакты -->
        <div class="page" id="contacts-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>📞 Контакты</h1>
                <p>Свяжитесь с нами удобным способом</p>
            </div>
            <div class="menu">
                <div class="menu-item" onclick="window.location.href='tel:+79990000000'">
                    <div class="icon">📱</div>
                    <div class="content">
                        <div class="title">Позвонить</div>
                        <div class="subtitle">+7 (999) 000-00-00</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="window.open('https://t.me/vakansiya_manager', '_blank')">
                    <div class="icon">💬</div>
                    <div class="content">
                        <div class="title">Telegram</div>
                        <div class="subtitle">@vakansiya_manager</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
                <div class="menu-item" onclick="window.location.href='mailto:hr@vakansiya.ru'">
                    <div class="icon">📧</div>
                    <div class="content">
                        <div class="title">Email</div>
                        <div class="subtitle">hr@vakansiya.ru</div>
                    </div>
                    <div class="arrow">→</div>
                </div>
            </div>
            <div style="margin-top: 24px; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 14px;">
                <p style="color: #8892b0; font-size: 14px; margin-bottom: 8px;">🕐 Режим работы:</p>
                <p>Пн-Пт: 9:00 - 18:00 (МСК)</p>
                <p>Сб-Вс: 10:00 - 15:00 (МСК)</p>
            </div>
        </div>
        <!-- Помощь -->
        <div class="page" id="help-page">
            <button class="back-btn" onclick="showPage('home-page')">← Назад</button>
            <div class="header">
                <h1>❓ Как это работает</h1>
                <p>4 простых шага к трудоустройству</p>
            </div>
            <div class="menu">
                <div class="menu-item">
                    <div class="icon">1️⃣</div>
                    <div class="content">
                        <div class="title">Заполните анкету</div>
                        <div class="subtitle">Это займёт 1 минуту</div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="icon">2️⃣</div>
                    <div class="content">
                        <div class="title">Дождитесь звонка</div>
                        <div class="subtitle">Менеджер свяжется в течение 24 часов</div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="icon">3️⃣</div>
                    <div class="content">
                        <div class="title">Пройдите собеседование</div>
                        <div class="subtitle">Онлайн или в офисе</div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="icon">4️⃣</div>
                    <div class="content">
                        <div class="title">Выезжайте на объект</div>
                        <div class="subtitle">Предоставим жильё и спецодежду</div>
                    </div>
                </div>
            </div>
            <button class="btn" style="width: 100%; margin-top: 24px;" onclick="showPage('form-page')">Начать сейчас 🚀</button>
        </div>
    </div>
    <script>
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        const user = tg.initDataUnsafe.user;
        let vacancies = [];
        let currentVacancyIndex = 0;

        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
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
            } catch (e) { console.log('Stats error:', e); }
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
                showVacancy(currentVacancyIndex);
                nav.style.display = 'flex';
            } catch (e) {
                container.innerHTML = '<div style="text-align:center;padding:40px;color:#8892b0;"><p>Ошибка загрузки</p></div>';
                nav.style.display = 'none';
            }
        }

        function showVacancy(index) {
            if (vacancies.length === 0) return;
            const v = vacancies[index];
            const container = document.getElementById('vacancy-container');
            container.innerHTML = '<div class="vacancy-card">' +
                '<h3>' + v.title + '</h3>' +
                '<p>' + v.description + '</p>' +
                '<div class="salary">' + v.salary + '</div>' +
                '<div class="info"><span>📍 ' + v.location + '</span></div>' +
                '</div>';
            document.getElementById('vacancy-counter').textContent = (index + 1) + ' из ' + vacancies.length;
            document.getElementById('prev-btn').disabled = index === 0;
            document.getElementById('next-btn').disabled = index === vacancies.length - 1;
        }

        function prevVacancy() {
            if (currentVacancyIndex > 0) {
                currentVacancyIndex--;
                showVacancy(currentVacancyIndex);
            }
        }

        function nextVacancy() {
            if (currentVacancyIndex < vacancies.length - 1) {
                currentVacancyIndex++;
                showVacancy(currentVacancyIndex);
            }
        }

        async function submitForm(event) {
            event.preventDefault();
            const formData = {
                name: document.getElementById('name').value,
                age: document.getElementById('age').value,
                citizenship: document.getElementById('citizenship').value,
                telegram_id: user ? user.id : null,
                username: user ? user.username : null
            };
            try {
                const res = await fetch('/api/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                if (res.ok) {
                    document.getElementById('anketa-form').style.display = 'none';
                    document.getElementById('success-message').style.display = 'block';
                    showNotification('Анкета успешно отправлена!');
                    tg.sendData(JSON.stringify(formData));
                }
            } catch (e) {
                document.getElementById('anketa-form').style.display = 'none';
                document.getElementById('success-message').style.display = 'block';
                showNotification('Анкета успешно отправлена!');
            }
        }

        function showNotification(message) {
            const n = document.getElementById('notification');
            n.textContent = '✓ ' + message;
            n.classList.add('show');
            setTimeout(() => n.classList.remove('show'), 3000);
        }

        loadStats();
    </script>
</body>
</html>
'''

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM candidates")
    candidates = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM vacancies")
    vacancies = cur.fetchone()[0]
    conn.close()
    return jsonify({'candidates': candidates, 'vacancies': vacancies})

@app.route('/api/vacancies')
def get_vacancies():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, description, location, salary FROM vacancies ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{
        'title': r['title'],
        'description': r['description'],
        'location': r['location'],
        'salary': r['salary']
    } for r in rows])

@app.route('/api/submit', methods=['POST'])
def submit_form():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO candidates (telegram_id, username, name, age, citizenship) VALUES (?, ?, ?, ?, ?)",
        (data.get('telegram_id'), data.get('username'), data.get('name'), data.get('age'), data.get('citizenship'))
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
