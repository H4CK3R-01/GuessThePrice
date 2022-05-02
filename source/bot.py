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
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
import logging
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
    bot.reply_to(message, "Welcome to this amazon prices guesser bot")
    
telebot.logger.setLevel(logging.DEBUG)
    
@bot.inline_handler(lambda query: query.query == 'text') # inline prints for debugging
def query_text(inline_query):
    
    """ Output in the console about current user actions and status of bot
    :type inline_query: 
    :param inline_query:

    :raises: none

    :rtype: none
    """
    try:
        r = types.InlineQueryResultArticle('1', 'Result1', types.InputTextMessageContent('hi'))
        r2 = types.InlineQueryResultArticle('2', 'Result2', types.InputTextMessageContent('hi'))
        bot.answer_inline_query(inline_query.id, [r, r2])
    except Exception as e:
        print(e)

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