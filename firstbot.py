import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

# Set up the logging module, for formatted console output based on events
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
token = os.environ.get('TELEGRAM_BOT_TOKEN')

# Individual functions are created to handle different types of messaging
# 'Update' = all the information coming from Telegram
# 'Context' = information abou the status of the python-telegram-bot library

# Sample function that reacts to the /start command with a message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

# Sample function that echoes back any message
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# Sample function that converts arguments after a /caps command to all-caps 
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

if __name__ == '__main__':
    # Start assembling an application, passing the token from BotFather
    application = ApplicationBuilder().token(token).build()
    
    # Define handlers
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)
    
    # Add each handler to the application (add order determines handling order)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)   
    application.add_handler(caps_handler)

    # Run the application until Cntl-C is pressed
    application.run_polling()
