import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8816202992:AAEemZFEmOXOQPSZt4OVWMePwyLnd2haZ5M'
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
            f"STATUS: 🚢 **Sent to Company**\n"
            f"🔢 **Company Number/Code:** ⏳ Pending (میں نمبر بھیجے کمپنی Reply)"
        )

        bot.reply_to(message, msg_text, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_company_number_reply(message):
    original_msg = message.reply_to_message
    if original_msg.from_user.id == bot.get_me().id and "NEW CLIENT SUBMITTED" in original_msg.text:
        number_sent = message.text
        
        updated_text = original_msg.text.replace(
            "⏳ Pending (میں نمبر بھیجے کمپنی Reply)", 
            f"✅ {number_sent}"
        )

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=original_msg.message_id,
            text=updated_text,
            reply_markup=original_msg.reply_markup,
            parse_mode="Markdown"
        )
        
        bot.reply_to(message, "✅ **Number Updated!** بروکر یہ نمبر کلائنٹ کو دے سکتا ہے۔")

@bot.callback_query_handler(func=lambda call: call.data == "mark_verified")
def handle_final_verification(call):
    if "STATUS: 🚢 **Sent to Company**" in call.message.text:
        updated_text = call.message.text.replace("STATUS: 🚢 **Sent to Company**", "STATUS: ✅ **VERIFIED & CLOSED**")
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
