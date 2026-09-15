import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8816202992:AAEemZFEmOXQPSZt40VWMePwyLnd2haZ5M'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_broker_submission(message):
    if message.chat.type in ['group', 'supergroup']:
        caption_text = message.caption if message.caption else "کوئی نام/ٹیکسٹ نہیں دیا گیا"
        
        keyboard = InlineKeyboardMarkup()
        btn_received = InlineKeyboardButton("✅ Company Verified (میسج آ گیا)", callback_data="mark_verified")
        keyboard.add(btn_received)
        
        msg_text = (
            f"📌 **NEW CLIENT SUBMITTED**\n\n"
            f"👤 **Broker:** @{message.from_user.username}\n"
            f"📝 **Details:** {caption_text}\n\n"
            f" STATUS: 📤 **Sent to Company**\n"
            f"🔢 **Company Number/Code:** ⏳ Pending (کمپنی Reply میں نمبر بھیجے)"
        )
        
        bot.reply_to(message, msg_text, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'] and m.reply_to_message)
def handle_company_number_reply(message):
    orig_msg = message.reply_to_message.text
    if orig_msg and "NEW CLIENT SUBMITTED" in orig_msg:
        updated_text = orig_msg.replace(
            "🔢 **Company Number/Code:** ⏳ Pending (کمپنی Reply میں نمبر بھیجے)", 
            f"🔢 **Company Number/Code:** `{message.text}`"
        )
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id,
            text=updated_text,
            reply_markup=message.reply_to_message.reply_markup,
            parse_mode="Markdown"
        )
        bot.reply_to(message, "✅ **Number Updated!** بروکر یہ نمبر کلائنٹ کو دے سکتا ہے۔")

@bot.callback_query_handler(func=lambda call: call.data == "mark_verified")
def handle_final_verification(call):
    if "STATUS: 📤 **Sent to Company**" in call.message.text:
        updated_text = call.message.text.replace("STATUS: 📤 **Sent to Company**", "STATUS: 🎉 **CLIENT CONTACTED & VERIFIED**")
        updated_text += f"\n\n✅ **Verified By:** @{call.from_user.username}"
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=updated_text,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "Client Status: VERIFIED!")
    else:
        bot.answer_callback_query(call.id, "یہ کلائنٹ پہلے ہی وریفائی ہو چکا ہے۔")

bot.infinity_polling()
