import os
import io
import aiohttp
from urllib.parse import urlparse, unquote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API endpoint
MENU_API_URL = "https://darkcyan-seahorse-221994.hostingersite.com/wp-json/wp/v2/menu?per_page=100"

# Global menu data cache
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

# Fetch file URL by media ID
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

# Resolve appropriate URL for a menu item
async def resolve_url(item):
    upload_file = item["acf"].get("upload_file")
    if upload_file and isinstance(upload_file, int):
        return await fetch_file_url(upload_file)
    elif isinstance(item["acf"].get("url"), str) and item["acf"]["url"].strip():
        return item["acf"]["url"]
    else:
        return item["link"]

# Build the inline keyboard
async def build_keyboard(menu_items, parent_id=0):
    buttons = []
    for item in menu_items:
        if item["parent"] == parent_id:
            name = item["name"]
            has_children = any(child["parent"] == item["id"] for child in menu_items)
            upload_file = item["acf"].get("upload_file")

            row_buttons = []

            if has_children:
                row_buttons.append(
                    InlineKeyboardButton(text=name, callback_data=str(item["id"]))
                )
            elif upload_file and isinstance(upload_file, int):
                row_buttons.append(
                    InlineKeyboardButton(text="⬇ " + name, callback_data=f"dl_{item['id']}")
                )
            else:
                url = await resolve_url(item)
                row_buttons.append(InlineKeyboardButton(text=name, url=url))

            buttons.append(row_buttons)

    if parent_id != 0:
        buttons.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="0")])
    return InlineKeyboardMarkup(buttons)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_menu_data()
    keyboard = await build_keyboard(menu_data, parent_id=0)

    await update.message.reply_text(
        "👋 Welcome to New Venture Brokerage!\n\n"
        "New Venture Brokerage CJSC is a licensed provider of brokerage, dealer, custody, and underwriting services, "
        "holding license \\#ՆԸ 0028 issued by the Central Bank of Armenia. The company's mission is to create an accessible "
        "and transparent private market, enabling individuals to buy and sell private equity in some of the world's most "
        "innovative companies. It aims to provide quality and reliable services to investors in private markets, adhering "
        "to international standards and fostering strong relationships with clients and partners.\n\n"
        "We specialize in venture capital, securities, and structured financial instruments. We are proud to say that we "
        "serve as a bridging link between investors from Armenia and abroad and leading companies worldwide that have "
        "already made a significant impact in their respective industries.",
        reply_markup=keyboard
    )

# Button handler
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Back to main menu
    if data == "0":
        keyboard = await build_keyboard(menu_data, parent_id=0)
        await query.edit_message_text("📋 Main Menu", reply_markup=keyboard)
        return

    # Download handler
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
                # Extract filename
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

    # Normal navigation
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

    # Build submenu
    keyboard = await build_keyboard(menu_data, parent_id=selected_id)
    title = selected_item["name"]
    description = selected_item.get("description", {}).get("rendered", "")
    text = f"📋 *{title}*\n\n{description}"

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

# Main runner
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
