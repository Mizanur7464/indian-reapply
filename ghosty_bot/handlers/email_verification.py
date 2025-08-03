from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
import re
from database.db import set_email_verified, get_referrer_id, add_wtx
import requests
import random

ASK_EMAIL, VERIFY_EMAIL, ENTER_CODE = range(3)

MAILEROO_API_KEY = "568018071eeba30cebfbf7120b62a0bc176bb0c4f7baa5bd4f3cb836de45ccba"
MAILEROO_SENDER = "noreply@ghostyphantom.com"

# Start email verification: show button
async def start_email_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("\ud83d\udce7 Verify Email", callback_data="verify_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please verify your email to continue:", reply_markup=reply_markup
    )
    return ASK_EMAIL

# Handle button click
async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Enter your email address:")
    return VERIFY_EMAIL

# Validate email and send code
async def verify_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text("\u274c Invalid email format. Try again:")
        return VERIFY_EMAIL
    # Generate code and send via Maileroo
    code = str(random.randint(100000, 999999))
    context.user_data['verify_email'] = {'email': email, 'code': code}
    maileroo_url = "https://smtp.maileroo.com/send"
    data = {
        "from": MAILEROO_SENDER,
        "to": email,
        "subject": "Your Ghosty Verification Code",
        "html": f"<b>Your verification code is: {code}</b>"
    }
    headers = {
        "X-API-Key": MAILEROO_API_KEY
    }
    try:
        resp = requests.post(maileroo_url, data=data, headers=headers, timeout=10)
        print('Maileroo response:', resp.status_code, resp.text)  # Debug print
        if resp.status_code == 200:
            await update.message.reply_text("A verification code has been sent to your email. Please enter the code:")
            return ENTER_CODE
        else:
            await update.message.reply_text("Failed to send email. Please try again later.")
            return ConversationHandler.END
    except Exception as e:
        print('Maileroo exception:', e)  # Debug print
        await update.message.reply_text("Failed to send email. Please try again later.")
        return ConversationHandler.END

# Check code
async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text.strip()
    data = context.user_data.get('verify_email', {})
    if user_code == data.get('code'):
        user_id = update.effective_user.id
        set_email_verified(user_id, data.get('email'))
        # Referral bonus
        referrer_id = get_referrer_id(user_id)
        if referrer_id:
            add_wtx(referrer_id, 500)
            try:
                await context.bot.send_message(
                    referrer_id,
                    "🎉 You received 500 $GHOSTY for a new referral!"
                )
            except Exception:
                pass
        keyboard = [[InlineKeyboardButton("\ud83d\ude80 Start Tasks", callback_data="start_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "\u2705 Email verified! Proceeding to next step...\n\nClick the button below to start your tasks:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("\u274c Incorrect code. Please try again:")
        return ENTER_CODE

# Handler registration helper
def get_email_verification_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('verify_email', start_email_verification)],
        states={
            ASK_EMAIL: [CallbackQueryHandler(ask_email, pattern="^verify_email$")],
            VERIFY_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_email)],
            ENTER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_code)]
        },
        fallbacks=[]
    ) 