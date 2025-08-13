import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Hardcoded menu data (cleaned up from your JSON)
MENU_DATA = [
    {
        "id": 8,
        "parent": 2,
        "name": "Download Pdf",
        "link": "http://telegram-bot.test/menu/download-pdf/",
        "acf": {"call_back": "", "url": "", "upload_file": 18},
    },
    {
        "id": 3,
        "parent": 0,
        "name": "Launch Your Product (B2B)",
        "link": "http://telegram-bot.test/menu/launch-your-product-b2b/",
        "acf": {"call_back": "", "url": "", "upload_file": None},
    },
    {
        "id": 6,
        "parent": 0,
        "name": "💸 Fees",
        "link": "http://telegram-bot.test/menu/fees/",
        "acf": {"call_back": "", "url": "", "upload_file": None},
    },
    {
        "id": 4,
        "parent": 0,
        "name": "🗼 How to Invest",
        "link": "http://telegram-bot.test/menu/how-to-invest/",
        "acf": {"call_back": "", "url": "", "upload_file": None},
    },
    {
        "id": 2,
        "parent": 0,
        "name": "🔍 View Investment Deals",
        "link": "http://telegram-bot.test/menu/view-investment-deals/",
        "acf": {"call_back": "", "url": "", "upload_file": None},
    },
    {
        "id": 12,
        "parent": 2,
        "name": "🚀 Space / AI / Robotics",
        "link": "http://telegram-bot.test/menu/space-ai-robotics/",
        "acf": {"call_back": "", "url": "https://tabclix.com/ruben-hayrapetyan", "upload_file": ""},
    },
    {
        "id": 11,
        "parent": 0,
        "name": "🤝 Referral Program",
        "link": "http://telegram-bot.test/menu/referral-program/",
        "acf": {"call_back": "", "url": "", "upload_file": ""},
    },
    {
        "id": 5,
        "parent": 0,
        "name": "🧑‍💼 Contact a Manager",
        "link": "http://telegram-bot.test/menu/contact-a-manage/",
        "acf": {"call_back": "", "url": "", "upload_file": None},
    },
]

# Map upload_file IDs to real file URLs (you must update this with your real URLs)
UPLOAD_FILE_URLS = {
    18: "http://telegram-bot.test/wp-content/uploads/2025/08/Telegram-bot-content-final-updated-05.08.2025-to-be-reviewed-and-implement.docx"
}

def resolve_url(item):
    """Return the correct URL for a menu item according to your rules."""
    if item["name"] == "Download Pdf" and item["acf"].get("upload_file"):
        upload_id = item["acf"]["upload_file"]
        return UPLOAD_FILE_URLS.get(upload_id, item["link"])
    # For other items, if acf.url is present and non-empty, use that
    if item["acf"].get("url"):
        return item["acf"]["url"]
    # fallback to the item's link
    return item["link"]

def build_keyboard(menu_items, parent_id=0):
    buttons = []
    for item in menu_items:
        if item["parent"] == parent_id:
            name = item["name"]
            has_children = any(child["parent"] == item["id"] for child in menu_items)
            if has_children:
                # If item has children, show button with callback_data for navigation
                button = InlineKeyboardButton(text=name, callback_data=str(item["id"]))
            else:
                # Leaf item, use resolved URL for button URL
                url = resolve_url(item)
                button = InlineKeyboardButton(text=name, url=url)
            buttons.append([button])
    if parent_id != 0:
        buttons.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="0")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = build_keyboard(MENU_DATA, parent_id=0)
    await update.message.reply_text("👋 Welcome to the Telegram Bot Menu:", reply_markup=keyboard)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_id = int(query.data)
    keyboard = build_keyboard(MENU_DATA, parent_id=selected_id)
    title = next((item["name"] for item in MENU_DATA if item["id"] == selected_id), "Menu")
    await query.edit_message_text(f"📋 {title}", reply_markup=keyboard)

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
