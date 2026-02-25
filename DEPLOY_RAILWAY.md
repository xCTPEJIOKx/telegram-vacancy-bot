# 🚀 Быстрый деплой на Railway

## Шаг 1: Подготовка файлов

Убедитесь, что у вас есть все файлы:
- ✅ bot.py
- ✅ server.py
- ✅ requirements.txt
- ✅ Procfile
- ✅ runtime.txt
- ✅ .gitignore

## Шаг 2: Загрузка на GitHub

1. Создайте репозиторий на GitHub
2. Загрузите файлы:

```bash
cd C:\Users\hp\telegram-vacancy-bot

# Инициализация git
git init
git add .
git commit -m "Initial commit"

# Подключите ваш репозиторий
git remote add origin https://github.com/YOUR_USERNAME/telegram-vacancy-bot.git
git branch -M main
git push -u origin main
```

## Шаг 3: Развёртывание на Railway

1. Перейдите на https://railway.app
2. Войдите через GitHub
3. Нажмите **New Project**
4. Выберите **Deploy from GitHub repo**
5. Выберите ваш репозиторий `telegram-vacancy-bot`

## Шаг 4: Настройка переменных окружения

В панели Railway:
1. Нажмите на проект
2. Перейдите в **Variables**
3. Добавьте:

```
TELEGRAM_BOT_TOKEN=8546310725:AAGkqmkjFp_DfMFKqA75Q0IXV8xuEU3JaNA
ADMIN_IDS=ваш_id_telegram
```

Чтобы узнать свой ID, отправьте @userinfobot любое сообщение.

## Шаг 5: Получение URL

После развёртывания Railway выдаст URL вида:
```
https://telegram-vacancy-bot-production.up.railway.app
```

## Шаг 6: Обновление bot.py

Измените строку в `bot.py`:

```python
WebAppInfo(url="https://telegram-vacancy-bot-production.up.railway.app")
```

Закоммитьте и отправьте изменения:
```bash
git add bot.py
git commit -m "Update Web App URL"
git push
```

Railway автоматически обновит приложение.

## Шаг 7: Настройка в BotFather

1. Откройте @BotFather
2. `/mybots` → Recruit2026_bot
3. **Bot Settings** → **Menu Button**
4. Отправьте URL вашего Web App
5. Введите название кнопки (например, "🎨 Меню")

## Готово! 🎉

Теперь бот работает 24/7 на Railway!

---

## Устранение проблем

### Бот не отвечает
1. Проверьте логи в Railway (**Logs**)
2. Убедитесь, что токен верный
3. Проверьте переменную ADMIN_IDS

### Web App не открывается
1. Проверьте, что сервер запущен (**Deployments** → статус)
2. Убедитесь, что URL правильный
3. Попробуйте открыть URL в браузере

### Ошибка PORT
Railway автоматически задаёт PORT. Убедитесь, что в server.py есть:
```python
port = int(os.environ.get('PORT', 5000))
```

---

## Мониторинг

- **Логи:** Railway → Проект → Logs
- **Использование:** Railway → Проект → Metrics
- **Перезапуск:** Railway → Проект → Deployments → Redeploy

## Тарифы Railway

- **Бесплатно:** $5 кредитов в месяц (~500 часов работы)
- **Hobby:** $5/месяц — безлимитные часы
- **Pro:** от $20/месяц

Для бота хватит бесплатного тарифа на начальном этапе.
