import os

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from dotenv import load_dotenv

from utils import kzt_course, usd_course

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('TOKEN')

# State definitions conversation
SELECTING_ACTION, TYPING, STOPPING, START_OVER = map(chr, range(4))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END
(
    COURSE,
    CURRENCY,
    KZT,
    USD,
) = map(chr, range(4, 8))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action"""
    text = (
        "Добро пожаловать! Пожалуйста, выберите вариант из меню:"
    )
    buttons = [
        [
            InlineKeyboardButton(text="Казахстанский тенге", callback_data=str(KZT)),
        ],
        [
            InlineKeyboardButton(text="USD", callback_data=str(USD)),
        ],
        [
            InlineKeyboardButton(text="Done", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, reply_markup=keyboard)
    return SELECTING_ACTION


def pretty_print(amount, course, currency) -> str:
    """Print course"""
    return_str = ''
    return_str += f"{amount} {currency} = {round(amount * course, 2)} RUB"
    return_str += f"\n\n{amount} RUB = {round((amount / course), 2)} {currency}"
    return return_str


async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Print course and ask user for input convertible amount."""
    user_data = context.user_data
    user_input = update.callback_query.data
    text = ''
    course = 1
    if user_input == KZT:
        currency = 'KZT'
        course = kzt_course()
        user_data[CURRENCY] = 'KZT'
        text += pretty_print(1, course, currency)
    if user_input == USD:
        currency = 'USD'
        course = usd_course()
        user_data[CURRENCY] = 'USD'
        text += pretty_print(1, course, currency)
    user_data[COURSE] = course
    text += f"\n\nВведите сумму:"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return TYPING


async def convertible_sum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Print convertible amount."""
    user_data = context.user_data
    user_input = update.message.text
    course = user_data[COURSE]
    currency = user_data[CURRENCY]
    text = pretty_print(float(user_input), course, currency)
    await update.message.reply_text(text=text)
    return TYPING


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    await update.callback_query.answer()
    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)
    return END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye!")
    return END


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    selection_handlers = [
        CallbackQueryHandler(ask_for_input, pattern="^(?!" + str(END) + ").*$"),
        CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: selection_handlers,
            STOPPING: [CommandHandler("start", start)],
            TYPING:   [
                MessageHandler(filters.TEXT & ~filters.COMMAND, convertible_sum)]
        },
        fallbacks=[CommandHandler("stop", stop)],
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
