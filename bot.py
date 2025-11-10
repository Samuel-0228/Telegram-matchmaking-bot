# bot.py - Telegram Matchmaking Bot (Webhook Edition)
# A flirty Python Telegram bot for profile setup, matchmaking, and instant chats.
# Built with python-telegram-bot v20+. Switched to webhooks for better scalability
# and handling multiple users concurrently (push-based updates from Telegram).
#
# Deployment Notes:
# - Requires HTTPS (e.g., deploy on Heroku, Render, or Vercel with SSL).
# - Set WEBHOOK_URL to your domain (e.g., https://yourapp.com/bot).
# - Optional: Provide cert_file and key_file for self-signed certs (local testing).
# - Set webhook via Telegram API: https://core.telegram.org/bots/api#setwebhook
# - For local dev: Use ngrok for HTTPS tunnel, then curl to set webhook.
# - Run: python bot.py (listens on PORT=8443 by default; override with env var).

import logging
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
NAME, AGE, GENDER, BIO, PREFERENCE, LOCATION = range(6)

# Simple in-memory storage for users and chats (use a DB like SQLite/Redis in production)
users = {}  # {user_id: {"name": ..., "age": ..., ...}}
active_chats = {}  # {user_id: matched_user_id}


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the profile registration flow."""
    await update.message.reply_text(
        "💖 Let’s build your profile!\n\nWhat’s your *name*, cutie? 😍"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect and store name."""
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Nice name 😏 How old are you?")
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect and store age with validation."""
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("😅 That doesn’t look like a valid age. Try again?")
        return AGE
    context.user_data["age"] = int(text)
    await update.message.reply_text("Got it! 🧠 What’s your gender? (Male/Female/Other)")
    return GENDER


async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect and store gender."""
    gender = update.message.text.strip().title()
    if gender not in ["Male", "Female", "Other"]:
        await update.message.reply_text("😏 Keep it simple: Male, Female, or Other? (Case doesn't matter!)")
        return GENDER
    context.user_data["gender"] = gender
    await update.message.reply_text("Perfect! 📝 Tell me about yourself (bio)?")
    return BIO


async def get_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect and store bio."""
    context.user_data["bio"] = update.message.text.strip()
    await update.message.reply_text("Sounds intriguing! ❤️ What are you looking for (preferences)?")
    return PREFERENCE


async def get_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect and store preference."""
    context.user_data["preference"] = update.message.text.strip()
    await update.message.reply_text("Got your vibe! 🌍 Where are you located?")
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect location and finalize profile."""
    context.user_data["location"] = update.message.text.strip()

    # Save full profile
    user_id = update.effective_user.id
    users[user_id] = context.user_data.copy()

    # Show potential matches (simple demo: assume other users exist)
    matches = find_matches(user_id)
    if matches:
        keyboard = [[InlineKeyboardButton(
            f"Chat with {users[match]['name']}", callback_data=f"chat_with_{match}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Profile saved, {context.user_data['name']}! 🎉 Found some matches:\n\n{matches_text(matches)}",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(f"Profile saved, {context.user_data['name']}! No matches yet—spread the word! 😘")

    # Clear user data and end conversation
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the registration."""
    await update.message.reply_text("No worries, cutie! Start over with /start anytime. 💋")
    context.user_data.clear()
    return ConversationHandler.END


def get_profile_conversation_handler():
    """Return the ConversationHandler for registration."""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_registration)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bio)],
            PREFERENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_preference)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


def find_matches(user_id):
    """Simple matchmaking: find users with compatible gender/preference (demo logic)."""
    user = users.get(user_id)
    if not user:
        return []
    matches = []
    for uid, profile in users.items():
        if uid != user_id and profile["gender"] in user["preference"] and user["gender"] in profile["preference"]:
            matches.append(uid)
    return matches[:3]  # Top 3 matches


def matches_text(matches):
    """Format matches for display."""
    text = ""
    for uid in matches:
        profile = users[uid]
        text += f"• {profile['name']}, {profile['age']}, {profile['location']}\n"
    return text


async def chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'chat_with_' callback to start a chat."""
    query = update.callback_query
    await query.answer()

    try:
        match_id = int(query.data.split("_")[-1])
    except (ValueError, IndexError):
        await query.answer("Invalid match selection. Try again!")
        return

    user_id = query.from_user.id

    # Pair them (avoid re-pairing if already matched)
    if active_chats.get(user_id) != match_id:
        active_chats[user_id] = match_id
        active_chats[match_id] = user_id

    await query.edit_message_text(
        f"🔥 Starting anonymous chat with {users.get(match_id, {}).get('name', 'a match')}! Say hi. (Use /reveal to unmask, /end to stop)"
    )
    await context.bot.send_message(match_id, f"💕 Someone wants to chat! Reply away. (/reveal or /end)")


async def handle_chat_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ongoing chat messages (routes to match)."""
    user_id = update.effective_user.id
    match_id = active_chats.get(user_id)

    if not match_id or match_id not in active_chats:
        await update.message.reply_text("👋 Not in an active chat? Use /start to begin!")
        return

    # Forward message to match (anonymously) - no extra reply to avoid duplication
    await context.bot.send_message(
        match_id,
        f"😏 *Anonymous Crush:* {update.message.text}\n\n(Reply here! /reveal or /end)"
    )
    # Removed "Message sent!" reply to prevent duplication with user's own message


async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """End the current chat."""
    user_id = update.effective_user.id
    match_id = active_chats.pop(user_id, None)
    if match_id:
        active_chats.pop(match_id, None)  # Unpair both
        await update.message.reply_text("Chat ended. Till next time! 👋 Find new matches after /start.")
        if match_id in users:  # Ensure match exists
            await context.bot.send_message(match_id, "Your chat partner said goodbye. 💔 New matches await!")
    else:
        await update.message.reply_text("No active chat to end.")


async def reveal_identity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reveal identities in active chat."""
    user_id = update.effective_user.id
    match_id = active_chats.get(user_id)

    if not match_id:
        await update.message.reply_text("No one to reveal to yet! Start a chat first.")
        return

    user_profile = users.get(
        user_id, {"name": "Mystery Person", "age": "?", "location": "?", "bio": "..."})
    match_profile = users.get(
        match_id, {"name": "Mystery Person", "age": "?", "location": "?", "bio": "..."})

    reveal_msg = f"🎭 Reveal! I'm {user_profile['name']}, {user_profile['age']}, from {user_profile['location']}. Bio: {user_profile['bio']}"
    await update.message.reply_text(reveal_msg)

    await context.bot.send_message(
        match_id,
        f"🎭 Your crush revealed: {reveal_msg}\n\nContinue chatting or /end?"
    )


def main():
    """Run the bot with webhooks."""
    # Replace with your bot token (use env var in production: os.getenv('BOT_TOKEN'))
    TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN env var missing! Set it in Render dashboard.")
        sys.exit(1)

    # Webhook config (customize for your deployment)
    # e.g., https://yourapp.onrender.com/bot (includes /bot)
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yourdomain.com/bot")
    PORT = int(os.getenv("PORT", 10000))  # Render defaults to 10000
    # Path to SSL cert (optional for local)
    CERT_FILE = os.getenv("CERT_FILE")
    KEY_FILE = os.getenv("KEY_FILE")     # Path to SSL key (optional for local)

    app = Application.builder().token(TOKEN).build()

    logger.info("Bot initialized. Waiting for webhook events...")

    # Add handlers
    app.add_handler(get_profile_conversation_handler())
    app.add_handler(CallbackQueryHandler(chat_callback, pattern="^chat_with_"))
    app.add_handler(CommandHandler("end", end_chat))
    app.add_handler(CommandHandler("reveal", reveal_identity))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_chat_messages))

    logger.info(f"Bot starting with webhooks on port {PORT} at {WEBHOOK_URL}")
    print(
        f"Set webhook: curl -F \"url={WEBHOOK_URL}\" https://api.telegram.org/bot{TOKEN}/setWebhook")

    try:
        if CERT_FILE and KEY_FILE:
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path="bot",  # No leading slash
                webhook_url=WEBHOOK_URL,  # Full URL including /bot path
                certificate_file=CERT_FILE,
                key_file=KEY_FILE
            )
        else:
            # For platforms with built-in SSL (e.g., Render), use drop_pending_updates=True
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path="bot",  # No leading slash
                webhook_url=WEBHOOK_URL,  # Full URL including /bot path
                drop_pending_updates=True  # Ignore old updates on startup
            )
    except Exception as e:
        logger.error(f"Webhook startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
