import os
import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MENU_API_URL = "https://darkcyan-seahorse-221994.hostingersite.com/wp-json/wp/v2/menu"

# Global menu cache
menu_data = []

# Fetch menu from WordPress
async def fetch_menu_data():
    global menu_data
    async with aiohttp.ClientSession() as session:
        async with session.get(MENU_API_URL) as response:
            if response.status == 200:
                menu_data = await response.json()
            else:
                print(f"Failed to fetch menu: {response.status}")
                menu_data = []

# Fetch any media (image or file)
async def fetch_media_url(media_id: int) -> str:
    url = f"https://darkcyan-seahorse-221994.hostingersite.com/wp-json/wp/v2/media/{media_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("source_url", "")
            else:
                print(f"Failed to fetch media {media_id}: {response.status}")
                return ""

# Get correct URL for any menu item
async def resolve_url(item):
    upload_file = item["acf"].get("upload_file")
    if upload_file and isinstance(upload_file, int):
        return await fetch_media_url(upload_file)
    elif isinstance(item["acf"].get("url"), str) and item["acf"]["url"].strip():
        return item["acf"]["url"]
    else:
        return item["link"]

# Get image URL if any
async def get_image_url(item):
    image_id = item["acf"].get("image")
    if isinstance(image_id, int):
        return await fetch_media_url(image_id)
    return None

# Helper: get a menu item by ID
def get_menu_item_by_id(menu_items, item_id):
    return next((item for item in menu_items if item["id"] == item_id), None)

# Build the Telegram inline keyboard
async def build_keyboard(menu_items, parent_id=0):
    buttons = []
    for item in menu_items:
        if item["parent"] == parent_id:
            name = item["name"]
            has_children = any(child["parent"] == item["id"] for child in menu_items)

            if has_children:
                button = InlineKeyboardButton(text=name, callback_data=str(item["id"]))
            elif item["name"] == "Download Pdf":
                # Special handling: no button, handled as direct file download
                continue
            else:
                url = await resolve_url(item)
                button = InlineKeyboardButton(text=name, url=url)

            buttons.append([button])

    if parent_id != 0:
        buttons.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="0")])

    return InlineKeyboardMarkup(buttons)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_menu_data()
    parent_id = 0
    keyboard = await build_keyboard(menu_data, parent_id)

    item = get_menu_item_by_id(menu_data, parent_id)
    if item:
        image_url = await get_image_url(item)
        if image_url:
            await update.message.reply_photo(photo=image_url)

    await update.message.reply_text("👋 Welcome to the Telegram Bot Menu:", reply_markup=keyboard)

# Handle button clicks
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_id = int(query.data)

    item = get_menu_item_by_id(menu_data, selected_id)

    # Special case: Download Pdf
    file_url = await resolve_url(item)
    if file_url:
        if file_url:
            await query.message.reply_document(document=file_url)
        return

    keyboard = await build_keyboard(menu_data, parent_id=selected_id)

    title = item["name"] if item else "Menu"

    if item:
        image_url = await get_image_url(item)
        if image_url:
            await query.message.reply_photo(photo=image_url)

    await query.edit_message_text(f"📋 {title}", reply_markup=keyboard)

# Start the bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    app.run_polling()
