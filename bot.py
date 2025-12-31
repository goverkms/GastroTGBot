import logging
import os
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and help debug the issue."""
    logging.error(f"Exception while handling an update: {context.error}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message with a button to share contact."""
    contact_keyboard = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    custom_keyboard = [[contact_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    welcome_text = (
        "✨ Добро пожаловать в\n"
        "@gastroshop_bali\n\n"
        "Этот бот поможет вам оформить заказ в несколько кликов.\n\n"
        "Пожалуйста, нажмите кнопку «Отправить номер телефона» внизу экрана 👇\n \n"
        "Затем нажмите кнопку «Gastroshop_bali», чтобы начать заказ.\n\n"
        "Приятных покупок и отличного вкуса 🍴"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=welcome_text, 
        reply_markup=reply_markup
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the received contact."""
    contact = update.effective_message.contact
    user = update.effective_user
    phone_number = contact.phone_number
    
    # Info to send to the channel
    user_info = (
        f"👤 **New User Contact**\n"
        f"**Name:** {user.first_name} {user.last_name or ''}\n"
        f"**Username:** @{user.username or 'N/A'}\n"
        f"**ID:** {user.id}\n"
        f"**Phone:** {phone_number}"
    )
    
    print(f"Received phone number: {phone_number}")
    
    # Send info to specific channel/user
    TARGET_CHAT_ID = '-1003698856504'
    try:
        logging.info(f"Attempting to send user info to channel: {TARGET_CHAT_ID}")
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=user_info,
            parse_mode='Markdown',
            connect_timeout=60.0,
            read_timeout=60.0
        )
        logging.info("Successfully sent user info to channel")
    except Exception as e:
        logging.error(f"Failed to send to channel: {e}")
    
    # First remove the keyboard (hide "Share Contact")
    # We send a temporary loading message to remove the keyboard, then delete it or just leave it.
    # Actually, simplest UI flow:
    # 1. Send "Thank you" and remove keyboard.
    # 2. Send the "Menu" button immediately after.
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Спасибо! Получен номер телефона: {phone_number}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Create WebApp button
    web_app = WebAppInfo(url="https://gastroshopbali.netlify.app/")
    keyboard = [[InlineKeyboardButton(text="Gastroshop_bali", web_app=web_app)]]
    reply_markup_inline = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Нажмите кнопку ниже, чтобы начать заказ:",
        reply_markup=reply_markup_inline
    )

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()
    
    # Get token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        exit(1)
    
    # Increase timeout to handle network issues on Railway
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(60.0)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .pool_timeout(60.0)
        .get_updates_connect_timeout(60.0)
        .get_updates_read_timeout(65.0)
        .build()
    )
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    start_handler = CommandHandler('start', start)
    contact_msg_handler = MessageHandler(filters.CONTACT, contact_handler)
    
    application.add_handler(start_handler)
    application.add_handler(contact_msg_handler)
    
    # Bot is polling (quietly)
    application.run_polling()
