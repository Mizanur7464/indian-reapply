from telegram.ext import ApplicationBuilder, CallbackQueryHandler
from handlers.start import get_start_handler
from handlers.email_verification import get_email_verification_handler
from handlers.tasks import get_tasks_handler
from handlers.wallet import get_wallet_handler, start_wallet
from handlers.profile import profile_handlers
from handlers.admin import admin_handlers
from config import BOT_TOKEN
import warnings

warnings.filterwarnings('ignore')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register /start handler (with captcha)
    app.add_handler(get_start_handler())
    # Register email verification handler
    app.add_handler(get_email_verification_handler())
    # Register tasks handler
    app.add_handler(get_tasks_handler())
    # Register wallet handler
    app.add_handler(get_wallet_handler())
    # Register handler for connect_wallet_start button
    app.add_handler(CallbackQueryHandler(start_wallet, pattern="^connect_wallet_start$"))
    # Register dashboard/profile handlers
    for handler in profile_handlers:
        app.add_handler(handler)
    # Register admin handlers
    for handler in admin_handlers:
        app.add_handler(handler)

    print("WellthEx Airdrop Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main() 