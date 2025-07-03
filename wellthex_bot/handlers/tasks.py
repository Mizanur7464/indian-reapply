from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler
from database.db import init_user_tasks, set_task_completed, set_twitter_username, set_instagram_username
from handlers.wallet import start_wallet
from telegram.ext import filters
from telegram.error import BadRequest
from config import TWITTER_LINK, INSTAGRAM_LINK, TELEGRAM_GROUP_LINK, TELEGRAM_GROUP_ID, YOUTUBE_LINK, TOKEN_NAME, TELEGRAM_CHANNEL_LINK, TELEGRAM_CHANNEL_ID

# Task states
TWITTER, INSTAGRAM, TELEGRAM, YOUTUBE = range(4)

# Add a new state for asking Twitter username
TWITTER_USERNAME = 100

# Add a new state for asking Instagram username
INSTAGRAM_USERNAME = 101

TASKS = [
    {
        'name': 'twitter',
        'text': '✅ Follow Twitter',
        'url': TWITTER_LINK,
        'state': TWITTER
    },
    {
        'name': 'instagram',
        'text': '✅ Follow Instagram',
        'url': INSTAGRAM_LINK,
        'state': INSTAGRAM
    },
    {
        'name': 'telegram',
        'text': '✅ Join Telegram Group & Add 5 users',
        'url': TELEGRAM_GROUP_LINK,
        'state': TELEGRAM
    },
    {
        'name': 'telegram_channel',
        'text': '✅ Join Telegram Channel',
        'url': TELEGRAM_CHANNEL_LINK,
        'state': 10  # New unique state for channel join
    },
    {
        'name': 'youtube',
        'text': '✅ Subscribe YouTube',
        'url': YOUTUBE_LINK,
        'state': YOUTUBE
    }
]

TELEGRAM_CHANNEL = 10  # New state for channel join

async def count_user_invites(user_id, bot):
    # TODO: Implement real invite count logic if possible
    return 0  # Placeholder: always returns 0

async def start_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_user_tasks(user_id)
    return await show_task(update, context, 0)

async def show_task(update, context, task_idx):
    # Always get the message object
    if hasattr(update, "callback_query") and update.callback_query:
        message = update.callback_query.message
    elif hasattr(update, "effective_message") and update.effective_message:
        message = update.effective_message
    else:
        return ConversationHandler.END

    if task_idx >= len(TASKS):
        # Show Connect Wallet button instead of calling start_wallet directly
        keyboard = [[InlineKeyboardButton("\ud83d\udce5 Connect Wallet", callback_data="connect_wallet_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "All tasks completed! Now connect your BEP20 wallet to receive your airdrop:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    task = TASKS[task_idx]
    keyboard = [
        [InlineKeyboardButton('Open Link', url=task['url'])],
        [InlineKeyboardButton('✅ Done', callback_data=f'done_{task_idx}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(f"{task['text']}", reply_markup=reply_markup)
    return task['state']

async def check_telegram_membership(user_id, bot):
    try:
        member = await bot.get_chat_member(TELEGRAM_GROUP_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except BadRequest:
        return False

async def check_channel_membership(user_id, bot):
    try:
        member = await bot.get_chat_member(TELEGRAM_CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except BadRequest:
        return False

async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[DEBUG] done_task called")
    query = update.callback_query
    user_id = query.from_user.id
    if query.data.startswith('done_'):
        idx = int(query.data.split('_')[1])
        print("[DEBUG] idx:", idx)
        if idx == 0:
            await query.message.reply_text("Please enter your twitter username with '@'.  (Mandatory)")
            return TWITTER_USERNAME
        elif idx == 1:
            await query.message.reply_text("Please enter your Instagram username with '@'.  (Mandatory)")
            return INSTAGRAM_USERNAME
        elif idx == 2:  # Telegram group task
            in_group = await check_telegram_membership(user_id, context.bot)
            print("[DEBUG] in_group:", in_group)
            if not in_group:
                print("[DEBUG] User not in group")
                await query.answer("❌ Sorry, please join our telegram group.", show_alert=True)
                return TELEGRAM
        elif idx == 3:  # Telegram channel task
            in_channel = await check_channel_membership(user_id, context.bot)
            print("[DEBUG] in_channel:", in_channel)
            if not in_channel:
                print("[DEBUG] User not in channel")
                await query.answer("❌ Sorry, please join our telegram channel.", show_alert=True)
                return TELEGRAM_CHANNEL
        set_task_completed(user_id, TASKS[idx]['name'])
        try:
            await query.message.delete()
        except Exception:
            pass
        return await show_task(update, context, idx + 1)
    await query.message.reply_text('Unknown task.')
    return ConversationHandler.END

async def save_twitter_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    user_id = update.effective_user.id
    if not username.startswith('@') or len(username) < 2:
        await update.message.reply_text("❌ Invalid username. Please enter your twitter username with '@'.")
        return TWITTER_USERNAME
    set_twitter_username(user_id, username)
    set_task_completed(user_id, 'twitter')
    await update.message.reply_text("✅ Twitter username saved!")
    return await show_task(update, context, 1)

async def save_instagram_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    user_id = update.effective_user.id
    if not username.startswith('@') or len(username) < 2:
        await update.message.reply_text("❌ Invalid username. Please enter your Instagram username with '@'.")
        return INSTAGRAM_USERNAME
    # Save Instagram username to DB (implement set_instagram_username in db.py)
    set_instagram_username(user_id, username)
    set_task_completed(user_id, 'instagram')
    await update.message.reply_text("✅ Instagram username saved!")
    return await show_task(update, context, 2)

def get_tasks_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_tasks, pattern='^start_tasks$')],
        states={
            TWITTER: [CallbackQueryHandler(done_task)],
            INSTAGRAM: [CallbackQueryHandler(done_task)],
            TELEGRAM: [CallbackQueryHandler(done_task)],
            TELEGRAM_CHANNEL: [CallbackQueryHandler(done_task)],
            YOUTUBE: [CallbackQueryHandler(done_task)],
            TWITTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_twitter_username)],
            INSTAGRAM_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_instagram_username)],
        },
        fallbacks=[]
    ) 