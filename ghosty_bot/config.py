import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Social and external links
TWITTER_LINK = os.getenv("TWITTER_LINK")
INSTAGRAM_LINK = os.getenv("INSTAGRAM_LINK")
TELEGRAM_GROUP_LINK = os.getenv("TELEGRAM_GROUP_LINK")
TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", "0"))
YOUTUBE_LINK = os.getenv("YOUTUBE_LINK")
TELEGRAM_CHANNEL_LINK = os.getenv("TELEGRAM_CHANNEL_LINK")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID", "0"))

# Token and project info
TOKEN_NAME = os.getenv("TOKEN_NAME", "GHOSTY")
REWARD_LINK = os.getenv("REWARD_LINK")

# Add more config variables as needed 
