import os
import io
import aiohttp
from urllib.parse import urlparse, unquote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MENU_API_URL = "https://darkcyan-seahorse-221994.hostingersite.com/wp-json/wp/v2/menu"

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
            upload_file = item["acf"].get("upload_file")

            row_buttons = []

            if has_children:
                row_buttons.append(InlineKeyboardButton(text=name, callback_data=str(item["id"])))
            elif upload_file and isinstance(upload_file, int):
                 row_buttons.append(InlineKeyboardButton(text="⬇ " + name, callback_data=f"dl_{item['id']}"))

            else:
                url = await resolve_url(item)
                row_buttons.append(InlineKeyboardButton(text=name, url=url))

            buttons.append(row_buttons)

    if parent_id != 0:
        buttons.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="0")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_menu_data()
    keyboard = await build_keyboard(menu_data, parent_id=0)
    await update.message.reply_text("👋 Welcome to the Telegram Bot Menu:", reply_markup=keyboard)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "0":
        keyboard = await build_keyboard(menu_data, parent_id=0)
        await query.edit_message_text("📋 Main Menu", reply_markup=keyboard)
        return

    if data.startswith("dl_"):
        try:
            item_id = int(data[3:])
        except ValueError:
            await query.edit_message_text("⚠️ Invalid download request.")
            return

        selected_item = next((item for item in menu_data if item["id"] == item_id), None)
        if not selected_item:
            await query.edit_message_text("⚠️ Item not found.")
            return

        upload_file = selected_item["acf"].get("upload_file")
        if upload_file and isinstance(upload_file, int):
            file_url = await fetch_file_url(upload_file)
            if file_url:
                # Extract filename from URL preserving extension
                path = urlparse(file_url).path
                filename = os.path.basename(unquote(path))

                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as resp:
                        if resp.status == 200:
                            file_bytes = await resp.read()
                            file_like = io.BytesIO(file_bytes)
                            file_like.name = filename

                            await query.message.reply_document(document=file_like, filename=filename)
                            return
                        else:
                            await query.edit_message_text("⚠️ Failed to download file.")
                            return
            else:
                await query.edit_message_text("⚠️ Could not retrieve the file URL.")
                return

    # Normal menu navigation
    try:
        selected_id = int(data)
    except ValueError:
        await query.edit_message_text("⚠️ Invalid selection.")
        return

    selected_item = next((item for item in menu_data if item["id"] == selected_id), None)
    if not selected_item:
        keyboard = await build_keyboard(menu_data, parent_id=0)
        await query.edit_message_text("📋 Main Menu", reply_markup=keyboard)
        return

    keyboard = await build_keyboard(menu_data, parent_id=selected_id)
    title = selected_item["name"]
    await query.edit_message_text(f"📋 {title}", reply_markup=keyboard)

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
