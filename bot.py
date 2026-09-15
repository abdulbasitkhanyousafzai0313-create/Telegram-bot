import re
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

from config import BOT_TOKEN, ADMIN_IDS
import db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Menu button labels ----------
BTN_NEW = "🆕 Naya Client"
BTN_ADDNUM = "📞 Number Add Karo"
BTN_PROOF = "📷 Proof Bhejo"
BTN_MYCLIENTS = "📋 Mere Clients"
BTN_STATS = "📊 Mera Stats"

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [BTN_NEW, BTN_ADDNUM],
        [BTN_PROOF, BTN_MYCLIENTS],
        [BTN_STATS],
    ],
    resize_keyboard=True,
)

# Conversation states
NAME, PHONE = range(2)
ADDNUM_ID, ADDNUM_NUMBER = range(2, 4)
PROOF_ID, PROOF_WAIT = range(4, 6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    await update.message.reply_text(
        "Namaste! Main aapka client-tracking bot hoon.\n\n"
        "Niche diye buttons se kaam karo, ya ye commands bhi use kar sakte ho:\n"
        "/newclient /addnumber /proof /myclients /mystats",
        reply_markup=MAIN_MENU,
    )


# ============ /newclient conversation ============
async def newclient_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Client ka naam bhejo:")
    return NAME


async def newclient_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["client_name"] = update.message.text.strip()
    await update.message.reply_text("Ab client ka phone number bhejo:")
    return PHONE


async def newclient_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    phone = update.message.text.strip()
    name = context.user_data.get("client_name")
    client_id = db.add_client(user.id, user.first_name, name, phone)
    await update.message.reply_text(
        f"✅ Client save ho gaya.\n"
        f"Client ID: {client_id}\n"
        f"Naam: {name}\n"
        f"Phone: {phone}\n\n"
        f"Jab company se numaindey ka number mile, '{BTN_ADDNUM}' button dabao "
        f"aur Client ID {client_id} bhejo.",
        reply_markup=MAIN_MENU,
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel ho gaya.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


# ============ /addnumber conversation ============
async def addnumber_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Agar command ke saath directly ID aur number diya ho: /addnumber 1 9876543210
    if context.args and len(context.args) >= 2:
        try:
            client_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Client ID number mein hona chahiye.")
            return ConversationHandler.END
        rep_number = context.args[1]
        client = db.get_client(client_id, user.id)
        if not client:
            await update.message.reply_text("Ye client ID aapke account mein nahi mili.")
            return ConversationHandler.END
        db.add_rep_number(client_id, user.id, rep_number)
        await update.message.reply_text(
            f"✅ Number save ho gaya.\n\n"
            f"Ye number client ({client['client_name']}) ko bhej do:\n"
            f"📞 {rep_number}\n\n"
            f"Proof aane par '{BTN_PROOF}' button dabao.",
            reply_markup=MAIN_MENU,
        )
        return ConversationHandler.END

    await update.message.reply_text("Client ID bhejo jiska number add karna hai:")
    return ADDNUM_ID


async def addnumber_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        client_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Client ID sirf number mein bhejo. Dubara try karo:")
        return ADDNUM_ID
    client = db.get_client(client_id, user.id)
    if not client:
        await update.message.reply_text("Ye client ID aapke account mein nahi mili. Dubara bhejo:")
        return ADDNUM_ID
    context.user_data["addnum_client_id"] = client_id
    await update.message.reply_text(f"Client: {client['client_name']}\nAb numaindey ka number bhejo:")
    return ADDNUM_NUMBER


async def addnumber_get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    client_id = context.user_data.get("addnum_client_id")
    rep_number = update.message.text.strip()
    client = db.get_client(client_id, user.id)
    db.add_rep_number(client_id, user.id, rep_number)
    await update.message.reply_text(
        f"✅ Number save ho gaya.\n\n"
        f"Ye number client ({client['client_name']}) ko bhej do:\n"
        f"📞 {rep_number}\n\n"
        f"Proof aane par '{BTN_PROOF}' button dabao.",
        reply_markup=MAIN_MENU,
    )
    return ConversationHandler.END


# ============ /proof conversation ============
async def proof_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args:
        try:
            client_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Client ID number mein hona chahiye.")
            return ConversationHandler.END
        client = db.get_client(client_id, user.id)
        if not client:
            await update.message.reply_text("Ye client ID aapke account mein nahi mili.")
            return ConversationHandler.END
        context.user_data["proof_client_id"] = client_id
        await update.message.reply_text("Proof bhejo — photo ya text message:")
        return PROOF_WAIT

    await update.message.reply_text("Client ID bhejo jiska proof bhejna hai:")
    return PROOF_ID


async def proof_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        client_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Client ID sirf number mein bhejo. Dubara try karo:")
        return PROOF_ID
    client = db.get_client(client_id, user.id)
    if not client:
        await update.message.reply_text("Ye client ID aapke account mein nahi mili. Dubara bhejo:")
        return PROOF_ID
    context.user_data["proof_client_id"] = client_id
    await update.message.reply_text(f"Client: {client['client_name']}\nAb proof bhejo — photo ya text message:")
    return PROOF_WAIT


async def proof_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    client_id = context.user_data.get("proof_client_id")
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        db.add_proof(client_id, user.id, "photo", file_id)
    else:
        text = update.message.text or ""
        db.add_proof(client_id, user.id, "text", text)
    today_count, total_count = db.get_user_stats(user.id)
    await update.message.reply_text(
        f"✅ Proof save ho gaya. Client #{client_id} complete ho gaya.\n\n"
        f"📊 Aapka aaj ka count: {today_count}\n"
        f"📊 Total count: {total_count}",
        reply_markup=MAIN_MENU,
    )
    return ConversationHandler.END


# ============ /myclients ============
async def myclients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rows = db.get_pending_clients(user.id)
    if not rows:
        await update.message.reply_text("Koi pending client nahi hai.", reply_markup=MAIN_MENU)
        return
    lines = ["📋 Pending clients:\n"]
    for r in rows:
        status_hindi = "Number ka wait" if r["status"] == "pending_number" else "Proof ka wait"
        lines.append(f"#{r['id']} - {r['client_name']} ({r['client_phone']}) - {status_hindi}")
    await update.message.reply_text("\n".join(lines), reply_markup=MAIN_MENU)


# ============ /mystats ============
async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today_count, total_count = db.get_user_stats(user.id)
    await update.message.reply_text(
        f"📊 Aapke stats:\nAaj: {today_count}\nTotal: {total_count}",
        reply_markup=MAIN_MENU,
    )


# ============ /teamstats (admin only) ============
async def teamstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("Ye command sirf admin ke liye hai.")
        return
    rows = db.get_team_stats()
    if not rows:
        await update.message.reply_text("Koi data nahi mila.")
        return
    lines = ["📊 Team stats (aaj / total):\n"]
    for r in rows:
        lines.append(f"{r['broker_name']}: {r['today_cnt']} / {r['total_cnt']}")
    await update.message.reply_text("\n".join(lines))


def main():
    db.init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    newclient_conv = ConversationHandler(
        entry_points=[
            CommandHandler("newclient", newclient_start),
            MessageHandler(filters.Regex(f"^{re.escape(BTN_NEW)}$"), newclient_start),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, newclient_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, newclient_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(newclient_conv)

    addnumber_conv = ConversationHandler(
        entry_points=[
            CommandHandler("addnumber", addnumber_entry),
            MessageHandler(filters.Regex(f"^{re.escape(BTN_ADDNUM)}$"), addnumber_entry),
        ],
        states={
            ADDNUM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, addnumber_get_id)],
            ADDNUM_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, addnumber_get_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(addnumber_conv)

    proof_conv = ConversationHandler(
        entry_points=[
            CommandHandler("proof", proof_entry),
            MessageHandler(filters.Regex(f"^{re.escape(BTN_PROOF)}$"), proof_entry),
        ],
        states={
            PROOF_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, proof_get_id)],
            PROOF_WAIT: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, proof_receive)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(proof_conv)

    app.add_handler(CommandHandler("myclients", myclients))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN_MYCLIENTS)}$"), myclients))

    app.add_handler(CommandHandler("mystats", mystats))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN_STATS)}$"), mystats))

    app.add_handler(CommandHandler("teamstats", teamstats))

    logger.info("Bot start ho raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
@bot.message_handler(commands=['resetstats'])
def handle_reset(message):
    # Sirf Admin ke liye
    if str(message.from_user.id) == str(ADMIN_ID):
        reset_all_data()
        bot.reply_to(message, "⚠️ تمام کلائنٹس اور اسٹیٹس کا ڈیٹا ری سیٹ (0) کر دیا گیا ہے۔")
    else:
        bot.reply_to(message, "❌ آپ کے پاس یہ کمانڈ چلانے کا اختیار نہیں ہے۔")
