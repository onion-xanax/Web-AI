import json
import os
import telebot
import time

owner = 87560475
web_bot = "7938479990:AAHzsQMWH_Pi7pGQFRKJJ0tSS05c15vcG_A"

bot = telebot.TeleBot(web_bot, threaded=False)

print("🔄 Установка завершена! Запускаю бота...")

files = ['user.json', 'sub.json', 'ban.json', 'ref.json']
for file in files:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def save_user(user_id):
    users = load_json('user.json')
    if str(user_id) not in users:
        users[str(user_id)] = True
        save_json('user.json', users)

def get_profile_text(user_data):
    users = load_json('user.json')
    bans = load_json('ban.json')
    subs = load_json('sub.json')
    refs = load_json('ref.json')
    
    user_ref_count = 0
    for ref_list in refs.values():
        if str(user_data.id) in ref_list:
            user_ref_count = len([uid for uid in ref_list if uid == str(user_data.id)])
            break
    
    return f"""<b><i>Информация о вашем профиле и статистика бота.</i></b>

<b>Ник нейм</b>: <code>{user_data.first_name or 'Не указан'}</code>
<b>Юзернейм</b>: <code>@{user_data.username if user_data.username else 'Не указан'}</code>
<b>ID</b>: <code>{user_data.id}</code>

<b>Кол-во запросов OSINT</b>: <code>0</code>
<b>Кол-во запросов Botnet</b>: <code>0</code>
<b>Кол-во запросов AI</b>: <code>0</code>

<b>Рефералов</b>: <code>{user_ref_count}</code>
<b>Подписка</b>: <code>{"активна" if str(user_data.id) in subs else "не активна"}</code>
<b>Баланс</b>: <code>0</code>

<b>Кол-во пользователей бота</b>: <code>{len(users)}</code>
<b>Кол-во купивших подписку</b>: <code>{len(subs)}</code>
<b>Кол-во забаненых админом</b>: <code>{len(bans)}</code>

<b>Реферальная ссылка</b>: <code>https://t.me/your_bot?start={user_data.id}</code>"""

def get_main_markup(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    row1 = [
        telebot.types.InlineKeyboardButton("🔍 OSINT", callback_data='osint_menu'),
        telebot.types.InlineKeyboardButton("💣 Botnet", callback_data='botnet_menu'),
        telebot.types.InlineKeyboardButton("🤖 AI", callback_data='ai_menu')
    ]
    row2 = [
        telebot.types.InlineKeyboardButton("🧧 Profile", callback_data='profile_menu'),
        telebot.types.InlineKeyboardButton("💲 Crypto", callback_data='crypto'),
        telebot.types.InlineKeyboardButton("💳 Card", callback_data='card')
    ]
    markup.row(*row1)
    markup.row(*row2)
    
    if user_id == owner:
        row3 = [telebot.types.InlineKeyboardButton("💻 Admin", callback_data='admin')]
        markup.row(*row3)
    
    return markup

def get_crypto_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    
    row1 = [
        telebot.types.InlineKeyboardButton("1 неделя", url="https://t.me/send?start=IVuF0HpIaXXu"),
        telebot.types.InlineKeyboardButton("1 месяц", url="https://t.me/send?start=IVHvxstS6a4v"),
        telebot.types.InlineKeyboardButton("2 месяца", url="https://t.me/send?start=IVoeSkLDfpBh")
    ]
    
    row2 = [
        telebot.types.InlineKeyboardButton("4 месяца", url="https://t.me/send?start=IVvDkRjHVyTc"),
        telebot.types.InlineKeyboardButton("1 год", url="https://t.me/send?start=IVI53FmncjJz"),
        telebot.types.InlineKeyboardButton("Навсгда", url="https://t.me/send?start=IVntCWhUqzm1")
    ]
    
    row3 = [
        telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')
    ]
    
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    
    return markup

def get_card_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    
    row1 = [
        telebot.types.InlineKeyboardButton("🪪Оплатить", url="https://t.me/root_exorcist"),
        telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')
    ]
    
    markup.row(*row1)
    
    return markup

def get_osint_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row1 = [
        telebot.types.InlineKeyboardButton("📱 Телефон", callback_data='phone_osint'),
        telebot.types.InlineKeyboardButton("📧 Почта", callback_data='email_osint'),
        telebot.types.InlineKeyboardButton("👤 ФИО", callback_data='name_osint')
    ]
    row2 = [
        telebot.types.InlineKeyboardButton("📄 ИНН", callback_data='inn_osint'),
        telebot.types.InlineKeyboardButton("🆔 СНИЛС", callback_data='snils_osint'),
        telebot.types.InlineKeyboardButton("🌐 IP", callback_data='ip_osint')
    ]
    row3 = [
        telebot.types.InlineKeyboardButton("🚗 Номер", callback_data='plate_osint'),
        telebot.types.InlineKeyboardButton("🔧 VIN", callback_data='vin_osint'),
        telebot.types.InlineKeyboardButton("📱 Соцсети", callback_data='social_osint')
    ]
    row4 = [telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]
    
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    markup.row(*row4)
    
    return markup

def get_botnet_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row1 = [
        telebot.types.InlineKeyboardButton("👤 Аккаунт", callback_data='account_botnet'),
        telebot.types.InlineKeyboardButton("👥 Группу", callback_data='group_botnet'),
        telebot.types.InlineKeyboardButton("📢 Канал", callback_data='channel_botnet')
    ]
    row2 = [
        telebot.types.InlineKeyboardButton("💬 Форум", callback_data='forum_botnet'),
        telebot.types.InlineKeyboardButton("🔐 Сессию", callback_data='session_botnet'),
        telebot.types.InlineKeyboardButton("➕ Добавить", callback_data='add_botnet')
    ]
    row3 = [telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]
    
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    
    return markup

def get_ai_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row1 = [
        telebot.types.InlineKeyboardButton("🌀 Serenity", callback_data='serenity_ai'),
        telebot.types.InlineKeyboardButton("🤖 Open AI", callback_data='openai_ai'),
        telebot.types.InlineKeyboardButton("🧠 Anthropic", callback_data='anthropic_ai')
    ]
    row2 = [
        telebot.types.InlineKeyboardButton("🔍 DeepSeek", callback_data='deepseek_ai'),
        telebot.types.InlineKeyboardButton("🌐 Yandex", callback_data='yandex_ai'),
        telebot.types.InlineKeyboardButton("🔵 Google", callback_data='google_ai')
    ]
    row3 = [telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]
    
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    
    return markup

def get_profile_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row1 = [
        telebot.types.InlineKeyboardButton("🔄 Обновить", callback_data='refresh_profile'),
        telebot.types.InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')
    ]
    markup.row(*row1)
    return markup

def get_admin_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row1 = [
        telebot.types.InlineKeyboardButton("📊 Статистика", callback_data='admin_stats'),
        telebot.types.InlineKeyboardButton("📤 Рассылка", callback_data='admin_broadcast')
    ]
    row2 = [telebot.types.InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')]
    markup.row(*row1)
    markup.row(*row2)
    return markup

last_video_message = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user.id)
    
    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        refs = load_json('ref.json')
        if ref_id != str(message.from_user.id):
            if ref_id not in refs:
                refs[ref_id] = []
            if str(message.from_user.id) not in refs[ref_id]:
                refs[ref_id].append(str(message.from_user.id))
                save_json('ref.json', refs)
    
    try:
        with open('onion.mp4', 'rb') as video:
            sent_message = bot.send_video(
                message.chat.id, 
                video, 
                caption="""<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>""", 
                parse_mode='HTML', 
                reply_markup=get_main_markup(message.from_user.id)
            )
            last_video_message[message.chat.id] = sent_message.message_id
        
        print(f"✅ Сообщение отправлено пользователю {message.from_user.id}")
    except Exception as e:
        print(f"❌ Ошибка отправки видео: {e}")
        sent_message = bot.send_message(
            message.chat.id,
            """<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>""",
            parse_mode='HTML',
            reply_markup=get_main_markup(message.from_user.id)
        )
        last_video_message[message.chat.id] = sent_message.message_id

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    print(f"📞 Получен callback: {call.data} от пользователя {call.from_user.id}")
    
    try:
        if call.data == 'admin' and call.from_user.id != owner:
            bot.answer_callback_query(call.id, "Доступ запрещен", show_alert=True)
            return

        if call.data == 'admin' and call.from_user.id == owner:
            admin_text = "<b><i>Панель администратора</i></b>"
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=admin_text,
                    parse_mode='HTML',
                    reply_markup=get_admin_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    admin_text,
                    parse_mode='HTML',
                    reply_markup=get_admin_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'crypto':
            crypto_text = "<b><i>Выберите оптимальный вариант подписки.</i></b>"
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=crypto_text,
                    parse_mode='HTML',
                    reply_markup=get_crypto_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    crypto_text,
                    parse_mode='HTML',
                    reply_markup=get_crypto_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'card':
            card_text = """<b><i>
Для оплаты банковской картой, пожалуйста, свяжитесь с создателем бота — он предоставит актуальные реквизиты для перевода.
Мы принимаем платежи из большинства российских банков, включая:
• Т‑Банк
• СберБанк
• Озон Банк
• Альфа‑Банк
</i></b>"""
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=card_text,
                    parse_mode='HTML',
                    reply_markup=get_card_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    card_text,
                    parse_mode='HTML',
                    reply_markup=get_card_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'osint_menu':
            osint_text = "<b><i>Выберите нужную вам функцию OSINT поиска.</i></b>"
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=osint_text,
                    parse_mode='HTML',
                    reply_markup=get_osint_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    osint_text,
                    parse_mode='HTML',
                    reply_markup=get_osint_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'botnet_menu':
            botnet_text = "<b><i>Выберите функцию сноса которая вам нужна.</i></b>"
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=botnet_text,
                    parse_mode='HTML',
                    reply_markup=get_botnet_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    botnet_text,
                    parse_mode='HTML',
                    reply_markup=get_botnet_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'ai_menu':
            ai_text = "<b><i>Выберите нужную для вас модель.</i></b>"
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=ai_text,
                    parse_mode='HTML',
                    reply_markup=get_ai_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    ai_text,
                    parse_mode='HTML',
                    reply_markup=get_ai_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'profile_menu':
            profile_text = get_profile_text(call.from_user)
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=profile_text,
                    parse_mode='HTML',
                    reply_markup=get_profile_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    profile_text,
                    parse_mode='HTML',
                    reply_markup=get_profile_markup()
                )
            bot.answer_callback_query(call.id)

        elif call.data == 'refresh_profile':
            profile_text = get_profile_text(call.from_user)
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=profile_text,
                    parse_mode='HTML',
                    reply_markup=get_profile_markup()
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    profile_text,
                    parse_mode='HTML',
                    reply_markup=get_profile_markup()
                )
            bot.answer_callback_query(call.id, "✅ Статистика обновлена")

        elif call.data == 'main_menu':
            main_text = """<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>"""
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=main_text,
                    parse_mode='HTML',
                    reply_markup=get_main_markup(call.from_user.id)
                )
            except:
                bot.send_message(
                    call.message.chat.id,
                    main_text,
                    parse_mode='HTML',
                    reply_markup=get_main_markup(call.from_user.id)
                )
            bot.answer_callback_query(call.id)

        else:
            bot.answer_callback_query(call.id, "🔄 В разработке...")
            
    except Exception as e:
        print(f"❌ Ошибка обработки callback: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ Произошла ошибка")
        except:
            pass

print("=" * 50)
print("🤖 БОТ УСПЕШНО ЗАПУЩЕН!")
print("=" * 50)
print("📱 Откройте Telegram и напишите /start вашему боту")
print("🎬 onion.mp4 будет всегда прикреплен к меню")
print("⏳ Бот работает пока открыта эта вкладка Colab")
print("=" * 50)

try:
    bot.remove_webhook()
    time.sleep(1)
    
    print("🔄 Начинаю опрос сервера Telegram...")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"⚠️ Перезапуск после ошибки: {e}")
            time.sleep(5)
            continue
            
except KeyboardInterrupt:
    print("\n⏹️ Бот остановлен пользователем")
except Exception as e:
    print(f"\n❌ Критическая ошибка: {e}")
