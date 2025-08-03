from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database.db import add_user
from utils.captcha_utils import generate_math_captcha
from config import TELEGRAM_GROUP_LINK, TELEGRAM_GROUP_ID, TWITTER_LINK, INSTAGRAM_LINK, YOUTUBE_LINK

# States for ConversationHandler
CAPTCHA = 1

# Store captcha answers in memory (for demo; use Redis/DB for production)
captcha_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or f"id_{user_id}"
    print(f"[START] User started: {username}")
    args = context.args if hasattr(context, 'args') else []
    referrer_id = None
    if args:
        try:
            ref_id = int(args[0])
            if ref_id != user_id:
                referrer_id = ref_id
        except Exception:
            pass
    # Save user to DB with status 'new' and optional referrer_id
    add_user(user_id=user_id, username=user.username, status='new', referrer_id=referrer_id)
    # Custom welcome message with image
    msg = (
        f"🎉 Welcome to the Ghosty Airdrop! 👻💸\n"
        f"You've just entered the most hyped memecoin airdrop of the season!\n\n"
        f"🔥 Get 500 $GHOSTY just for joining!\n"
        f"💥 Earn 500 $GHOSTY for every friend you refer!\n\n"
        f"✅ Complete simple social media tasks to become eligible.\n"
        f"🚀 Let's make history like $SHIBA, $BONK, and $WIF — Ghosty is Phantom's own baby!\n\n"
        f"🌐 Official Website: https://ghostyphantom.com\n\n"
        f"✅ Click \"Check\" button to verify your entry and join the Airdrop successfully."
    )
    keyboard = [[InlineKeyboardButton("Check", callback_data="check_entry")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send image with caption
    with open('data/logo.jpg', 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=msg,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    return ConversationHandler.END

async def show_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    # Directly show captcha without group membership check
    question, answer = generate_math_captcha()
    captcha_answers[user_id] = answer
    sent_msg = await update.callback_query.message.reply_text(
        f"\U0001F44B Welcome to Ghosty Airdrop!\n\nPlease solve this captcha to continue:\n\n{question}"
    )
    # Store message IDs for deletion
    context.user_data['captcha_msg_id'] = sent_msg.message_id
    context.user_data['user_msg_id'] = update.callback_query.message.message_id
    await update.callback_query.answer()
    return CAPTCHA

async def check_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_answer = update.message.text.strip()
    correct_answer = str(captcha_answers.get(user_id, ''))
    if user_answer == correct_answer:
        # Delete captcha question and user reply
        try:
            await update.message.delete()
            captcha_msg_id = context.user_data.get('captcha_msg_id')
            if captcha_msg_id:
                await update.message.chat.delete_message(captcha_msg_id)
        except Exception:
            pass
        # Prompt user to verify email using /verify_email
        await update.message.reply_text(
            "✅ Captcha passed! Now, please verify your email to continue. Click /verify_email"
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Wrong answer. Please try again.")
        return CAPTCHA

# Handler registration helper
def get_start_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(show_captcha, pattern='^check_entry$')],
        states={
            CAPTCHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha)]
        },
        fallbacks=[]
    ) 