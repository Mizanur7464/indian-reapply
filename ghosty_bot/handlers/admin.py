from telegram import Update, InputFile
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from config import ADMIN_ID
from database.db import get_db_connection
import csv
import io

# States for broadcast
ASK_BROADCAST = 1

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return
    msg = (
        "🛠 <b>Admin Panel</b>\n\n"
        "/stats - Show user stats\n"
        "/broadcast - Send message to all users\n"
        "/export - Export all user data (CSV)"
    )
    await update.message.reply_text(msg, parse_mode='HTML')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM users WHERE email_verified = 1')
    verified = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM users WHERE referrer_id IS NOT NULL')
    referrals = cur.fetchone()[0]
    conn.close()
    msg = f"👥 Total users: <b>{total}</b>\n✅ Verified: <b>{verified}</b>\n🤝 Referrals: <b>{referrals}</b>"
    await update.message.reply_text(msg, parse_mode='HTML')

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return ConversationHandler.END
    await update.message.reply_text("Send the message you want to broadcast to all users:")
    return ASK_BROADCAST

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return ConversationHandler.END
    text = update.message.text
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in cur.fetchall()]
    conn.close()
    sent = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(uid, text)
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"Broadcast sent to {sent} users.")
    return ConversationHandler.END

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id, username, status, email, email_verified, referrer_id, wtx, wallet FROM users')
    rows = cur.fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['user_id', 'username', 'status', 'email', 'email_verified', 'referrer_id', 'wtx', 'wallet'])
    for row in rows:
        writer.writerow([row['user_id'], row['username'], row['status'], row['email'], row['email_verified'], row['referrer_id'], row['wtx'], row['wallet']])
    output.seek(0)
    await update.message.reply_document(InputFile(io.BytesIO(output.getvalue().encode()), filename='users.csv'))

admin_handlers = [
    CommandHandler('admin', admin_panel),
    CommandHandler('stats', stats),
    CommandHandler('export', export_csv),
    ConversationHandler(
        entry_points=[CommandHandler('broadcast', broadcast_start)],
        states={ASK_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send)]},
        fallbacks=[],
    ),
] 