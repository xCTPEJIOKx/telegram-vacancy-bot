import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import aiosqlite

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Состояния диалога анкеты
NAME, AGE, CITIZENSHIP = range(3)

# Состояния для рассылки
MAILING_TEXT, MAILING_CONFIRM = range(3, 5)

# Администраторы (добавьте свой Telegram ID)
ADMIN_IDS = []

DB_PATH = "vacancy_bot.db"


async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                username TEXT,
                name TEXT,
                age INTEGER,
                citizenship TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                location TEXT,
                salary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Добавление демо-вакансий если пусто
        async with db.execute("SELECT COUNT(*) FROM vacancies") as cursor:
            result = await cursor.fetchone()
            if result[0] == 0:
                await db.executemany(
                    """
                    INSERT INTO vacancies (title, description, location, salary)
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        ("Разнорабочий на склад", "Погрузка/разгрузка, комплектация заказов. Вахта 15/30/45 дней.", "Москва", "от 80 000 ₽"),
                        ("Строитель", "Работа на строительных объектах. Опыт от 1 года.", "Север", "от 120 000 ₽"),
                        ("Работник производства", "Работа на производственной линии. Обучение предоставляется.", "Санкт-Петербург", "от 75 000 ₽"),
                        ("Сотрудник склада", "Приёмка, учёт и отгрузка товара. Вахта 30/60 дней.", "Москва", "от 85 000 ₽"),
                        ("Фасовщик", "Фасовка продукции, маркировка. Без опыта.", "Краснодар", "от 60 000 ₽"),
                        ("Грузчик", "Погрузка/разгрузка грузов. Вахта 45 дней.", "Север", "от 100 000 ₽"),
                    ]
                )
        
        await db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    # Кнопка Web App
    webapp_button = [[
        InlineKeyboardButton(
            "🎨 Открыть красивое меню",
            web_app=WebAppInfo(url="https://vacancy-bot-b9o5.onrender.com")
        )
    ]]
    
    keyboard = [
        [InlineKeyboardButton("📝 Заполнить анкету", callback_data="anketa")],
        [InlineKeyboardButton("💼 Смотреть вакансии", callback_data="vacancies")],
        [InlineKeyboardButton("📍 Локации работы", callback_data="locations")],
        [InlineKeyboardButton("📞 Связаться с нами", callback_data="contacts")],
        [InlineKeyboardButton("❓ Как это работает?", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(webapp_button + keyboard)

    await update.message.reply_text(
        "👋 *Добро пожаловать в VacancyBot!*\n\n"
        "🏗 *Ваш надёжный партнёр по вахтовой работе*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Что мы предлагаем:*\n"
        "• Официальное трудоустройство\n"
        "• Высокая зарплата от 80 000 ₽\n"
        "• Бесплатное проживание\n"
        "• Питание за счёт компании\n"
        "• Вахта от 15 до 60 дней\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎨 *Попробуйте наше новое красивое меню!*\n"
        "Нажмите кнопку ниже 👇\n",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def anketa_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало заполнения анкеты"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📝 **Заполнение анкеты**\n\n"
        "Давайте начнем! Как вас зовут? (ФИО полностью)"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение имени"""
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}!\n\n"
        "Сколько вам лет?"
    )
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение возраста"""
    try:
        age = int(update.message.text)
        if age < 18 or age > 70:
            await update.message.reply_text(
                "Пожалуйста, введите корректный возраст (18-70):\n"
                "Сколько вам лет?"
            )
            return AGE
        context.user_data["age"] = age
        await update.message.reply_text(
            "Отлично! Какое у вас гражданство?"
        )
        return CITIZENSHIP
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите число:\n"
            "Сколько вам лет?"
        )
        return AGE


async def get_citizenship(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение гражданства и сохранение анкеты"""
    citizenship = update.message.text
    context.user_data["citizenship"] = citizenship

    # Сохранение в БД
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO candidates (telegram_id, username, name, age, citizenship)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                update.message.from_user.id,
                update.message.from_user.username,
                context.user_data["name"],
                context.user_data["age"],
                citizenship,
            ),
        )
        await db.commit()

    await update.message.reply_text(
        "✅ **Анкета успешно заполнена!**\n\n"
        f"Данные:\n"
        f"• Имя: {context.user_data['name']}\n"
        f"• Возраст: {context.user_data['age']}\n"
        f"• Гражданство: {citizenship}\n\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n"
        "Вы можете посмотреть доступные вакансии в главном меню."
    )

    # Очистка данных
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена заполнения анкеты"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Заполнение анкеты отменено.\n"
        "Вы можете начать заново, выбрав '📝 Заполнить анкету'."
    )
    return ConversationHandler.END


async def show_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ вакансий"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        send_message = query.edit_message_text
    else:
        send_message = update.message.reply_text

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, title, description, location, salary FROM vacancies ORDER BY created_at DESC"
        ) as cursor:
            vacancies = await cursor.fetchall()

    if not vacancies:
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]
        await send_message(
            "💼 *Вакансии*\n\n"
            "На данный момент нет доступных вакансий.\n"
            "Заполните анкету, и мы сообщим вам о новых предложениях.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # Сохраняем вакансии в context для навигации
    context.user_data['vacancies'] = vacancies
    context.user_data['vacancy_index'] = 0

    # Показ первой вакансии
    return await show_vacancy_page(update, context, 0)


async def show_vacancy_page(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Показ конкретной вакансии"""
    query = update.callback_query if update.callback_query else None
    vacancies = context.user_data.get('vacancies', [])
    
    if not vacancies or index < 0 or index >= len(vacancies):
        return ConversationHandler.END

    vac = vacancies[index]
    
    keyboard = []
    nav_row = []
    
    if index > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"vac_prev_{index}"))
    nav_row.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"vac_next_{index}"))
    keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("📝 Откликнуться", callback_data="anketa")])
    keyboard.append([InlineKeyboardButton("⬅️ К меню", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"💼 *{vac[1]}*\n\n"
        f"📋 *Описание:*\n{vac[2]}\n\n"
        f"📍 *Локация:* {vac[3]}\n"
        f"💰 *Зарплата:* {vac[4]}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"*Вакансия {index + 1} из {len(vacancies)}*"
    )

    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    return ConversationHandler.END


async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ контактов"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📱 Позвонить", url="tel:+79990000000")],
        [InlineKeyboardButton("💬 Написать в Telegram", url="https://t.me/vakansiya_manager")],
        [InlineKeyboardButton("📧 Написать на Email", url="mailto:hr@vakansiya.ru")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📞 *Контакты для связи*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🕐 *Режим работы:*\n"
        "Пн-Пт: 9:00 - 18:00 (МСК)\n"
        "Сб-Вс: 10:00 - 15:00 (МСК)\n\n"
        "📧 Email: `hr@vakansiya.ru`\n"
        "📱 Телефон: `+7 (999) 000-00-00`\n"
        "💬 Менеджер: @vakansiya_manager\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📍 *Офис:*\n"
        "г. Москва, ул. Примерная, д. 1\n\n"
        "Выберите способ связи 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def show_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ локаций"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📍 *Города и объекты работы*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏙 *Москва и МО*\n"
        "  • Склады и логистика\n"
        "  • Строительство\n"
        "  💰 от 80 000 ₽\n\n"
        "🏙 *Санкт-Петербург*\n"
        "  • Портовые работы\n"
        "  • Производство\n"
        "  💰 от 75 000 ₽\n\n"
        "🏙 *Север (Вахта)*\n"
        "  • Нефтегазовые объекты\n"
        "  • Строительство\n"
        "  💰 от 120 000 ₽\n\n"
        "🏙 *Юг (Сезон)*\n"
        "  • Сельское хозяйство\n"
        "  • Курорты\n"
        "  💰 от 60 000 ₽\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Заполните анкету для подбора 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ помощи"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📝 Заполнить анкету", callback_data="anketa")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "❓ *Как это работает?*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ *Заполните анкету*\n"
        "   Нажмите '📝 Заполнить анкету'\n"
        "   Это займёт 1 минуту\n\n"
        "2️⃣ *Дождитесь звонка*\n"
        "   Менеджер свяжется в течение 24 часов\n"
        "   Обсудим детали и подберём вакансию\n\n"
        "3️⃣ *Пройдите собеседование*\n"
        "   Онлайн или в офисе\n"
        "   Оформим документы\n\n"
        "4️⃣ *Выезжайте на объект*\n"
        "   Предоставим жильё и спецодежду\n"
        "   Приступайте к работе!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 *Готовы начать? Заполняйте анкету!*\n👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📝 Заполнить анкету", callback_data="anketa")],
        [InlineKeyboardButton("💼 Смотреть вакансии", callback_data="vacancies")],
        [InlineKeyboardButton("📍 Локации работы", callback_data="locations")],
        [InlineKeyboardButton("📞 Связаться с нами", callback_data="contacts")],
        [InlineKeyboardButton("❓ Как это работает?", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "👋 *VacancyBot — главное меню*\n\n"
        "🏗 *Ваш надёжный партнёр по вахтовой работе*\n\n"
        "Выберите действие 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-меню"""
    if update.message.from_user.id not in ADMIN_IDS:
        return

    keyboard = [
        [InlineKeyboardButton("📋 Все анкеты", callback_data="admin_all")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔧 *Админ-панель*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Выберите действие 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка назад в админ-меню"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Доступ запрещён")
        return

    keyboard = [
        [InlineKeyboardButton("📋 Все анкеты", callback_data="admin_all")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🔧 *Админ-панель*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Выберите действие 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def admin_mailing_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало рассылки"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Доступ запрещён")
        return

    await query.edit_message_text(
        "📢 **Рассылка кандидатам**\n\n"
        "Введите текст сообщения для рассылки всем кандидатам:\n\n"
        "Или отправьте /cancel для отмены"
    )
    return MAILING_TEXT


async def admin_mailing_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение текста рассылки и подтверждение"""
    context.user_data["mailing_text"] = update.message.text

    # Получение количества получателей
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(DISTINCT telegram_id) FROM candidates"
        ) as cursor:
            result = await cursor.fetchone()
            count = result[0] if result else 0

    keyboard = [
        [InlineKeyboardButton("✅ Отправить", callback_data="mailing_send")],
        [InlineKeyboardButton("❌ Отмена", callback_data="mailing_cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📢 **Подтверждение рассылки**\n\n"
        f"Текст сообщения:\n_{update.message.text}_\n\n"
        f"Получателей: {count}\n\n"
        "Отправить сообщение?",
        reply_markup=reply_markup,
    )
    return MAILING_CONFIRM


async def admin_mailing_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка рассылки"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Доступ запрещён")
        return

    text = context.user_data.get("mailing_text", "")
    if not text:
        await query.edit_message_text("❌ Ошибка: текст рассылки не найден")
        context.user_data.clear()
        return ConversationHandler.END

    # Получение всех уникальных telegram_id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT DISTINCT telegram_id, username FROM candidates"
        ) as cursor:
            candidates = await cursor.fetchall()

    success_count = 0
    fail_count = 0

    await query.edit_message_text(f"📢 Рассылка началась...\n0/{len(candidates)}")

    for telegram_id, username in candidates:
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=f"📢 **Важное сообщение от работодателя**\n\n{text}",
                parse_mode="Markdown",
            )
            success_count += 1
        except Exception as e:
            logger.warning(f"Не удалось отправить пользователю {telegram_id}: {e}")
            fail_count += 1

        # Обновление прогресса каждые 10 сообщений
        if success_count % 10 == 0:
            try:
                await query.edit_message_text(
                    f"📢 Рассылка...\n{success_count}/{len(candidates)}"
                )
            except:
                pass

    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=f"✅ **Рассылка завершена**\n\n"
        f"Успешно: {success_count}\n"
        f"Не удалось: {fail_count}",
    )

    context.user_data.clear()
    return ConversationHandler.END


async def admin_mailing_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена рассылки"""
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    await query.edit_message_text("❌ Рассылка отменена")
    return ConversationHandler.END


async def admin_show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ всех анкет администратору"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Доступ запрещён")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT name, age, citizenship, username, created_at FROM candidates ORDER BY created_at DESC"
        ) as cursor:
            candidates = await cursor.fetchall()

    if not candidates:
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="admin_menu")]]
        await query.edit_message_text(
            "📭 *Анкет пока нет*\n\n"
            "Как только кандидаты заполнят анкеты, они появятся здесь.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return

    # Показ первых 10 анкет
    text = "📋 *Все анкеты (последние 10):*\n\n"
    for i, cand in enumerate(candidates[:10], 1):
        text += f"*{i}.* 👤 `{cand[0]}`\n"
        text += f"  ├ Возраст: `{cand[1]}`\n"
        text += f"  ├ Гражданство: `{cand[2]}`\n"
        text += f"  ├ Telegram: @{cand[3] if cand[3] else 'нет'}\n"
        text += f"  └ Дата: `{cand[4]}`\n\n"

    if len(candidates) > 10:
        text += f"... и ещё {len(candidates) - 10} анкет\n"

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="admin_menu")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ статистики"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Доступ запрещён")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM candidates") as cursor:
            result = await cursor.fetchone()
            total_candidates = result[0] if result else 0
        
        async with db.execute("SELECT COUNT(*) FROM vacancies") as cursor:
            result = await cursor.fetchone()
            total_vacancies = result[0] if result else 0
        
        async with db.execute("SELECT citizenship, COUNT(*) FROM candidates GROUP BY citizenship") as cursor:
            citizenship_stats = await cursor.fetchall()

    text = "📊 *Статистика бота*\n\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"👥 *Всего анкет:* `{total_candidates}`\n"
    text += f"💼 *Вакансий:* `{total_vacancies}`\n\n"
    
    if citizenship_stats:
        text += "*Гражданство:*\n"
        for cit, count in citizenship_stats:
            text += f"  • {cit}: `{count}`\n"

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="admin_menu")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()

    # Обработка навигации по вакансиям
    if query.data.startswith("vac_prev_"):
        index = int(query.data.split("_")[-1])
        return await show_vacancy_page(update, context, index - 1)
    elif query.data.startswith("vac_next_"):
        index = int(query.data.split("_")[-1])
        return await show_vacancy_page(update, context, index + 1)

    if query.data == "anketa":
        return await anketa_start(update, context)
    elif query.data == "vacancies":
        return await show_vacancies(update, context)
    elif query.data == "contacts":
        return await show_contacts(update, context)
    elif query.data == "locations":
        return await show_locations(update, context)
    elif query.data == "help":
        return await show_help(update, context)
    elif query.data == "back_to_main":
        return await back_to_main(update, context)
    elif query.data == "admin_menu":
        return await admin_menu_callback(update, context)
    elif query.data == "admin_all":
        return await admin_show_all(update, context)
    elif query.data == "admin_stats":
        return await admin_stats(update, context)
    elif query.data == "admin_mailing":
        return await admin_mailing_start(update, context)
    elif query.data == "mailing_send":
        return await admin_mailing_send(update, context)
    elif query.data == "mailing_cancel":
        return await admin_mailing_cancel(update, context)

    return ConversationHandler.END


async def post_init(application):
    """Инициализация после запуска"""
    await init_db()
    print("🤖 Бот запущен...")


def run_bot():
    """Запуск бота"""
    # Загрузка переменных из .env
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Не найден токен бота! Установите переменную TELEGRAM_BOT_TOKEN")
        return

    # Добавление админов из переменных окружения
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        global ADMIN_IDS
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",")]

    # Создание и запуск приложения
    async def main():
        application = Application.builder().token(token).post_init(post_init).build()

        # Конвейер анкеты
        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(anketa_start, pattern="^anketa$"),
            ],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
                CITIZENSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_citizenship)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            per_message=False,
        )

        # Конвейер рассылки
        mailing_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(admin_mailing_start, pattern="^admin_mailing$"),
            ],
            states={
                MAILING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_mailing_text)],
                MAILING_CONFIRM: [CallbackQueryHandler(admin_mailing_send, pattern="^mailing_send$")],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            per_message=False,
        )

        # Обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_menu))
        application.add_handler(conv_handler)
        application.add_handler(mailing_handler)
        application.add_handler(CallbackQueryHandler(button_handler))

        # Запуск
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        print("[OK] Bot is running. Press Ctrl+C to stop.")
        
        # Держим бота запущенным
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await application.stop()
            await application.shutdown()

    # Создаём новый event loop для Python 3.14
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен.")
    finally:
        loop.close()


if __name__ == "__main__":
    run_bot()
