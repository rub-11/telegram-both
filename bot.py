import os
import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MENU_API_URL = "https://darkcyan-seahorse-221994.hostingersite.com/wp-json/wp/v2/menu"

UPLOAD_FILE_URLS = {
    18: "http://telegram-bot.test/wp-content/uploads/2025/08/Telegram-bot-content-final-updated-05.08.2025-to-be-reviewed-and-implement.docx"
}

# Global menu cache
menu_data = []

async def fetch_menu_data():
    global menu_data
    async with aiohttp.ClientSession() as session:
        async with session.get(MENU_API_URL) as response:
            if response.status == 200:
                menu_data = await response.json()
            else:
                print(f"Failed to fetch menu: {response.status}")
                menu_data = []
async def fetch_file_url(media_id: int) -> str:
    url = f"https://darkcyan-seahorse-221994.hostingersite.com/wp-json/wp/v2/media/{media_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("source_url", "")
            else:
                print(f"Failed to fetch media {media_id}: {response.status}")
                return ""

async def resolve_url(item):
    upload_file = item["acf"].get("upload_file")

    if upload_file and isinstance(upload_file, int):
        return await fetch_file_url(upload_file)

    elif isinstance(item["acf"].get("url"), str) and item["acf"]["url"].strip():
        return item["acf"]["url"]

    else:
        return item["link"]


async def build_keyboard(menu_items, parent_id=0):
    buttons = []
    for item in menu_items:
        if item["parent"] == parent_id:
            name = item["name"]
            has_children = any(child["parent"] == item["id"] for child in menu_items)
            if has_children:
                button = InlineKeyboardButton(text=name, callback_data=str(item["id"]))
            else:
                url = await resolve_url(item)
                button = InlineKeyboardButton(text=name, url=url)
            buttons.append([button])
    if parent_id != 0:
        buttons.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="0")])
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_menu_data()
    parent_id = 0
    keyboard = await build_keyboard(menu_data, parent_id=parent_id)

    # Get main menu item (optional image display)
    item = get_menu_item_by_id(menu_data, parent_id)
    if item and item["acf"].get("image"):
        await update.message.reply_photo(photo=item["acf"]["image"])

    await update.message.reply_text("👋 Welcome to the Telegram Bot Menu:", reply_markup=keyboard)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_id = int(query.data)
    keyboard = await build_keyboard(menu_data, parent_id=selected_id)

    item = get_menu_item_by_id(menu_data, selected_id)
    title = item["name"] if item else "Menu"
    image_url = get_image_url(item) if item else None

    if image_url:
        await query.message.reply_photo(photo=image_url)

    await query.edit_message_text(f"📋 {title}", reply_markup=keyboard)

def get_menu_item_by_id(menu_items, item_id):
    return next((item for item in menu_items if item["id"] == item_id), None)


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    # 🚫 No asyncio.run() here!
    app.run_polling()
