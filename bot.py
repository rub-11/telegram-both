from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Use your actual token here or load from .env if using
BOT_TOKEN = os.getenv("BOT_TOKEN") 
# Start message and menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 View Investment Deals", callback_data='deals')],
        [InlineKeyboardButton("🏢 Launch Your Product (B2B)", callback_data='b2b')],
        [InlineKeyboardButton("💼 How to Invest", callback_data='invest')],
        [InlineKeyboardButton("📚 Learn & Explore", callback_data='learn')],
        [InlineKeyboardButton("🧑‍💼 Contact a Manager", callback_data='contact')],
        [InlineKeyboardButton("💸 Fees", url='https://tabclix.com/ruben-hayrapetyan')],
        [InlineKeyboardButton("🤝 Referral Program", url='https://yourwebsite.com/referral')],
        [InlineKeyboardButton("📄 Partnership Deck", url='https://tabclix.com/ruben-hayrapetyan.pdf')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to New Venture Brokerage!\n\n"
        "We're a licensed investment platform offering access to:\n"
        "🌐 Venture Capital | 🏢 Real Estate | 📈 ETFs\n\n"
        "What would you like to explore?",
        reply_markup=reply_markup
    )

# Handle button clicks
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'deals':
        keyboard = [
            [InlineKeyboardButton("🚀 Space / AI / Robotics", url='https://yourwebsite.com/deals')],
            [InlineKeyboardButton("🧠 Neuralink Deal", url='https://yourwebsite.com/deals/neuralink')],
            [InlineKeyboardButton("📞 Request Call", url='https://calendly.com/nvbmanager')],
            [InlineKeyboardButton("⬅ Back to Menu", callback_data='back')]
        ]
        await query.edit_message_text("📊 Our current private market opportunities:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'b2b':
        keyboard = [
            [InlineKeyboardButton("📝 Become a Deal Provider", url='https://yourwebsite.com/b2b')],
            [InlineKeyboardButton("📘 Step-by-Step Guide", url='https://yourwebsite.com/b2b-guide')],
            [InlineKeyboardButton("📞 Request Demo Call", url='https://calendly.com/nvbmanager')],
            [InlineKeyboardButton("⬅ Back to Menu", callback_data='back')]
        ]
        await query.edit_message_text("🏢 Launch your own product with NVB:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'invest':
        keyboard = [
            [InlineKeyboardButton("✅ Start KYC", url='https://yourwebsite.com/kyc')],
            [InlineKeyboardButton("📞 Talk to Manager", url='https://t.me/gyulnara')],
            [InlineKeyboardButton("📊 Access Terminal", url='https://yourwebsite.com/terminal')],
            [InlineKeyboardButton("⬅ Back to Menu", callback_data='back')]
        ]
        await query.edit_message_text("💼 How to Invest with NVB:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'contact':
        keyboard = [
            [InlineKeyboardButton("📞 Request Call", url='https://calendly.com/nvbmanager')],
            [InlineKeyboardButton("❓ Ask a Question", url='https://t.me/nvbmanager')],
            [InlineKeyboardButton("📅 Book Zoom", url='https://zoom.us/yourlink')],
            [InlineKeyboardButton("⬅ Back to Menu", callback_data='back')]
        ]
        await query.edit_message_text("🧑‍💼 Contact our team:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'learn':
        await query.edit_message_text("📚 Educational content is coming soon!", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back to Menu", callback_data='back')]
        ]))

    elif query.data == 'back':
       keyboard = [
            [InlineKeyboardButton("🔍 View Investment Deals", callback_data='deals')],
            [InlineKeyboardButton("🏢 Launch Your Product (B2B)", callback_data='b2b')],
            [InlineKeyboardButton("💼 How to Invest", callback_data='invest')],
            [InlineKeyboardButton("📚 Learn & Explore", callback_data='learn')],
            [InlineKeyboardButton("🧑‍💼 Contact a Manager", callback_data='contact')],
            [InlineKeyboardButton("💸 Fees", url='https://tabclix.com/ruben-hayrapetyan')],
            [InlineKeyboardButton("🤝 Referral Program", url='https://yourwebsite.com/referral')],
            [InlineKeyboardButton("📄 Partnership Deck", url='https://yourwebsite.com/partnership.pdf')],
        ]
    await query.edit_message_text(
            "👋 Back to Main Menu:\n\n"
            "We're a licensed investment platform offering access to:\n"
            "🌐 Venture Capital | 🏢 Real Estate | 📈 ETFs\n\n"
            "What would you like to explore?",
            reply_markup=InlineKeyboardMarkup(keyboard)
     )


# Launch bot
if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
