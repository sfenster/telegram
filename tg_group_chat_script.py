import os
import logging
import sqlite3
import telegram
from telegram.ext import Updater, MessageHandler, Filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Set up Telegram bot
TOKEN = '6183384920:AAHFAhHA89iRuY2415hHekpDU3WV2QCWeJk'
bot = telegram.Bot(token=TOKEN)

# Set up Telegram updater and dispatcher
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Set up database connection
conn = sqlite3.connect('downloads.db')
c = conn.cursor()

# Set the video duration threshold (in seconds)
VIDEO_DURATION_THRESHOLD = 60

# Set the path for downloaded videos
DOWNLOADS_PATH = '/path/to/downloads/folder'

# Create the downloads table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS downloads
             (channel_name text, file_id text)''')
conn.commit()


def check_download_status(channel_name, file_id):
    # Check if the video has already been downloaded
    c.execute("SELECT * FROM downloads WHERE channel_name=? AND file_id=?",
              (channel_name, file_id))
    if c.fetchone() is not None:
        logging.info('Video already downloaded: %s, %s', channel_name, file_id)
        return True
    return False


def save_download_status(channel_name, file_id):
    # Save the download status of the video
    c.execute("INSERT INTO downloads VALUES (?, ?)", (channel_name, file_id))
    conn.commit()
    logging.info('Video download status saved: %s, %s', channel_name, file_id)


def download_video(update, context, channel_name, file_id):
    # Get the video file object
    video = context.bot.get_file(file_id)
    # Construct the path for the downloaded video
    download_path = os.path.join(DOWNLOADS_PATH, channel_name)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    download_path = os.path.join(download_path, f'{file_id}.mp4')
    # Download the video
    video.download(custom_path=download_path)
    logging.info('Video downloaded: %s, %s', channel_name, file_id)
    # Save the download status
    save_download_status(channel_name, file_id)


def callback(update, context):
    # Check if the message is a video and has a duration greater than the specified length
    if update.message.video and update.message.video.duration > VIDEO_DURATION_THRESHOLD:
        # Get the name of the group from which the video was sent
        group_name = update.message.chat.title
        # Get the file ID of the video
        file_id = update.message.video.file_id
        # Check if the video has already been downloaded
        if check_download_status(group_name, file_id):
            return
        # Download the video
        download_video(update, context, group_name, file_id)


def get_messages():
    # Fetch all messages in a group chat
    group_handler = MessageHandler(Filters.chat_type.groups, callback)
    updater.dispatcher.add_handler(group_handler)


if __name__ == '__main__':
    # Start getting messages from Telegram group chat
    get_messages()
    updater.start_polling()
    updater.idle()
