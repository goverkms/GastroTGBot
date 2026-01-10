import logging
import os
import html
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Silence noisy httpx logs (only show warnings and errors)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Constants
WEBAPP_URL = "https://gastroshopbali.netlify.app/"
TARGET_CHAT_ID = '-1003698856504'


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and help debug the issue."""
    logger.error(f"Exception while handling an update: {context.error}")


async def send_webapp_button(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the WebApp button to start ordering."""
    web_app = WebAppInfo(url=WEBAPP_URL)
    keyboard = [[InlineKeyboardButton(text="Gastroshop_bali", web_app=web_app)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="Нажмите кнопку ниже, чтобы начать заказ:",
        reply_markup=reply_markup
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message with a button to share contact."""
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
        f"👤 <b>New User Contact</b>\n"
        f"<b>Name:</b> {html.escape(user.first_name)} {html.escape(user.last_name or '')}\n"
        f"<b>Username:</b> @{html.escape(user.username or 'N/A')}\n"
        f"<b>ID:</b> {user.id}\n"
        f"<b>Phone:</b> {html.escape(phone_number)}"
    )
    
    logger.info(f"Received phone number: {phone_number}")
    
    # Send info to specific channel
    try:
        logger.info(f"Attempting to send user info to channel: {TARGET_CHAT_ID}")
        logger.info(f"Message content:\n{user_info}")
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=user_info,
            parse_mode='HTML',
            connect_timeout=60.0,
            read_timeout=60.0
        )
        logger.info("Successfully sent user info to channel")
    except Exception as e:
        logger.error(f"Failed to send to channel: {e}")
    
    # Send confirmation and remove keyboard
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Спасибо! Получен номер телефона: {phone_number}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Send WebApp button
    await send_webapp_button(update.effective_chat.id, context)


async def skip_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles when user sends any text instead of sharing phone."""
    user = update.effective_user
    
    # Info to send to the channel (without phone)
    user_info = (
        f"👤 <b>User Skipped Phone</b>\n"
        f"<b>Name:</b> {html.escape(user.first_name)} {html.escape(user.last_name or '')}\n"
        f"<b>Username:</b> @{html.escape(user.username or 'N/A')}\n"
        f"<b>ID:</b> {user.id}\n"
        f"<b>Phone:</b> Not shared"
    )
    
    logger.info(f"User skipped phone sharing: {user.first_name} (@{user.username or 'N/A'})")
    
    # Send info to channel
    try:
        logger.info(f"Attempting to send user info to channel: {TARGET_CHAT_ID}")
        logger.info(f"Message content (skipped phone):\n{user_info}")
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=user_info,
            parse_mode='HTML',
            connect_timeout=60.0,
            read_timeout=60.0
        )
    except Exception as e:
        logger.error(f"Failed to send to channel: {e}")
    
    # Remove the phone keyboard
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Хорошо! Вы можете начать заказ без номера телефона, но после оформления заказа обязательно свяжитесь с нами @gastroshop_bali",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Send WebApp button
    await send_webapp_button(update.effective_chat.id, context)


if __name__ == '__main__':
    
    # Get token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        exit(1)
    
    # Build application with timeouts for Railway
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
    
    # Add handlers
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, skip_phone_handler))
    
    # Start polling
    logger.info("Bot starting...")
    application.run_polling()
