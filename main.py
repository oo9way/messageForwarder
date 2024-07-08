import logging
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_CHAT_ID = os.getenv('TARGET_CHAT_ID')
WORD_LIST = os.getenv('WORD_LIST').split(',')

bot = Bot(token=BOT_TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

dispatcher = Dispatcher(bot, None, workers=0)


def contains_word(message_text):
    for word in message_text:
        if word in WORD_LIST:
            return True
    return False


def forward_message(update: Update, context: CallbackContext) -> None:
    chat_type = update.effective_chat.type
    group_name = update.effective_chat.title
    user = update.message.from_user
    user_name = f"{user.first_name} {user.last_name}  @{user.username}"
    message_text = update.message.text

    if chat_type in ['group', 'supergroup', 'channel'] and contains_word(message_text.split()):
        user_id = user.id
        profile_link = f'<a href="tg://user?id={user_id}">{user_id}</a>'

        formatted_message = (
            f"Guruh nomi: {group_name}\n"
            f"Mijoz: {user_name}\n"
            f"Xabar: {message_text}\n"
            f"Kontakt: {profile_link}"
        )

        bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=formatted_message,
            parse_mode=ParseMode.HTML
        )


message_handler = MessageHandler(Filters.text & ~Filters.command, forward_message)
dispatcher.add_handler(message_handler)


@app.route('/webhook', methods=['POST'])
def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram Bot with Webhook')
    parser.add_argument('--webhook', type=str, help='Webhook URL')
    parser.add_argument('--port', type=int, default=4500, help='Port number (default: 4500)')
    args = parser.parse_args()

    if args.webhook:
        bot.set_webhook(url=args.webhook)
        print(f"Webhook set to: {args.webhook}")

    # Run Flask app
    app.run(port=args.port)