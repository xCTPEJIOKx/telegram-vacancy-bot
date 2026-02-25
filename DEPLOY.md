# 🚀 Инструкция по развёртыванию на хостинге

## Вариант 1: PythonAnywhere (Бесплатно)

### 1. Регистрация
1. Перейдите на https://www.pythonanywhere.com
2. Зарегистрируйтесь (бесплатный аккаунт)

### 2. Загрузка файлов
1. В панели управления нажмите **Files** → **Upload a file**
2. Загрузите все файлы проекта:
   - `bot.py`
   - `server.py`
   - `requirements.txt`
   - `.env` (с токеном и ADMIN_IDS)

### 3. Установка зависимостей
Откройте **Consoles** → **Bash** и выполните:
```bash
pip install --user -r requirements.txt
```

### 4. Настройка Web App
1. Перейдите в **Web** → **Add a new web app**
2. Выберите **Flask** → **Python 3.10**
3. В настройках укажите:
   - Source code: `/home/yourusername/server.py`
   - Working directory: `/home/yourusername/`

### 5. Запуск бота
1. Откройте **Consoles** → **Bash**
2. Запустите бота:
```bash
python bot.py &
```

### 6. Настройка HTTPS URL
Ваш Web App будет доступен по адресу:
```
https://yourusername.pythonanywhere.com
```

### 7. Обновление bot.py
Измените строку в `bot.py`:
```python
WebAppInfo(url="https://yourusername.pythonanywhere.com")
```

### 8. Автозапуск (важно!)
Создайте файл `startup.sh`:
```bash
#!/bin/bash
cd /home/yourusername
python bot.py &
```

Добавьте в **Crontab**:
```
*/5 * * * * /home/yourusername/startup.sh
```

---

## Вариант 2: Railway (Бесплатно с ограничениями)

### 1. Регистрация
1. Перейдите на https://railway.app
2. Войдите через GitHub

### 2. Создание проекта
1. Нажмите **New Project**
2. Выберите **Deploy from GitHub repo**
3. Подключите ваш репозиторий

### 3. Настройка переменных окружения
В **Variables** добавьте:
```
TELEGRAM_BOT_TOKEN=ваш_токен
ADMIN_IDS=ваш_id
PORT=5000
```

### 4. Создайте файл `Procfile`:
```
web: python server.py & python bot.py
```

### 5. Создайте файл `runtime.txt`:
```
python-3.10.0
```

### 6. Деплой
Railway автоматически развернёт проект.
URL будет вида: `https://your-project.railway.app`

### 7. Обновите bot.py:
```python
WebAppInfo(url="https://your-project.railway.app")
```

---

## Вариант 3: Render (Бесплатно)

### 1. Регистрация
https://render.com

### 2. Создание Web Service
1. **New** → **Web Service**
2. Подключите репозиторий GitHub
3. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`

### 3. Переменные окружения
Добавьте в **Environment**:
```
TELEGRAM_BOT_TOKEN=ваш_токен
ADMIN_IDS=ваш_id
```

### 4. Для бота создайте отдельный сервис
1. **New** → **Background Worker**
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `python bot.py`

---

## Вариант 4: VPS (Платно, ~5$/месяц)

### Провайдеры:
- DigitalOcean Droplet
- Linode
- Vultr
- Timeweb Cloud (Россия)

### Установка на Ubuntu:

```bash
# Обновление
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip -y

# Установка nginx
sudo apt install nginx -y

# Клонирование проекта
git clone https://github.com/yourusername/telegram-vacancy-bot.git
cd telegram-vacancy-bot

# Установка зависимостей
pip3 install -r requirements.txt

# Настройка .env
nano .env  # Вставьте токен и ADMIN_IDS

# Запуск через systemd
sudo nano /etc/systemd/system/vacancy-bot.service
```

Содержимое `vacancy-bot.service`:
```ini
[Unit]
Description=VacancyBot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/telegram-vacancy-bot
ExecStart=/usr/bin/python3 /var/www/telegram-vacancy-bot/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Включение сервиса
sudo systemctl enable vacancy-bot
sudo systemctl start vacancy-bot
sudo systemctl status vacancy-bot

# Настройка nginx
sudo nano /etc/nginx/sites-available/vacancy-bot
```

Содержимое nginx конфига:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активация
sudo ln -s /etc/nginx/sites-available/vacancy-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL сертификат (HTTPS)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## После развёртывания

### 1. Обновите URL в bot.py:
```python
WebAppInfo(url="https://your-domain.com")
```

### 2. Перезапустите бота

### 3. Настройте Web App в BotFather:
1. Откройте @BotFather
2. `/mybots` → ваш бот
3. **Bot Settings** → **Menu Button**
4. Укажите HTTPS URL

---

## Проверка работы

1. Откройте @Recruit2026_bot
2. Нажмите `/start`
3. Нажмите "🎨 Открыть красивое меню"
4. Web App должен открыться

---

## Рекомендации

| Хостинг | Бесплатно | Сложность | Надёжность |
|---------|-----------|-----------|------------|
| PythonAnywhere | ✅ | Средняя | Средняя |
| Railway | ✅ (с лимитами) | Низкая | Хорошая |
| Render | ✅ | Низкая | Хорошая |
| VPS | ❌ (~5$/мес) | Высокая | Отличная |

**Для начала рекомендую Railway или Render** — проще настройка, хорошая надёжность.
