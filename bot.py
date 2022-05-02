"""
script for telegram bot and its functions
"""
__author__ = "Florian Kellermann, Linus Eickhoff, Florian Kaiser"
__date__ = "02.05.2022"
__version__ = "0.0.1" 
__license__ = "None"

# main bot at http://t.me/guess_the_price_bot
# debug bot at http://t.me/amazondebug_bot

from dotenv import load_dotenv
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import os
import sys

load_dotenv(dotenv_path='.env') # load environment variables

bot_version = "0.0.1" # version of bot

bot = telebot.TeleBot(os.getenv('BOT_API_KEY'))

@bot.message_handler(commands=['start', 'Start']) 
def send_start(message):
    
    """ Sending welcome message to new user
    :type message: message object bot
    :param message: message that was reacted to, in this case always containing '/start'

    :raises: none

    :rtype: none
    """
    bot.reply_to(message, "Welcome to this amazon bot")

def main_loop():
    
    """ Start bot
    :raises: none

    :rtype: none
    """
    bot.infinity_polling()

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)