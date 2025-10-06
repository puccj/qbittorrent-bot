from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import qbittorrentapi
import logging
import requests

from config import *

# ==== CONNECT TO QBITTORRENT ====
qbt_client = qbittorrentapi.Client(
    host=f"http://{QBITTORRENT_HOST}:{QBITTORRENT_PORT}",
    username=QBITTORRENT_USER,
    password=QBITTORRENT_PASS,
)

# ==== Auth Decorator ====
def restricted(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in AUTHORIZED_USERS_ID:
            await update.message.reply_text("🚫 You are not authorized to use this bot.")
            logging.warning(f"Unauthorized access attempt by {user_id}")
            return
        return await func(update, context)
    return wrapper

# ==== Command: Start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 *Welcome to Torrent Raspberry Bot!*\n\n"
        "I am a *private* bot that helps to manage torrents on a Raspberry Pi.\n"
        "_Private_ means that only authorized users can interact with me, so if you are "
        "here by chance I'm sorry but I can't work for you 😅."
        "However, feel free to copy the code from the [GitHub repository](https://github.com/puccj/qbittorrent-bot)"
        "and develop your own bot!\n\n"
        "For the authorized users, here’s what I can do for you:\n"
        "• Just paste a magnet or an xtravel link and I’ll start downloading it!\n"
        "• /ip — Show the public IP\n"
        "• /status — Show the last 5 torrents and their progress\n\n"
        "To automatically search for torrents, I can suggest you to use"
        "[1337x search bot](https://t.me/search_content_bot) and then forward (or copy-paste) the link to me.\n\n"
        "_Ready when you are!_ 🚀"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


# ==== Command: Get Public IP ====
@restricted
async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = requests.get("https://api.ipify.org").text
    await update.message.reply_text(f"🌐 Raspberry's public IP: {ip}")

# ==== Command: Get status ====
@restricted
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        torrents = qbt_client.torrents_info(sort="added_on", reverse=True)
        if not torrents:
            await update.message.reply_text("No torrents currently in the list.")
            return

        # get the last 5 added torrents
        latest = torrents[:5]
        msg = "📊 *Last 5 Torrents:*\n\n"
        for t in latest:
            emoji = "🎬" if t.save_path.startswith(DOWNLOAD_PATHS["film"]) else "📺"
            progress = round(t.progress * 100, 1)
            done = "✅" if progress == 100 else "⏳"
            msg += f"{emoji} *{t.name}*\nProgress: {progress}% {done} | State: {t.state}\n\n"

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error getting status:\n`{e}`", parse_mode="Markdown")

# ==== Command: Add torrent (handled via message) ====
@restricted
async def add_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith("magnet:?") or text.startswith("https://xtravel."):
        context.user_data["magnet"] = text
        await update.message.reply_text("🔗 Magnet link saved. Please select a category.")
    else:
        await update.message.reply_text("Please send a valid magnet link or an xtravel URL.")

# ==== Message Handler ====
@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.startswith("magnet:?") or text.startswith("https://xtravel."):
        # Save magnet link in user_data for later button callback
        context.user_data["magnet"] = text

        # Create inline keyboard with two buttons
        keyboard = [
            [
                InlineKeyboardButton("🎬 Film", callback_data="film"),
                InlineKeyboardButton("📺 TV Series", callback_data="tv"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Select the category for this torrent:",
            reply_markup=reply_markup,
        )
    else:
        await update.message.reply_text("Send me a magnet link (starting with `magnet:?`) or an xtravel URL.")


# ==== Button Handler ====
@restricted
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    magnet = context.user_data.get("magnet")
    if not magnet:
        await query.edit_message_text("⚠️ No magnet link found in memory. Send a new one.")
        return

    category = query.data
    save_path = DOWNLOAD_PATHS.get(category)

    try:
        qbt_client.torrents_add(urls=magnet, save_path=save_path)
        await query.edit_message_text(
            f"✅ Torrent added to qBittorrent under *{category}* folder!\n"
            f"`{save_path}`",
            parse_mode="Markdown",
        )
    except Exception as e:
        await query.edit_message_text(f"⚠️ Error adding torrent: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ip", get_ip))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("addtorrent", add_torrent))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()