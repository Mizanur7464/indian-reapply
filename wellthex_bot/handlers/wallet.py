from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from utils.validators import is_valid_wallet
from database.db import set_wallet, get_user_status, get_user_tasks
from config import TOKEN_NAME, REWARD_LINK

ASK_WALLET = 1

async def start_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Always get the message object
    if hasattr(update, "callback_query") and update.callback_query:
        message = update.callback_query.message
    elif hasattr(update, "effective_message") and update.effective_message:
        message = update.effective_message
    else:
        return ConversationHandler.END

    # Directly ask for wallet address, do not show button
    await message.reply_text(
        "Please enter your BEP20 wallet address (must start with 0x and be 42 characters long):"
    )
    return ASK_WALLET

async def ask_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please enter your BEP20 wallet address (must start with 0x and be 42 characters long):")
    return ASK_WALLET

async def save_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet = update.message.text.strip()
    print("[DEBUG] Entered save_wallet")
    print("[DEBUG] User entered wallet:", wallet)
    if not is_valid_wallet(wallet):
        print("[DEBUG] Invalid wallet detected")
        await update.message.reply_text("❌ Invalid wallet address. Please try again:")
        return ASK_WALLET
    user_id = update.effective_user.id
    print("[DEBUG] Saving wallet for user:", user_id)
    set_wallet(user_id, wallet)
    print("[DEBUG] Wallet saved, calling claim_reward")
    # Directly call claim_reward without sending confirmation message
    await claim_reward(update, context)
    return ConversationHandler.END

async def claim_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Fetch user status and tasks
    user_status = get_user_status(user_id)
    user_tasks = get_user_tasks(user_id)
    # Check email_verified
    if not user_status or user_status.get('email_verified') != 1:
        await update.message.reply_text("❌ You must verify your email before claiming your reward.")
        return
    # Check at least one task completed
    if not user_tasks or not any(user_tasks.get(task) for task in ['twitter', 'instagram', 'telegram', 'youtube']):
        await update.message.reply_text("❌ You must complete at least one social task before claiming your reward.")
        return
    # Check wallet connected
    if not user_status.get('wallet'):
        await update.message.reply_text("❌ You must connect your BEP20 wallet before claiming your reward.")
        return
    # All checks passed
    keyboard = [
        [InlineKeyboardButton("\U0001F381 Claim Airdrop", callback_data="claim_airdrop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎁 Congratulations! You have completed all requirements.\n\nYour reward is ready to claim! Visit: " + REWARD_LINK,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

def get_wallet_handler():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r'^/wallet$'), start_wallet),
            CallbackQueryHandler(start_wallet, pattern="^connect_wallet_start$")
        ],
        states={
            ASK_WALLET: [
                CallbackQueryHandler(ask_wallet, pattern="^connect_wallet$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_wallet)
            ]
        },
        fallbacks=[]
    )

# Add a handler for /claim command
claim_handler = CommandHandler('claim', claim_reward) 