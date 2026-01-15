import json
import os
import telebot

owner = 87560475
web_bot = "7938479990:AAHzsQMWH_Pi7pGQFRKJJ0tSS05c15vcG_A"

bot = telebot.TeleBot(web_bot)

def load_users():
    if os.path.exists('user.json'):
        with open('user.json', 'r') as f:
            return json.load(f)
    return {}

def save_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = True
        with open('user.json', 'w') as f:
            json.dump(users, f)

def get_main_markup(user_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    btn1 = telebot.types.InlineKeyboardButton("🔍 OSINT", callback_data='osint_menu')
    btn2 = telebot.types.InlineKeyboardButton("💣 Botnet", callback_data='botnet_menu')
    btn3 = telebot.types.InlineKeyboardButton("🤖 AI", callback_data='ai_menu')
    btn4 = telebot.types.InlineKeyboardButton("🧧 Profile", callback_data='profile')
    btn5 = telebot.types.InlineKeyboardButton("💲 Crypto", callback_data='crypto')
    btn6 = telebot.types.InlineKeyboardButton("💳 Card", callback_data='card')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    if user_id == owner:
        btn7 = telebot.types.InlineKeyboardButton("💻 Admin", callback_data='admin')
        markup.add(btn7)
    return markup

def get_osint_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    btn1 = telebot.types.InlineKeyboardButton("📱 Телефон", callback_data='phone_osint')
    btn2 = telebot.types.InlineKeyboardButton("📧 Почта", callback_data='email_osint')
    btn3 = telebot.types.InlineKeyboardButton("👤 ФИО", callback_data='name_osint')
    btn4 = telebot.types.InlineKeyboardButton("📄 ИНН", callback_data='inn_osint')
    btn5 = telebot.types.InlineKeyboardButton("🆔 СНИЛС", callback_data='snils_osint')
    btn6 = telebot.types.InlineKeyboardButton("🌐 IP", callback_data='ip_osint')
    btn7 = telebot.types.InlineKeyboardButton("🚗 Номер", callback_data='plate_osint')
    btn8 = telebot.types.InlineKeyboardButton("🔧 VIN", callback_data='vin_osint')
    btn9 = telebot.types.InlineKeyboardButton("📱 Соцсети", callback_data='social_osint')
    btn10 = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn7, btn8, btn9)
    markup.add(btn10)
    return markup

def get_botnet_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    btn1 = telebot.types.InlineKeyboardButton("👤 Аккаунт", callback_data='account_botnet')
    btn2 = telebot.types.InlineKeyboardButton("👥 Группу", callback_data='group_botnet')
    btn3 = telebot.types.InlineKeyboardButton("📢 Канал", callback_data='channel_botnet')
    btn4 = telebot.types.InlineKeyboardButton("💬 Форум", callback_data='forum_botnet')
    btn5 = telebot.types.InlineKeyboardButton("🔐 Сессию", callback_data='session_botnet')
    btn6 = telebot.types.InlineKeyboardButton("➕ Добавить", callback_data='add_botnet')
    btn7 = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn7)
    return markup

def get_ai_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    btn1 = telebot.types.InlineKeyboardButton("🌀 Serenity", callback_data='serenity_ai')
    btn2 = telebot.types.InlineKeyboardButton("🤖 Open AI", callback_data='openai_ai')
    btn3 = telebot.types.InlineKeyboardButton("🧠 Anthropic", callback_data='anthropic_ai')
    btn4 = telebot.types.InlineKeyboardButton("🔍 DeepSeek", callback_data='deepseek_ai')
    btn5 = telebot.types.InlineKeyboardButton("🌐 Yandex", callback_data='yandex_ai')
    btn6 = telebot.types.InlineKeyboardButton("🔵 Google", callback_data='google_ai')
    btn7 = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='main_menu')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn7)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user.id)
    video = open('onion.mp4', 'rb')
    caption = """<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>"""
    markup = get_main_markup(message.from_user.id)
    bot.send_video(message.chat.id, video, caption=caption, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'admin' and call.from_user.id != owner:
        bot.answer_callback_query(call.id, "Доступ запрещен")
        return

    if call.data == 'osint_menu':
        new_caption = "<b><i>Выберите нужную вам функцию OSINT поиска.</i></b>"
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=new_caption,
                parse_mode='HTML',
                reply_markup=get_osint_markup()
            )
        except:
            pass
        bot.answer_callback_query(call.id)
        return

    if call.data == 'botnet_menu':
        new_caption = "<b><i>Выберите функцию сноса которая вам нужна.</i></b>"
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=new_caption,
                parse_mode='HTML',
                reply_markup=get_botnet_markup()
            )
        except:
            pass
        bot.answer_callback_query(call.id)
        return

    if call.data == 'ai_menu':
        new_caption = "<b><i>Выберите нужную для вас модель.</i></b>"
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=new_caption,
                parse_mode='HTML',
                reply_markup=get_ai_markup()
            )
        except:
            pass
        bot.answer_callback_query(call.id)
        return

    if call.data == 'main_menu':
        original_caption = """<b><i>
Web - AI: Telegram - бот в котором собраны все необходимые инструменты для osint'еров, pentest'еров, snos'еров и простых пользователей Telegram.

Желаю удачи в использовании!
</i></b>"""
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=original_caption,
                parse_mode='HTML',
                reply_markup=get_main_markup(call.from_user.id)
            )
        except:
            pass
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "В разработке")

if __name__ == "__main__":
    bot.infinity_polling()