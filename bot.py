import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8816202992:AAEemZFEmOXOQPSZt4OVWMePwyLnd2haZ5M'
bot = telebot.TeleBot(API_TOKEN)

# ہر ممبر کے الگ ریکارڈ گننے کے لیے
user_counts = {}

# 1. پہلا مرحلہ: تصویر (Photo) یا متن (Text) دونوں صورتوں میں سبمٹ ہونا
@bot.message_handler(content_types=['photo', 'text'])
def handle_broker_submission(message):
    if message.chat.type in ['group', 'supergroup']:
        # اگر یہ کسی بوٹ کے میسج کا ریپلائی ہے تو اسے یہاں پروسیس نہ کریں
        if message.reply_to_message is not None:
            return

        user_id = message.from_user.id
        user_name = message.from_user.username or message.from_user.first_name
        
        if user_id not in user_counts:
            user_counts[user_id] = 0

        # اگر تصویر ہے تو کیپشن لے لیں، اگر صرف متن ہے تو میسج کا متن لے لیں
        if message.content_type == 'photo':
            client_info = message.caption if message.caption else "📸 تصویر (کوئی اضافی تفصیل نہیں)"
        else:
            client_info = message.text

        msg_text = (
            f"📌 **NEW CLIENT SUBMITTED**\n\n"
            f"👤 **Broker:** @{user_name}\n"
            f"📝 **Details:** {client_info}\n\n"
            f"STATUS: ⏳ **Pending**\n"
            f"❓ **سوال:** کیا آپ نے کمپنی کا نمبر بھیج دیا ہے؟ (اس میسج کو Reply کر کے نمبر یا تفصیل لکھیں)\n\n"
            f"📊 **Member Total Cleared Clients:** {user_counts[user_id]}"
        )

        bot.reply_to(message, msg_text, parse_mode="Markdown")

# 2. دوسرا مرحلہ: کمپنی کا نمبر یا تصویر/ٹیکسٹ Reply میں موصول ہونا
@bot.message_handler(func=lambda message: message.reply_to_message is not None, content_types=['photo', 'text'])
def handle_company_number_reply(message):
    original_msg = message.reply_to_message
    
    # چیک کریں کہ بوٹ کے ہی بھیجے گئے پینڈنگ میسج پر ریپلائی کیا گیا ہے
    if original_msg.from_user.id == bot.get_me().id and "NEW CLIENT SUBMITTED" in original_msg.text:
        
        if message.content_type == 'photo':
            number_sent = message.caption if message.caption else "📸 (تصویر بھیجی گئی ہے)"
        else:
            number_sent = message.text
        
        # WhatsApp Received کے لیے بٹن
        keyboard = InlineKeyboardMarkup()
        btn_received = InlineKeyboardButton("✅ WhatsApp Received (میسج ہو گیا)", callback_data="mark_received")
        keyboard.add(btn_received)

        # کارڈ اپ ڈیٹ کرنا
        updated_text = original_msg.text.replace(
            "STATUS: ⏳ **Pending**", 
            "STATUS: 📲 **Number Sent to Client**"
        )
        updated_text = updated_text.replace(
            "❓ **سوال:** کیا آپ نے کمپنی کا نمبر بھیج دیا ہے؟ (اس میسج کو Reply کر کے نمبر یا تفصیل لکھیں)",
            f"🔢 **Company Number/Info:** `{number_sent}`\n\n❓ **سوال:** کیا کلائنٹ نے اس نمبر کے WhatsApp پر میسج کر دیا ہے (Received)؟"
        )

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=original_msg.message_id,
            text=updated_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        bot.reply_to(message, f"✅ **نمبر/تفصیل درج ہو گئی:** `{number_sent}`\nیہ کلائنٹ کو بھیج دیا گیا ہے۔ WhatsApp میسج موصول ہونے پر **WhatsApp Received** بٹن دبائیں۔", parse_mode="Markdown")

# 3. تیسرا مرحلہ: WhatsApp Received اور کلائنٹ Clear ہونا
@bot.callback_query_handler(func=lambda call: call.data == "mark_received")
def handle_final_cleared(call):
    if "STATUS: 📲 **Number Sent to Client**" in call.message.text:
        user_id = call.from_user.id
        user_name = call.from_user.username or call.from_user.first_name

        if user_id not in user_counts:
            user_counts[user_id] = 0
            
        # اس مخصوص ممبر کا کاؤنٹ 1 بڑھائیں
        user_counts[user_id] += 1

        updated_text = call.message.text.replace(
            "STATUS: 📲 **Number Sent to Client**", 
            "STATUS: 🎉 **CLIENT CLEAR & VERIFIED**"
        )
        updated_text = updated_text.replace(
            "❓ **سوال:** کیا کلائنٹ نے اس نمبر کے WhatsApp پر میسج کر دیا ہے (Received)؟",
            "✅ **Status:** کلائنٹ نے WhatsApp پر میسج کر دیا ہے (Received)"
        )
        
        # ممبر کا کاؤنٹ اپ ڈیٹ کرنا
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
        bot.answer_callback_query(call.id, f"کلائنٹ کلیئر ہو گیا! آپ کے ٹوٹل کلیئر کلائنٹس: {user_counts[user_id]}")
    else:
        bot.answer_callback_query(call.id, "یہ کلائنٹ پہلے ہی کلیئر ہو چکا ہے۔")

bot.infinity_polling()
