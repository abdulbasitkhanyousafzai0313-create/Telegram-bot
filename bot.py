import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8816202992:AAEemZFEmOXOQPSZt4OVWMePwyLnd2haZ5M'
bot = telebot.TeleBot(API_TOKEN)

user_counts = {}

# 1. پہلا مرحلہ: صرف نئی سبمیشن (تصویر یا ٹیکسٹ) کے لیے
@bot.message_handler(content_types=['photo', 'text'])
def handle_broker_submission(message):
    if message.chat.type in ['group', 'supergroup']:
        # اگر میسج کسی کا ریپلائی ہے تو نیا کلائنٹ نہ بنائیں
        if message.reply_to_message is not None:
            return

        user_id = message.from_user.id
        user_name = message.from_user.username or message.from_user.first_name
        
        if user_id not in user_counts:
            user_counts[user_id] = 0

        if message.content_type == 'photo':
            client_info = message.caption if message.caption else "📸 تصویر (تفصیل درج نہیں)"
        else:
            client_info = message.text

        msg_text = (
            f"📌 **NEW CLIENT SUBMITTED**\n\n"
            f"👤 **Broker:** @{user_name}\n"
            f"📝 **Details:** {client_info}\n\n"
            f"STATUS: ⏳ **Pending**\n"
            f"❓ **سوال:** کیا آپ نے کمپنی کا نمبر بھیج دیا؟ (اس میسج کو Reply کر کے نمبر لکھیں)\n\n"
            f"📊 **Member Total Cleared Clients:** {user_counts[user_id]}"
        )

        bot.reply_to(message, msg_text, parse_mode="Markdown")

# 2. دوسرا مرحلہ: کمپنی کے نمبر کا Reply ملنا
@bot.message_handler(func=lambda message: message.reply_to_message is not None, content_types=['photo', 'text'])
def handle_company_number_reply(message):
    original_msg = message.reply_to_message
    
    if original_msg.from_user.id == bot.get_me().id and "NEW CLIENT SUBMITTED" in original_msg.text:
        
        if message.content_type == 'photo':
            number_sent = message.caption if message.caption else "📸 (تصویر بھیجی گئی)"
        else:
            number_sent = message.text
        
        # وریفکیشن کا بٹن (نیا کارڈ بننے سے روکے گا)
        keyboard = InlineKeyboardMarkup()
        btn_received = InlineKeyboardButton("✅ Received (کلائنٹ نے میسج کر دیا)", callback_data="mark_received")
        keyboard.add(btn_received)

        updated_text = original_msg.text.replace(
            "STATUS: ⏳ **Pending**", 
            "STATUS: 📲 **Number Sent to Client**"
        )
        updated_text = updated_text.replace(
            "❓ **سوال:** کیا آپ نے کمپنی کا نمبر بھیج دیا؟ (اس میسج کو Reply کر کے نمبر لکھیں)",
            f"🔢 **Company WhatsApp Number:** `{number_sent}`\n\n❓ **سوال:** کیا کلائنٹ نے اس نمبر کے WhatsApp پر میسج کر دیا ہے؟"
        )

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=original_msg.message_id,
            text=updated_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        bot.reply_to(message, f"✅ **نمبر درج ہو گیا:** `{number_sent}`", parse_mode="Markdown")

# 3. تیسرا مرحلہ: بٹن دبانے پر کلیئر ہونا (کوئی نیا میسج یا کارڈ نہیں بنے گا)
@bot.callback_query_handler(func=lambda call: call.data == "mark_received")
def handle_final_cleared(call):
    if "STATUS: 📲 **Number Sent to Client**" in call.message.text:
        user_id = call.from_user.id
        user_name = call.from_user.username or call.from_user.first_name

        if user_id not in user_counts:
            user_counts[user_id] = 0
            
        user_counts[user_id] += 1

        updated_text = call.message.text.replace(
            "STATUS: 📲 **Number Sent to Client**", 
            "STATUS: 🎉 **CLIENT CLEAR & VERIFIED**"
        )
        updated_text = updated_text.replace(
            "❓ **سوال:** کیا کلائنٹ نے اس نمبر کے WhatsApp پر میسج کر دیا ہے؟",
            "✅ **Status:** کلائنٹ کا میسج موصول ہو گیا (Received)"
        )
        
        if "📊 **Member Total Cleared Clients:**" in updated_text:
            old_count_str = updated_text.split("📊 **Member Total Cleared Clients:**")[1].strip()
            updated_text = updated_text.replace(
                f"📊 **Member Total Cleared Clients:** {old_count_str}", 
                f"📊 **Member Total Cleared Clients:** {user_counts[user_id]}"
            )

        updated_text += f"\n\n👤 **Cleared By:** @{user_name}"
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=updated_text,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, f"کلائنٹ کلیئر ہو گیا! آپ کا ٹوٹل: {user_counts[user_id]}")
    else:
        bot.answer_callback_query(call.id, "یہ کلائنٹ پہلے ہی کلیئر ہو چکا ہے۔")

bot.infinity_polling()
