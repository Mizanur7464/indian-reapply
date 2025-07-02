from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.db import get_user_info, get_user_tasks, get_referral_count
from config import TOKEN_NAME

# Dashboard handler
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE, welcome_back=False):
    user_id = update.effective_user.id
    info = get_user_info(user_id)
    tasks = get_user_tasks(user_id)
    referrals = get_referral_count(user_id)
    # Right message object
    if update.message:
        message = update.message
    elif hasattr(update, "callback_query") and update.callback_query:
        message = update.callback_query.message
    else:
        return

    twitter = info['username'] or 'N/A'
    instagram = info.get('instagram') if info and 'instagram' in info else 'N/A'
    email = info.get('email') if info and 'email' in info else 'N/A'
    # User's balance is the total earned tokens (base + referral bonus)
    wtx_balance = info['wtx'] or 0
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"

    if welcome_back:
        greeting = "Hi, welcome back!"
    else:
        greeting = "🎉Congratulations! You have successfully completed airdrop tasks."

    msg = (
        f"{greeting}\n\n"
        f"<b>Total Referrals:</b> <code>{referrals}</code>\n"
        f"<b>Total Referral Bonus Earned:</b> <code>{referrals * 20} {TOKEN_NAME}</code>\n"
        f"Earn 20 {TOKEN_NAME} for every friend you invite!\n\n"
        f"Your Provided Data:\n"
        f"    Email: <code>{email}</code>\n"
        f"    Twitter: @{twitter}\n"
        f"    Instagram: @{instagram}\n"
        f"    ETH or BSC Address:\n"
        f"    <code>{info['wallet'] or 'N/A'}</code>\n\n"
        f"🔗 referral link: <code>{referral_link}</code>"
    )
    keyboard = [
        [InlineKeyboardButton("\ud83d\udd04 Refresh", callback_data="refresh_dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def refresh_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Dashboard refreshed!", show_alert=False)
    try:
        await query.message.delete()
    except Exception:
        pass
    await dashboard(update, context, welcome_back=True)

# Remove profile handler and button logic; only keep dashboard and its handler
profile_handlers = [
    CommandHandler('dashboard', dashboard),
    CallbackQueryHandler(dashboard, pattern='^dashboard$'),
    CallbackQueryHandler(refresh_dashboard, pattern='^refresh_dashboard$'),
] 