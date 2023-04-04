import os
import sqlite3
import logging
from pathlib import Path
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from telegram.constants import ChatAction

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the database
DB_NAME = 'downloads.db'
DOWNLOADS_TABLE = '''CREATE TABLE IF NOT EXISTS download_videos (
                        id INTEGER PRIMARY KEY,
                        file_id TEXT UNIQUE,
                        channel_name TEXT,
                        download_date TEXT
                    );'''

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute(DOWNLOADS_TABLE)
conn.commit()

# Set up the file download directory
DOWNLOAD_DIR = '/media/veracrypt1'
Path(DOWNLOAD_DIR).mkdir(exist_ok=True)

# Define the start command handler


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Hello! Please send me the name of the channel you want me to download videos from.')

# Define the channel name handler


def channel_name(update, context):
    channel_name = update.message.text.strip()
    context.user_data['channel_name'] = channel_name

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Thank you! I will now start downloading videos from {channel_name}.')

    # Start downloading videos from the channel
    download_videos(context, update.effective_chat.id)

# Define the video download function


def download_videos(context, chat_id):
    channel_name = context.user_data['channel_name']
    bot = context.bot

    bot.send_message(chat_id=chat_id,
                     text=f'Downloading videos from {channel_name}...')

    # Set the chat action to "typing" while downloading
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Get the channel's message history
    channel = bot.get_chat(chat_id=channel_name)
    messages = bot.get_chat_history(chat_id=channel_name, limit=100)

    # Download videos from the messages
    for message in messages:
        if message.video and message.video.duration > 120:
            file_id = message.video.file_id

            # Check if the video has already been downloaded
            c.execute("SELECT * FROM download_videos WHERE file_id=?", (file_id,))
            row = c.fetchone()
            if row is None:
                # Download the video file
                file_name = f'{channel_name}_{file_id}.mp4'
                file_path = os.path.join(DOWNLOAD_DIR, file_name)
                bot.send_message(chat_id=chat_id,
                                 text=f'Downloading {file_name}...')
                bot.get_file(file_id).download(custom_path=file_path)

                # Record the download in the database
                c.execute("INSERT INTO download_videos (file_id, channel_name, download_date) VALUES (?, ?, datetime('now'))",
                          (file_id, channel_name))
                conn.commit()

    # Send a message when the download is complete
    bot.send_message(chat_id=chat_id, text='Download complete!')

# Define the main function


def main():
    # Get the Telegram bot token
    token = os.environ.get('TELEGRAM_BOT_TOKEN')

    # Create the updater and dispatcher
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Set up the command handlers
    start_handler = CommandHandler('start', start)
    channel_name_handler = Message

    #Run application until Cntl-C
    application.run_polling()
