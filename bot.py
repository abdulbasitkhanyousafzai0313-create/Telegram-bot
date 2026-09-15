import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
ADMIN_ID = 123456789  # اپنا ٹیلیگرام چیٹ آئی ڈی یہاں لکھیں

bot = telebot.TeleBot(API_TOKEN)

# کسٹمر کا ڈیٹا عارضی طور پر محفوظ کرنے کے لیے Dictionary
user_data = {}
cleared_clients_count = 0

# 1. Start Command (/start)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! بوٹ سٹارٹ ہو گیا ہے۔\n\nبرائے مہربانی **کسٹمر کی ڈیٹیل (نام یا معلومات)** لکھ کر بھیجیں۔")

# 2. Clear Command (/clear) - صرف ایڈمن کے لیے
@bot.message_handler(commands=['clear'])
def clear_data(message):
    global cleared_clients_count
    if message.from_user.id == ADMIN_ID:
        cleared_clients_count = 0
        bot.reply_to(message, "تمام ڈیٹا اور کاؤنٹر کلیئر کر دیا گیا ہے!")
    else:
        bot.reply_to(message, "آپ کے پاس اس کمانڈ کا اختیار نہیں ہے۔")

# 3. Step 2 & 3: کسٹمر ڈیٹیل اور کمپنی نمبر کا فلو
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    # اگر یوزر کا اگلا اسٹیپ کمپنی نمبر دینا ہے
    if chat_id in user_data and user_data[chat_id].get('status') == 'waiting_for_company_num':
        user_data[chat_id]['company_num'] = text
        user_data[chat_id]['status'] = 'completed'

        # تیسرا اسٹیپ: Received کا بٹن بنانا
        markup = InlineKeyboardMarkup()
        btn_received = InlineKeyboardButton("Received", callback_data=f"received_{chat_id}")
        markup.add(btn_received)

        summary_msg = (
            f"📌 **NEW CLIENT SUBMITTED**\n\n"
            f"👤 **Details:** {user_data[chat_id]['details']}\n"
            f"🏢 **Company Number:** {text}\n"
            f"⏳ **Status:** Pending"
        )
        bot.send_message(chat_id, summary_msg, reply_markup=markup, parse_mode="Markdown")

    else:
        # پہلا اسٹیپ: کسٹمر کی ڈیٹیل سیو کرنا
        user_data[chat_id] = {
            'details': text,
            'status': 'waiting_for_company_num'
        }
        
        # دوسرا اسٹیپ: کمپنی نمبر مانگنے کا میسج
        bot.send_message(
            chat_id, 
            f"✅ کسٹمر ڈیٹیل محفوظ ہو گئی: **{text}**\n\nاب **کمپنی کا نمبر** لکھ کر بھیجیں:",
            parse_mode="Markdown"
        )

# 4. Received Button Handler (کاؤنٹ کرنے کے لیے)
@bot.callback_query_handler(func=lambda call: call.data.startswith('received_'))
def handle_received_button(call):
    global cleared_clients_count
    
    # کاؤنٹر میں 1 کا اضافہ
    cleared_clients_count += 1
    
    # میسج اپڈیٹ کرنا
    updated_text = call.message.text.replace("Status: Pending", "Status: Approved ✅")
    updated_text += f"\n\n📊 **Total Cleared Clients:** {cleared_clients_count}"
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=updated_text,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, text="Client Received and Counted!")

# بوٹ کو ہر وقت چالو رکھنے کے لیے
bot.infinity_polling()
