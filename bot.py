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
async def fetch_menu_items():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

# =========================
# Build keyboard for a given parent
# =========================
def build_keyboard(menu_items, parent_id=0):
    buttons = []
    for item in menu_items:
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
    menu_items = await fetch_menu_items()
    keyboard = build_keyboard(menu_items, parent_id=0)
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

    menu_items = await fetch_menu_items()
    keyboard = build_keyboard(menu_items, parent_id=selected_id)

    title = next((item["name"] for item in menu_items if item["id"] == selected_id), "Menu")
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
