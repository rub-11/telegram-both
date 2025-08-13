from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # or replace with your bot token as a string

# Hardcoded menu data
MENU_ITEMS = [
    {
        "id": 8,
        "name": "Download Pdf",
        "acf": {
            "url": "",
            "upload_file": 18
        }
    },
    {
        "id": 3,
        "name": "Launch Your Product (B2B)",
        "acf": {
            "url": "",
            "upload_file": None
        }
    },
    {
        "id": 6,
        "name": "💸 Fees",
        "acf": {
            "url": "",
            "upload_file": None
        }
    },
    {
        "id": 4,
        "name": "💼 How to Invest",
        "acf": {
            "url": "",
            "upload_file": None
        }
    },
    {
        "id": 2,
        "name": "🔍 View Investment Deals",
        "acf": {
            "url": "",
            "upload_file": None
        }
    },
    {
        "id": 12,
        "name": "🚀 Space / AI / Robotics",
        "acf": {
            "url": "https://tabclix.com/ruben-hayrapetyan",
            "upload_file": ""
        }
    },
    {
        "id": 11,
        "name": "🤝 Referral Program",
        "acf": {
            "url": "",
            "upload_file": ""
        }
    },
    {
        "id": 5,
        "name": "🧑‍💼 Contact a Manager",
        "acf": {
            "url": "",
            "upload_file": None
        }
    },
]

# Helper function to get final URL
def get_url(acf):
    if acf["url"]:
        return acf["url"]
    elif acf["upload_file"]:
        # Construct a dummy file URL (adjust if needed based on real domain)
        return f"https://telegram-bot.test/wp-content/uploads/{acf['upload_file']}.pdf"
    else:
        return None

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for item in MENU_ITEMS:
        url = get_url(item["acf"])
        if url:
            keyboard.append([
                InlineKeyboardButton(text=item["name"], url=url)
            ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose an option below:",
        reply_markup=reply_markup
    )

# Main function
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot is running...")
    app.run_polling()
