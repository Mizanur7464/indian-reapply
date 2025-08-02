from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.db import get_user_info, get_user_tasks, get_referral_count, get_airdrop_claimed, set_airdrop_claimed, add_wtx
from config import TOKEN_NAME

# Claim Reward handler (was dashboard)
async def claim_reward(update: Update, context: ContextTypes.DEFAULT_TYPE, welcome_back=False):
    user_id = update.effective_user.id
    info = get_user_info(user_id)
    tasks = get_user_tasks(user_id)
    referrals = get_referral_count(user_id)
    claimed = get_airdrop_claimed(user_id)
    if update.message:
        message = update.message
    elif hasattr(update, "callback_query") and update.callback_query:
        message = update.callback_query.message
    else:
        return
    # Ensure only one '@' for Twitter and Instagram usernames
    def format_username(username):
        if not username or username == 'N/A':
            return 'N/A'
        return username if username.startswith('@') else f'@{username}'
    twitter = format_username(info['username'])
    instagram = format_username(info.get('instagram')) if info and 'instagram' in info else 'N/A'
    email = info.get('email') if info and 'email' in info else 'N/A'
    wtx_balance = info['wtx'] or 0
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    referral_token = referrals * 500
    all_tasks_complete = tasks and all(tasks.get(t, 0) == 1 for t in tasks)
    if welcome_back:
        greeting = "Hi, welcome back!"
    else:
        greeting = "\U0001F389Congratulations! You have successfully completed airdrop tasks."
    msg = (
        f"{greeting}\n\n"
        f"<b>Airdrop Token Balance:</b> <code>{wtx_balance} {TOKEN_NAME}</code>\n"
        f"<b>Referral Token Balance:</b> <code>{referral_token} {TOKEN_NAME}</code>\n"
        f"<b>Total Referrals:</b> <code>{referrals}</code>\n"
        f"Earn 500 {TOKEN_NAME} for every friend you invite!\n\n"
        f"Your Provided Data:\n"
        f"    Email: <code>{email}</code>\n"
        f"    Twitter: {twitter}\n"
        f"    Instagram: {instagram}\n"
        f"    BSC Address:\n"
        f"    <code>{info['wallet'] or 'N/A'}</code>\n\n"
        f"\U0001F517<code>referral link:</code> <a href='{referral_link}'>{referral_link}</a>"
    )
    keyboard = []
    keyboard.append([InlineKeyboardButton("💰 BUY GHOSTY (Presale)", callback_data="buy_wtx")])
    keyboard.append([InlineKeyboardButton("\U0001F504 Refresh", callback_data="refresh_claim_reward")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def claim_airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    claimed = get_airdrop_claimed(user_id)
    if claimed:
        await claim_reward(update, context, welcome_back=True)
        return
    set_airdrop_claimed(user_id)
    add_wtx(user_id, 500)
    await query.answer("Airdrop claimed!", show_alert=True)
    await claim_reward(update, context, welcome_back=True)

async def buy_wtx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Presale purchase coming soon! Stay tuned.")

async def refresh_claim_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Reward summary refreshed!", show_alert=False)
    try:
        await query.message.delete()
    except Exception:
        pass
    await claim_reward(update, context, welcome_back=True)

# Remove profile handler and button logic; only keep claim_reward and its handler
profile_handlers = [
    CommandHandler('claim_reward', claim_reward),
    CallbackQueryHandler(claim_reward, pattern='^claim_reward$'),
    CallbackQueryHandler(claim_airdrop, pattern='^claim_airdrop$'),
    CallbackQueryHandler(buy_wtx, pattern='^buy_wtx$'),
    CallbackQueryHandler(refresh_claim_reward, pattern='^refresh_claim_reward$'),
] 