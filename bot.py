import os
import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "http://telegram-bot.test/wp-json/wp/v2/menu"
print(API_URL)
# =========================
# Fetch and parse menu data
# =========================

MENU_ITEMS = [
    {"id": 2, "name": "🔍 View Investment Deals", "link": "http://telegram-bot.test/menu/view-investment-deals/", "parent": 0},
    {"id": 12, "name": "🚀 Space / AI / Robotics", "link": "http://telegram-bot.test/menu/space-ai-robotics/", "parent": 2},
    {"id": 3, "name": "🏢 Launch Your Product (B2B)", "link": "http://telegram-bot.test/menu/launch-your-product-b2b/", "parent": 0},
    {"id": 4, "name": "💼 How to Invest", "link": "http://telegram-bot.test/menu/how-to-invest/", "parent": 0},
    {"id": 5, "name": "🧑‍💼 Contact a Manager", "link": "http://telegram-bot.test/menu/contact-a-manage/", "parent": 0},
    {"id": 6, "name": "💸 Fees", "link": "http://telegram-bot.test/menu/fees/", "parent": 0},
    {"id": 8, "name": "Download Pdf", "link": "http://telegram-bot.test/menu/download-pdf/", "parent": 2},
    {"id": 11, "name": "🤝 Referral Program", "link": "http://telegram-bot.test/menu/referral-program/", "parent": 0}
]

""" async def fetch_menu_items():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status == 200:
                return await resp.json()
            return [] """

# =========================
# Build keyboard for a given parent
# =========================
def build_keyboard(menu_items, parent_id=0):
    buttons = []
    for item in MENU_ITEMS:
        if item["parent"] == parent_id:
            name = item["name"]
            # If it has children, show as callback
            has_children = any(child["parent"] == item["id"] for child in menu_items)
            if has_children:
                button = InlineKeyboardButton(text=name, callback_data=str(item["id"]))
            else:
                button = InlineKeyboardButton(text=name, url=item["link"])
            buttons.append([button])  # One per row
    # Add back button if not root
    if parent_id != 0:
        buttons.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="0")])
    return InlineKeyboardMarkup(buttons)

# ===============
# /start command
# ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = build_keyboard(MENU_ITEMS, parent_id=0)
    await update.message.reply_text(
        "👋 Welcome to the Telegram Bot Menu:",
        reply_markup=keyboard
    )

# =======================
# Handle button clicks
# =======================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_id = int(query.data)


    keyboard = build_keyboard(MENU_ITEMS, parent_id=selected_id)

    title = next((item["name"] for item in MENU_ITEMS if item["id"] == selected_id), "Menu")
    await query.edit_message_text(
        f"📋 {title}",
        reply_markup=keyboard
    )

# ==========
# Run Bot
# ==========
if __name__ == '__main__':
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
